from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView, RedirectView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'createfields.views.index', name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^oauth_response/$', 'createfields.views.oauth_response', name='oauth_response'),
    url(r'^create_fields/(?P<job_id>[0-9A-Za-z_\-]+)/$', 'createfields.views.create_fields'),
    url(r'^logout/$', 'createfields.views.logout', name='logout'),
    url(r'^loading/(?P<job_id>[0-9A-Za-z_\-]+)/$', 'createfields.views.loading'),
    url(r'^job_status/(?P<job_id>[0-9A-Za-z_\-]+)/$', 'createfields.views.job_status'),
    url(r'^get_layouts/(?P<job_id>[0-9A-Za-z_\-]+)/(?P<object_name>[0-9A-Za-z_\-]+)/$', 'createfields.views.get_layouts'),
    url(r'^get_profiles/(?P<job_id>[0-9A-Za-z_\-]+)/$', 'createfields.views.get_profiles'),
    url(r'^deploy_field/(?P<job_id>[0-9A-Za-z_\-]+)/(?P<object_name>[0-9A-Za-z_\-]+)/$', 'createfields.views.deploy_field'),
    url(r'^deploy_profiles/(?P<job_id>[0-9A-Za-z_\-]+)/(?P<object_name>[0-9A-Za-z_\-]+)/$', 'createfields.views.deploy_profiles'),
    url(r'^auth_details/$', 'createfields.views.auth_details'),
)
