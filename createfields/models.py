from django.db import models

class Job(models.Model):
	random_id = models.CharField(db_index=True, max_length=255, blank=True, null=True)
	created_date = models.DateTimeField(null=True, blank=True)
	finished_date = models.DateTimeField(null=True, blank=True)
	org_id = models.CharField(max_length=255)
	org_name = models.CharField(max_length=255, blank=True, null=True)
	email = models.CharField(max_length=255, blank=True, null=True)
	username = models.CharField(max_length=255, blank=True, null=True)
	access_token = models.CharField(max_length=255, blank=True, null=True)
	instance_url = models.CharField(max_length=255, blank=True, null=True)
	json_message = models.TextField(blank=True, null=True)
	status = models.CharField(max_length=255, blank=True, null=True)
	error = models.TextField(blank=True, null=True)

	def sorted_objects(self):
		return self.customobject_set.order_by('name')

	def sorted_profiles(self):
		return self.profile_set.order_by('name')

	def __str__(self):
		return '%s' % (self.random_id)

class CustomObject(models.Model):
	job = models.ForeignKey(Job)
	label = models.CharField(max_length=255, blank=True, null=True)
	name = models.CharField(max_length=255, blank=True, null=True)

	def __str__(self):
		return '%s (%s)' % (self.name, self.label)

	def page_layouts(self):
		return self.pagelayout_set.all().order_by('name')

class PageLayout(models.Model):
	job = models.ForeignKey(Job)
	salesforce_object = models.ForeignKey(CustomObject)
	salesforce_id = models.CharField(max_length=255, blank=True, null=True)
	name = models.CharField(max_length=255, blank=True, null=True)

	def __str__(self):
		return '%s' % (self.name)

class Profile(models.Model):
	job = models.ForeignKey(Job)
	salesforce_id = models.CharField(max_length=255, blank=True, null=True)
	name = models.CharField(max_length=255, blank=True, null=True)
	fullName = models.CharField(max_length=255, blank=True, null=True)

	def __str__(self):
		return '%s' % (self.name)

class ErrorLog(models.Model):
	created_date = models.DateTimeField(blank=True,null=True)
	name = models.CharField(max_length=255, blank=True, null=True)
	error = models.TextField(blank=True, null=True)

	def __str__(self):
		return '%s' % (self.name)
