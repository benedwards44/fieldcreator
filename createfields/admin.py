from django.contrib import admin
from createfields.models import Job, CustomObject, PageLayout, Profile, ErrorLog

"""
	INLINES/RELATED LISTS 
"""
class CustomObjectInline(admin.TabularInline):
	fields = ['name','label']
	ordering = ['name']
	model = CustomObject
	extra = 0

class PageLayoutInline(admin.TabularInline):
	fields = ['salesforce_id','name']
	ordering = ['name']
	model = PageLayout
	extra = 0

class ProfileInline(admin.TabularInline):
	fields = ['salesforce_id','name']
	ordering = ['name']
	model = Profile
	extra = 0


"""
	ADMIN CLASSES
"""
class JobAdmin(admin.ModelAdmin):
    list_display = ('created_date','finished_date','status','error')
    ordering = ['-created_date']
    inlines = [CustomObjectInline, PageLayoutInline, ProfileInline]

class ErrorLogAdmin(admin.ModelAdmin):
	list_display = ('created_date','name','error')
	ordering = ['-created_date']

admin.site.register(Job, JobAdmin)
admin.site.register(ErrorLog, ErrorLogAdmin)
