import datetime
import difflib
import random
import mptt
import re
import time
from django.db import models
from django.core.urlresolvers import reverse
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
from pastebin.apps.dpaste.highlight import LEXER_DEFAULT, pygmentize

t = 'abcdefghijkmnopqrstuvwwxyzABCDEFGHIJKLOMNOPQRSTUVWXYZ1234567890'
def generate_secret_id(length=5):
    return ''.join([random.choice(t) for i in range(length)])

class Snippet(models.Model):
    secret_id = models.CharField(_(u'Secret ID'), max_length=255, blank=True)
    title = models.CharField(_(u'Title'), max_length=120, blank=True)
    author = models.CharField(_(u'Author'), max_length=30, blank=True)
    content = models.TextField(_(u'Content'), )
    content_highlighted = models.TextField(_(u'Highlighted Content'), blank=True)
    lexer = models.CharField(_(u'Lexer'), max_length=30, default=LEXER_DEFAULT)
    published = models.DateTimeField(_(u'Published'), blank=True)
    expires = models.DateTimeField(_(u'Expires'), blank=True, help_text='asdf')
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

    class Meta:
        ordering = ('-published',)

    def age(self):
        age = time.mktime(self.published.timetuple())
        return self._readable_delta(age)

    def _readable_delta(self, from_seconds, until_seconds=None):
        '''Returns a nice readable delta.

        readable_delta(1, 2)           # 1 second ago
        readable_delta(1000, 2000)     # 16 minutes ago
        readable_delta(1000, 9000)     # 2 hours, 133 minutes ago
        readable_delta(1000, 987650)   # 11 days ago
        readable_delta(1000)           # 15049 days ago (relative to now)
        '''

        if not until_seconds:
            until_seconds = time.time()

        seconds = until_seconds - from_seconds
        delta = datetime.timedelta(seconds=seconds)

        # deltas store time as seconds and days, we have to get hours and minutes ourselves
        delta_minutes = delta.seconds // 60
        delta_hours = delta_minutes // 60

        ## show a fuzzy but useful approximation of the time delta
        if delta.days:
            return '%d days ago' % (delta.days)
        elif delta_hours:
            return '%d hours ago' % (delta_hours)
        elif delta_minutes:
            return '%d minutes ago' % (delta_minutes)
        else:
            return '%d seconds ago' % (delta.seconds)

    def get_linecount(self):
        return len(self.content.splitlines())

    def content_splitted(self):
        return self.content_highlighted.splitlines()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.published = datetime.datetime.now()
            self.secret_id = generate_secret_id()
        self.content_highlighted = self.content
        super(Snippet, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('snippet_details', kwargs={'snippet_id': self.secret_id})

    def __unicode__(self):
        return '%s' % self.secret_id

mptt.register(Snippet, order_insertion_by=['content'])


class SpamwordManager(models.Manager):
    def get_regex(self):
        return re.compile(r'|'.join((i[1] for i in self.values_list())),
            re.MULTILINE)

class Spamword(models.Model):
    word = models.CharField(max_length=100)
    objects = SpamwordManager()

    def __unicode__(self):
        return self.word
