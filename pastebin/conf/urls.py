from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from piston.resource import Resource
from pastebin.apps.api.handlers import SnippetHandler

admin.autodiscover()
snippet_resource = Resource(handler=SnippetHandler)

urlpatterns = patterns('',
    url(r'^about/$', 'django.views.generic.simple.direct_to_template', {'template': 'about.html'}, name='about'),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^api/(?P<secret_id>[^/]+)/$', snippet_resource),
    url(r'^api/$', snippet_resource),    
    (r'^', include('pastebin.apps.dpaste.urls')),
)
