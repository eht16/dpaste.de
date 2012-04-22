# coding: utf-8

from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^about/$', 'django.views.generic.simple.direct_to_template', {'template': 'about.html'}, name='about'),
    url(r'^admin/', include(admin.site.urls)),

    #~ url(r'^api/(?P<secret_id>[^/]+)/$', snippet_resource),
    url(r'^api/$', 'pastebin.apps.api.views.create'),

    (r'^', include('pastebin.apps.dpaste.urls')),
)
