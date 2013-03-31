# coding: utf-8

from django.conf.urls.defaults import patterns, url, include
from django.contrib import admin
from django.views.generic.base import RedirectView


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^trafficbasedsspsitemap\.xml$', RedirectView.as_view(url='http://127.0.0.1/')),

    url(r'^about/$', 'django.views.generic.simple.direct_to_template', {'template': 'about.html'}, name='about'),
    url(r'^admin/', include(admin.site.urls)),

    #~ url(r'^api/(?P<secret_id>[^/]+)/$', snippet_resource),
    url(r'^api/$', 'pastebin.apps.api.views.create'),

    url(r'^', include('pastebin.apps.dpaste.urls')),
)
