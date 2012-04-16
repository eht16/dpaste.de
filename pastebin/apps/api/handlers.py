# coding: utf-8

from datetime import datetime, timedelta
from django.contrib.sites.models import Site
from pastebin.apps.dpaste.models import Snippet
from piston.handler import AnonymousBaseHandler
from piston.utils import rc


class SnippetHandler(AnonymousBaseHandler):
    allowed_methods = ('POST',)
    fields = ('title', 'content','expires','author','lexer')
    model = Snippet

    def create(self, request):
        if not request.POST.get('content'):
            return rc.BAD_REQUEST

        content = request.POST.get('content')
        expires_seconds = request.POST.get('expires', u'')
        author = request.POST.get('author', u'')
        title = request.POST.get('title', u'')
        lexer = request.POST.get('lexer', u'')

        # TODO add more validations

        if expires_seconds:
            try:
                expires_seconds = int(expires_seconds)
            except (ValueError, TypeError):
                expires_seconds = None

        if not expires_seconds:
            expires_seconds = 30 * 24 * 60 * 60  # 30 days


        expires = datetime.now() + timedelta(seconds=expires_seconds)

        s = Snippet.objects.create(
            content=content,
            author=author,
            title=title,
            lexer=lexer,
            expires=expires
        )
        s.save()
        return 'http://%s%s' % (Site.objects.get_current().domain, s.get_absolute_url())
