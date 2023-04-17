from django.urls import path
from django.views.generic import TemplateView
from django.contrib import admin

from createfields import views

urlpatterns = [
   path('', views.index, name='index'),
   path('admin/', admin.site.urls),
   path('oauth_response/', views.oauth_response, name='oauth_response'),
   path('create_fields/<str:job_id>/', views.create_fields, name='create_fields'),
   path('logout/', views.logout, name='logout'),
   path('loading/<str:job_id>/', views.loading, name='loading'),
   path('job_status/<str:job_id>/', views.job_status, name='job_status'),
   path('get_layouts/<str:job_id>/<str:object_name>/', views.get_layouts, name='get_layouts'),
   path('get_profiles/<str:job_id>/', views.get_profiles, name='get_profiles'),
   path('deploy_field/<str:job_id>/<str:object_name>/', views.deploy_field, name='deploy_field'),
   path('deploy_profiles/<str:job_id>/<str:object_name>/', views.deploy_profiles, name='deploy_profiles'),
   path('auth_details/', views.auth_details, name='auth_details'),
]
