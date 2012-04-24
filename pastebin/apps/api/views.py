# coding: utf-8

from django.contrib.sites.models import Site
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from pastebin.apps.api.create import CreateSnippetApiController, SnippetValidationError


@require_POST
@csrf_exempt
def create(request):
    try:
        controller = CreateSnippetApiController(request)
        snippet = controller.create()
    except SnippetValidationError, e:
        return HttpResponseBadRequest(unicode(e), content_type=u'text/plain')

    site = Site.objects.get_current()
    absolute_url = snippet.get_absolute_url()
    result = u'http://%s%s' % (site.domain, absolute_url)
    return HttpResponse(result, content_type=u'text/plain')
