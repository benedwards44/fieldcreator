from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from createfields.models import Job, CustomObject, PageLayout, Profile, ErrorLog
from createfields.forms import LoginForm
from django.conf import settings
from createfields.tasks import get_metadata, deploy_profiles_async
from suds.client import Client
from createfields.utils import build_metadata_for_field, create_error_log
import uuid
import json	
import requests
import datetime
from time import sleep
import sys
import traceback

reload(sys)
sys.setdefaultencoding("utf-8")

def index(request):
	"""
		Controller for the index/landing page.
	"""
	
	if request.method == 'POST':

		login_form = LoginForm(request.POST)

		if login_form.is_valid():

			# Get Production or Sandbox value
			environment = login_form.cleaned_data['environment']

			# URL to send login request
			oauth_url = 'https://login.salesforce.com/services/oauth2/authorize'
			if environment == 'Sandbox':
				oauth_url = 'https://test.salesforce.com/services/oauth2/authorize'

			# Set up URL based on Salesforce Connected App details
			oauth_url = oauth_url + '?response_type=code&client_id=' + settings.SALESFORCE_CONSUMER_KEY + '&redirect_uri=' + settings.SALESFORCE_REDIRECT_URI + '&state='+ environment
			
			# Re-direct to login page
			return HttpResponseRedirect(oauth_url)
	else:
		login_form = LoginForm()

	return render(request, 'index.html', {'login_form': login_form })


def oauth_response(request):
	"""
		Controller for the oauth_response page.
	"""

	# Default variables
	error_exists = False
	error_message = ''
	username = ''
	org_name = ''
	org_id = ''
	email = ''

	# On page load
	if request.GET:

		# Get OAuth response  values
		oauth_code = request.GET.get('code')
		environment = request.GET.get('state')
		access_token = ''
		instance_url = ''

		if 'Sandbox' in environment:
			login_url = 'https://test.salesforce.com'
		else:
			login_url = 'https://login.salesforce.com'
		
		# Log in to REST API to obtain access token
		r = requests.post(login_url + '/services/oauth2/token', headers={ 'content-type':'application/x-www-form-urlencoded'}, data={'grant_type':'authorization_code','client_id': settings.SALESFORCE_CONSUMER_KEY,'client_secret':settings.SALESFORCE_CONSUMER_SECRET,'redirect_uri': settings.SALESFORCE_REDIRECT_URI,'code': oauth_code})
		
		# Load JSON response
		auth_response = json.loads(r.text)

		# If login error - return error for user
		if 'error_description' in auth_response:
			error_exists = True
			error_message = auth_response['error_description']

		# Otherwise get session details
		else:
			access_token = auth_response['access_token']
			instance_url = auth_response['instance_url']
			user_id = auth_response['id'][-18:]
			org_id = auth_response['id'][:-19]
			org_id = org_id[-18:]

			# get username of the authenticated user
			r = requests.get(instance_url + '/services/data/v' + str(settings.SALESFORCE_API_VERSION) + '.0/sobjects/User/' + user_id + '?fields=Username,Email', headers={'Authorization': 'OAuth ' + access_token})
			query_response = json.loads(r.text)

			if 'Username' in query_response:
				username = query_response['Username']

			if 'Email' in query_response:
				email = query_response['Email']

			# get the org name of the authenticated user
			r = requests.get(instance_url + '/services/data/v' + str(settings.SALESFORCE_API_VERSION) + '.0/sobjects/Organization/' + org_id + '?fields=Name', headers={'Authorization': 'OAuth ' + access_token})
			
			if 'Name' in json.loads(r.text):
				org_name = json.loads(r.text)['Name']

		login_form = LoginForm(initial={'environment': environment, 'access_token': access_token, 'instance_url': instance_url, 'org_id': org_id, 'username': username, 'org_name':org_name, 'email': email})	

	# Run after user selects logout or get schema
	if request.POST:

		login_form = LoginForm(request.POST)

		if login_form.is_valid():

			# Copy all variables from form
			environment = login_form.cleaned_data['environment']
			access_token = login_form.cleaned_data['access_token']
			instance_url = login_form.cleaned_data['instance_url']
			org_id = login_form.cleaned_data['org_id']
			username = login_form.cleaned_data['username']
			email = login_form.cleaned_data['email']
			org_name = login_form.cleaned_data['org_name']

			# Logout action
			if 'logout' in request.POST:

				r = requests.post(instance_url + '/services/oauth2/revoke', headers={'content-type':'application/x-www-form-urlencoded'}, data={'token': access_token})
				return HttpResponseRedirect('/logout?instance_prefix=' + instance_url.replace('https://','').replace('.salesforce.com',''))

			# Continue action. Start job to get metadata for the job
			if 'get_metadata' in request.POST:

				job = Job()
				job.random_id = uuid.uuid4()
				job.created_date = datetime.datetime.now()
				job.status = 'Not Started'
				job.username = username
				job.email = email
				job.environment = environment
				job.org_id = org_id
				job.org_name = org_name
				job.instance_url = instance_url
				job.access_token = access_token
				job.save()

				# Start downloading metadata using async task
				get_metadata.delay(job.id)

				# Return to loading page. This will cycle an AJAX request to check when job is finished
				return HttpResponseRedirect('/loading/' + str(job.random_id))

	return render(
        request, 
        'oauth_response.html', 
        {
            'error': error_exists, 
            'error_message': error_message, 
            'username': username, 
            'org_name': org_name, 
            'login_form': login_form
		}
	)
        

def logout(request):
	"""
		Controller for the logout page
	"""

	# Determine logout url based on environment
	instance_prefix = request.GET.get('instance_prefix')
		
	return render(request, 'logout.html', { 'instance_prefix': instance_prefix })


def create_fields(request, job_id):
	"""
		Controller for the create_fields page
	"""

	# Get the job object from URL
	job = get_object_or_404(Job, random_id = job_id)

	# If form is posted to refresh objects and profiles
	if request.POST:

		# Clear objects and profiles
		job.sorted_objects().delete()
		job.sorted_profiles().delete()

		# Start downloading metadata using async task
		get_metadata.delay(job.id)

		# Determine URL for redirection
		return_url = '/loading/' + str(job.random_id) + '/'

		# If no header is in URL, keep it there
		if 'noheader' in request.GET and request.GET.noheader == '1':
			return_url += '?noheader=1'

		# Return to loading page. This will cycle an AJAX request to check when job is finished
		return HttpResponseRedirect(return_url)

	# Else GET request, render page.
	else:

		return render(request, 'create_fields.html', { 'job': job })


def job_status(request, job_id):
	"""
		AJAX endpoint for page to constantly check if job is finished
	"""

	job = get_object_or_404(Job, random_id = job_id)

	# Return job status. Will be finished when all metadata is downloaded
	response_data = {
		'status': job.status,
		'error': job.error
	}

	return JsonResponse(response_data)


def loading(request, job_id):
	"""
		Controller for page for user to wait for job to run
	"""

	job = get_object_or_404(Job, random_id = job_id)

	if job.status == 'Finished':

		# Return URL when job is finished
		return_url = '/create_fields/' + str(job.random_id) + '/'

		# If no header is in URL, keep it there
		if 'noheader' in request.GET and request.GET.noheader == '1':
			return_url += '?noheader=1'

		return HttpResponseRedirect(return_url)

	else:
		
		return render(request, 'loading.html', { 'job': job })


def get_profiles(request, job_id):
	"""
		AJAX method to return a list of profiles to the page.
	"""
	# Query for records
	job = get_object_or_404(Job, random_id = job_id)

	# List of profiles for the page
	profile_list = []

	# Iterate over profiles for job
	for profile in job.sorted_profiles():

		# Append to list in JSON format
		profile_list.append({
			'id': profile.salesforce_id,
			'fullName': profile.fullName,
			'name': profile.name
		})

	# Return list to page
	return JsonResponse(profile_list, safe=False)


def get_layouts(request, job_id, object_name):
	"""
		AJAX endpoint to query for layouts for a specified object 
	"""

	# Query for records
	job = get_object_or_404(Job, random_id = job_id)
	custom_object = get_object_or_404(CustomObject, job = job.id, name = object_name)

	# Layout list to return to page
	layout_list = []

	# Layouts have already been queried, so return those
	if custom_object.page_layouts():

		for layout in custom_object.page_layouts():

			layout_list.append({'name': layout.name})

		return JsonResponse(layout_list, safe=False)

	# Otherwise we need to query for layouts
	else:

		# Tooling API settings
		request_url = job.instance_url + '/services/data/v' + str(settings.SALESFORCE_API_VERSION) + '.0/'

		# Set headers for callout
		headers = { 
			'Accept': 'application/json',
			'X-PrettyPrint': 1,
			'Authorization': 'Bearer ' + job.access_token
		}

		# Make callout
		request = requests.get(request_url + 'tooling/query/?q=Select+Id,Name+From+Layout+Where+TableEnumOrId=\'' + custom_object.name + '\'+Order+by+Name', headers = headers)

		# If successful
		if request.status_code == 200:

			# Iterate over layouts and create records
			for layout in request.json()['records']:
		
				# layout list to return to page
				layout_list.append({'name': layout['Name']})

				# Create layout record
				new_layout = PageLayout()
				new_layout.job = job
				new_layout.salesforce_object = custom_object
				new_layout.salesforce_id = layout['Id']
				new_layout.name = layout['Name']
				new_layout.save()

			# Return the layout list for the page
			return JsonResponse(layout_list, safe=False)

		# Error making REST call
		else:

			# Set response data for page
			response_data = {
				'errorCode': request.json()[0]['errorCode'],
				'message': request.json()[0]['message']
			}

			return JsonResponse(response_data)


def deploy_field(request, job_id, object_name):
	"""
		AJAX endpoint to deploy a field. Fields are deployed one-by-one
	"""

	job = get_object_or_404(Job, random_id=job_id)

	# If POST request made
	if request.method == 'POST':

		# Response array for the page
		page_response = {}

		# Parse POST data into array
		field_data = json.loads(request.body)	

		# Use Metadata API for Production deployment
		if job.environment == 'Production':

			# Instantiate the metadata API
			metadata_client = Client('http://fieldcreator.herokuapp.com/static/metadata-' + str(settings.SALESFORCE_API_VERSION) + '.xml')
			metadata_url = job.instance_url + '/services/Soap/m/' + str(settings.SALESFORCE_API_VERSION) + '.0/' + job.org_id
			session_header = metadata_client.factory.create("SessionHeader")
			session_header.sessionId = job.access_token
			metadata_client.set_options(location=metadata_url, soapheaders=session_header)

			# Build the field metadata
			field_metadata = build_metadata_for_field(field_data, metadata_client=metadata_client)
			field_metadata.fullName = object_name + '.' + field_data['name']

			# Deploy the field
			try:

				result = metadata_client.service.createMetadata([field_metadata])

				if result[0].success:

					page_response = {
						'success': True,
						'errorCode': None,
						'message': 'Successfully created field.'
					}

				else:

					page_response = {
						'success': False,
						'errorCode': result[0].errors[0].statusCode,
						'message': result[0].errors[0].message
					}

				# Return the POST response
				return JsonResponse(page_response)

			except Exception as ex:

				page_response = {
					'success': False,
					'errorCode': 'Error building field metadata',
					'message': ex
				}

				create_error_log('Data Payload Debug', traceback.format_exc())

				return JsonResponse(page_response)

		else:

			# URL to send deploying data
			request_url = job.instance_url + '/services/data/v' + str(settings.SALESFORCE_API_VERSION) + '.0/tooling/sobjects/CustomField/'
			
			# Set headers for POST request
			headers = { 
				'Accept': 'application/json',
				'X-PrettyPrint': 1,
				'Authorization': 'Bearer ' + job.access_token,
				'Content-Type': 'application/json'
			}

			try:

				# Set data (the field to deploy)
				data = {
					'Id': None,
					'FullName': object_name + '.' + field_data['name'],
					'Metadata': build_metadata_for_field(field_data)
				}

				create_error_log('Data Payload Debug', data)

			except Exception as ex:

				page_response = {
					'success': False,
					'errorCode': 'Error building field metadata',
					'message': ex
				}

				create_error_log('Data Payload Debug', traceback.format_exc())

				return JsonResponse(page_response)

			# Make RESTful POST
			try:

				r = requests.post(request_url, headers=headers, data=json.dumps(data))
				page_response = r.json()

			except Exception as ex:

				page_response = {
					'success': False,
					'errorCode': 'Error connecting to Tooling API',
					'message': ex
				}

				create_error_log('Deploy Field Error', traceback.format_exc())

			# Return the POST response
			return JsonResponse(page_response)

	# No POST method found - return error
	else:

		return JsonResponse({'error': 'No POST message.'})


def deploy_profiles(request, job_id, object_name):
	"""
		AJAX endpoint for deploying profiles. Called when fields are finished deploying.
	"""

	job = get_object_or_404(Job, random_id = job_id)

	# If POST request made
	if request.method == 'POST':

		# Parse POST data into array
		all_fields = json.loads(request.body)

		# If data exists, set job to deploy profiles
		if all_fields:

			try:

				deploy_profiles_async.delay(job, object_name, all_fields)

			except Exception as ex:

				page_response = {
					'success': False,
					'errorCode': 'Error creating task to deploy profiles',
					'message': ex
				}

				create_error_log('Delay Profile Deployment Error', traceback.format_exc())

		return JsonResponse({
			'success': True,
			'message': 'Successfully start profile job'
		})

		# No POST method found - return error
	else:

		return JsonResponse({'error': 'No POST message.'})

@csrf_exempt
def auth_details(request):
	"""
		RESTful endpoint to pass authentication details
	"""

	try:

		request_data = json.loads(request.body)

		# Check for all required fields
		if 'org_id' not in request_data or 'access_token' not in request_data or 'instance_url' not in request_data:

			response_data = {
				'status': 'Error',
				'success':  False,
				'error_text': 'Not all required fields were found in the message. Please ensure org_id, access_token and instance_url are all passed in the payload'
			}

		# All fields exist. Start job and send response
		else:

			# create the package record to store results
			job = Job()
			job.random_id = uuid.uuid4()
			job.created_date = datetime.datetime.now()
			job.status = 'Not Started'
			job.org_id = request_data['org_id']
			job.instance_url = request_data['instance_url']
			job.access_token = request_data['access_token']
			job.save()

			# Run job
			get_metadata.delay(job.id)

			# Build response 
			response_data = {
				'job_url': 'https://fieldcreator.herokuapp.com/loading/' + str(job.random_id) + '/?noheader=1',
				'status': 'Success',
				'success': True
			}

	except Exception as error:

		# If there is an error, raise exception and return
		response_data = {
			'status': 'Error',
			'success':  False,
			'error_text': str(error)
		}
	
	return JsonResponse(response_data)
