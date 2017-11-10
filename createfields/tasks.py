from __future__ import absolute_import
from celery import Celery
from django.conf import settings
from zipfile import ZipFile
from suds.client import Client
from base64 import b64encode, b64decode
import requests
import os
import datetime
import sys
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fieldcreator.settings')

app = Celery('tasks', broker=os.environ.get('REDISTOGO_URL', 'redis://localhost'))

from createfields.models import Job, CustomObject, PageLayout, Profile, ErrorLog
from createfields.utils import create_error_log, chunks

@app.task
def get_metadata(job): 
	"""
		Async task to download list of objects and profiles
	"""
	
	job.status = 'Downloading Metadata'
	job.save()

	try:

		# The list of standard objects that support custom fields
		# https://www.salesforce.com/us/developer/docs/object_reference/Content/sforce_api_objects_custom_objects.htm
		supported_standard_objects = (
			'Account',
			'Asset',
			'Campaign',
			'CampaignMember',
			'Case',
			'Contact',
			'Contract',
			'Event',
			'Lead',
			'Opportunity',
			'OpportunityCompetitor',
			'OpportunityLineItem',
			'Order',
			'OrderItem',
			'Pricebook2',
			'PricebookEntry',
			'Product2',
			'Quote',
			'QuoteLineItem',
			'Task',
			'User',
			'WorkOrder',
			'WorkOrderLineItem',
		)

		request_url = job.instance_url + '/services/data/v' + str(settings.SALESFORCE_API_VERSION) + '.0/'
		headers = { 
			'Accept': 'application/json',
			'X-PrettyPrint': 1,
			'Authorization': 'Bearer ' + job.access_token
		}

		# Query for all objects
		for record in requests.get(request_url + 'sobjects', headers = headers).json()['sobjects']:

			if record['custom'] or record['name'] in supported_standard_objects:

				custom_object = CustomObject()
				custom_object.job = job
				custom_object.label = record['label']
				custom_object.name = record['name']
				custom_object.save()


		# Query for profiles in Org
		# NOTE: Hardcoding 34.0 here as 35.0+ didn't support querying for FullName field in the query, but 34.0 did. Go figure!
		profile_query = requests.get(job.instance_url + '/services/data/v34.0/tooling/query/?q=Select+Id,Name,FullName+From+Profile', headers = headers).json()

		# If profiles are found, save thema gainst the job
		if 'records' in profile_query:

			# Query for all profiles
			for record in profile_query['records']:

				profile = Profile()
				profile.job = job
				profile.salesforce_id = record['Id']
				profile.name = record['Name']
				profile.fullName = record['FullName']
				profile.save()

		# Update Job status to finished
		job.status = 'Finished'

	except Exception as error:
		
		job.status = 'Error'
		job.error = traceback.format_exc()

	job.finished_date = datetime.datetime.now()
	job.save()



@app.task
def deploy_profiles_async(job, object_name, all_fields):
	"""
		Async task to deploy profiles. This takes longer so is done silently
	"""

	# Deploy layouts - Have to use the Metadata SOAP API because the Tooling REST API wouldn't bloody work!

	#create_error_log('Reach tasks', '')

	try:

		# work with profiles
		metadata_client = Client('http://fieldcreator.herokuapp.com/static/metadata-' + str(settings.SALESFORCE_API_VERSION) + '.xml')
		metadata_url = job.instance_url + '/services/Soap/m/' + str(settings.SALESFORCE_API_VERSION) + '.0/' + job.org_id
		session_header = metadata_client.factory.create("SessionHeader")
		session_header.sessionId = job.access_token
		metadata_client.set_options(location=metadata_url, soapheaders=session_header)

		#create_error_log('Profile Debug', 'instance_url: ' + job.instance_url + '\n\naccess_token: ' + job.access_token)

		# Dictory of profiles to deploy
		profile_dict = {}

		# Iterate over fields to build profile deployment
		for field in all_fields:

			# Iterate over profiles within field
			for profile in field['profiles']:

				# Only add if at least read is given
				if profile['read']:

					field_permission = metadata_client.factory.create('ProfileFieldLevelSecurity')
					field_permission.field = object_name + '.' + field['name']
					field_permission.editable = profile['edit']
					field_permission.readable = profile['read']

					# If key exists in dict - append new permission. Otherwise start new list and add permission
					profile_dict.setdefault(profile['fullName'], []).append(field_permission)

		# Profile list to delpoy
		profile_deploy_list = []

		# If we have some profiles to deploy
		if profile_dict:

			# Iterate over dict
			for profile_name in profile_dict:

				# Create profile Metadata
				new_profile = metadata_client.factory.create("Profile")
				new_profile.fullName = profile_name

				# Get field permissions from dict
				new_profile.fieldPermissions = profile_dict[profile_name]

				# List of profiles to deploy
				profile_deploy_list.append(new_profile)


		# If profiles to deploy
		if profile_deploy_list:

			try:

				# Only allowed to deploy 10 at a time. Split deploy list into chunks
				for profiles_to_deploy in chunks(profile_deploy_list, 10):

					result = metadata_client.service.updateMetadata(profiles_to_deploy)

					# Print result
					create_error_log('Deploy Profiles Result', str(result))

					# Capture error if exists
					if not result[0].success:

						create_error_log('Deploy Profiles Error', str(result))

			except Exception as ex:

				create_error_log('Deploy Profiles Error', str(traceback.format_exc()))

	except Exception as ex:

		create_error_log('Deploy Profiles Error', str(traceback.format_exc()))

