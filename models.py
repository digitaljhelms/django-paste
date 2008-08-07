import difflib

from django.db import models
from django.db.models import permalink
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
    title = models.CharField(max_length=120, blank=True)
    author = models.CharField(max_length=30, blank=True)
    content = models.TextField()
    content_highlighted = models.TextField(blank=True)
    lexer = models.CharField(max_length=30, default=LEXER_DEFAULT)
    published = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

    class Meta:
        ordering = ('-published',)

    def get_linecount(self):
        return len(self.content.splitlines())

    def save(self):
        self.content_highlighted = pygmentize(self.content, self.lexer)
        super(Snippet, self).save()

    @permalink
    def get_absolute_url(self):
        return ('snippet_details', (self.pk,))

    def __unicode__(self):
        return 'Snippet #%s' % self.pk

mptt.register(Snippet, order_insertion_by=['content'])