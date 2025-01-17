from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template.context import RequestContext
from django.http import Http404, HttpResponseRedirect, HttpResponseBadRequest, \
    HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils.translation import ugettext_lazy as _
from honeypot.decorators import check_honeypot
from pastebin.apps.dpaste.forms import SnippetForm, UserSettingsForm
from pastebin.apps.dpaste.models import Snippet
from pastebin.apps.dpaste.highlight import pygmentize, guess_code_lexer
from django.core.urlresolvers import reverse
from django.utils import simplejson
import difflib
from datetime import datetime


def _get_snippet_list():
    try:
        max_snippets = getattr(settings, 'MAX_SNIPPETS_PER_USER', 10)
        snippet_list = get_list_or_404(Snippet)[:max_snippets]
    except ValueError:
        snippet_list = list()
    return snippet_list


def _clean_expired_snippets():
    deleteable_snippets = Snippet.objects.filter(expires__lte=datetime.now())
    if deleteable_snippets:
        deleteable_snippets.delete()


@check_honeypot
def snippet_new(request, template_name='dpaste/snippet_new.html'):

    if request.method == "POST":
        snippet_form = SnippetForm(data=request.POST, request=request)
        if snippet_form.is_valid():
            request, new_snippet = snippet_form.save()
            return HttpResponseRedirect(new_snippet.get_absolute_url())
    else:
        # housekeeping
        _clean_expired_snippets()
        snippet_form = SnippetForm(request=request)

    snippet_list = _get_snippet_list()

    template_context = {
        'snippet_form': snippet_form,
        'snippet_list': snippet_list,
    }

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )


@check_honeypot
def snippet_details(request, snippet_id, template_name='dpaste/snippet_details.html', is_raw=False):

    # housekeeping
    _clean_expired_snippets()

    try:
        snippet = Snippet.objects.get(secret_id=snippet_id)
    except MultipleObjectsReturned:
        raise Http404('Multiple snippets exist for this slug. This should never '
                      'happen but its likely that you are a spam bot, so I dont '
                      'care.')
    except ObjectDoesNotExist:
        raise Http404('This snippet does not exist anymore. Its likely that its '
                      'lifetime is expired.')

    tree = snippet.get_root()
    tree = tree.get_descendants(include_self=True)

    new_snippet_initial = {
        'content': snippet.content,
        'lexer': snippet.lexer,
    }

    if request.method == "POST":
        snippet_form = SnippetForm(data=request.POST, request=request, initial=new_snippet_initial)
        if snippet_form.is_valid():
            request, new_snippet = snippet_form.save(parent=snippet)
            return HttpResponseRedirect(new_snippet.get_absolute_url())
    else:
        snippet_form = SnippetForm(initial=new_snippet_initial, request=request)

    snippet_list = _get_snippet_list()
    template_context = {
        'snippet_list': snippet_list,
        'snippet_form': snippet_form,
        'snippet': snippet,
        'lines': range(snippet.get_linecount()),
        'tree': tree,
    }

    response = render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )

    if is_raw:
        response['Content-Type'] = 'text/plain;charset=UTF-8'
        return response
    else:
        return response


def snippet_delete(request, snippet_id):
    snippet = get_object_or_404(Snippet, secret_id=snippet_id)
    try:
        snippet_list = request.session['snippet_list']
    except KeyError:
        return HttpResponseForbidden('You have no recent snippet list, cookie error?')
    if not snippet.pk in snippet_list:
        return HttpResponseForbidden('That\'s not your snippet, sucka!')
    snippet.delete()
    return HttpResponseRedirect(reverse('snippet_new'))


def snippet_list(request, template_name='dpaste/snippet_list.html'):

    snippet_list = _get_snippet_list()

    template_context = {
        'snippets_max': getattr(settings, 'MAX_SNIPPETS_PER_USER', 10),
        'snippet_list': snippet_list,
    }

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request)
    )


def userprefs(request, template_name='dpaste/userprefs.html'):

    if request.method == 'POST':
        settings_form = UserSettingsForm(request.POST, initial=request.session.get('userprefs', None))
        if settings_form.is_valid():
            request.session['userprefs'] = settings_form.cleaned_data
            settings_saved = True
    else:
        settings_form = UserSettingsForm(initial=request.session.get('userprefs', None))
        settings_saved = False

    template_context = {
        'settings_form': settings_form,
        'settings_saved': settings_saved,
    }

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request))


def snippet_diff(request, template_name='dpaste/snippet_diff.html'):

    if request.GET.get('a') and request.GET.get('a').isdigit() \
                    and request.GET.get('b') and request.GET.get('b').isdigit():
        try:
            fileA = Snippet.objects.get(pk=int(request.GET.get('a')))
            fileB = Snippet.objects.get(pk=int(request.GET.get('b')))
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(u'Selected file(s) does not exist.')
    else:
        return HttpResponseBadRequest(u'You must select two snippets.')

    if fileA.content != fileB.content:
        d = difflib.unified_diff(
            fileA.content.splitlines(),
            fileB.content.splitlines(),
            'Original',
            'Current',
            lineterm=''
        )
        difftext = '\n'.join(d)
        difftext = pygmentize(difftext, 'diff')
    else:
        difftext = _(u'No changes were made between this two files.')

    template_context = {
        'difftext': difftext,
        'fileA': fileA,
        'fileB': fileB,
    }

    return render_to_response(
        template_name,
        template_context,
        RequestContext(request))


def guess_lexer(request):
    code_string = request.GET.get('codestring', False)
    response = simplejson.dumps({'lexer': guess_code_lexer(code_string)})
    return HttpResponse(response)
