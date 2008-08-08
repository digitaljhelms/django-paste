import difflib

from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _
import mptt

from dpaste.highlight import LEXER_DEFAULT, pygmentize


class Snippet(models.Model):
    """
    Stores the snippets.

    Some Doctests:
    ==============
    >>> from dpaste.models import Snippet
    >>> p = Snippet(title=u'foobar', author=u'foo@bar.invalid', lexer=u'text', content=u'foo')
    >>> p.title
    u'foobar'

    >>> p.content_highlighted
    ''

    # Highlighted content is processed on save
    >>> p.save()

    # Now there is highlighted content (well, it's not really highlighted due
    # the simple text lexer.
    >>> p.content_highlighted
    u'foo\\n'

    Relationships between snippets
    ------------------------------
    >>> q = Snippet(title=u'answer to foobar', lexer=u'text', content=u'bar')
    >>> q.parent = p
    >>> q.save()

    # There is now a relationship between ``q`` and ``p``
    >>> q.get_root()
    <Snippet: Snippet #1>
    """
    title = models.CharField(_(u'Title'), max_length=120, blank=True)
    author = models.CharField(_(u'Author'), max_length=30, blank=True)
    content = models.TextField(_(u'Content'), )
    content_highlighted = models.TextField(_(u'Highlighted Content'), blank=True)
    lexer = models.CharField(_(u'Lexer'), max_length=30, default=LEXER_DEFAULT)
    published = models.DateTimeField(_(u'Published'), auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

    class Meta:
        ordering = ('-published',)

    def get_linecount(self):
        return len(self.content.splitlines())

    def content_splitted(self):
        return self.content_highlighted.splitlines()

    def save(self):
        self.content_highlighted = pygmentize(self.content, self.lexer)
        super(Snippet, self).save()

    @permalink
    def get_absolute_url(self):
        return ('snippet_details', (self.pk,))

    def __unicode__(self):
        return '%s #%s' % (_(u'Snippet'), self.pk)

mptt.register(Snippet, order_insertion_by=['content'])
