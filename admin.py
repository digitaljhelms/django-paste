from dpaste.models import Snippet
from django.contrib import admin

class SnippetAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'lexer',
        'published',
    )

admin.site.register(Snippet, SnippetAdmin)
