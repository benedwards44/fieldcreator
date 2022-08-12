from django.conf.urls import url, include
from django.views.generic import TemplateView, RedirectView
from django.contrib import admin

from createfields import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index, name='index'),
    url(r'^oauth_response/$', views.oauth_response, name='oauth_response'),
    url(r'^create_fields/(?P<job_id>[0-9A-Za-z_\-]+)/$', views.create_fields, name='create_fields'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^loading/(?P<job_id>[0-9A-Za-z_\-]+)/$', views.loading, name='loading'),
    url(r'^job_status/(?P<job_id>[0-9A-Za-z_\-]+)/$', views.job_status, name='job_status'),
    url(r'^get_layouts/(?P<job_id>[0-9A-Za-z_\-]+)/(?P<object_name>[0-9A-Za-z_\-]+)/$', views.get_layouts, name='get_layouts'),
    url(r'^get_profiles/(?P<job_id>[0-9A-Za-z_\-]+)/$', views.get_profiles, name='get_profiles'),
    url(r'^deploy_field/(?P<job_id>[0-9A-Za-z_\-]+)/(?P<object_name>[0-9A-Za-z_\-]+)/$', views.deploy_field, name='deploy_field'),
    url(r'^deploy_profiles/(?P<job_id>[0-9A-Za-z_\-]+)/(?P<object_name>[0-9A-Za-z_\-]+)/$', views.deploy_profiles, name='deploy_profiles'),
    url(r'^auth_details/$', views.auth_details, name='auth_details'),
]
