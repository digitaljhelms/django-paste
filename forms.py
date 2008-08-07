from django import newforms as forms
from django.conf import settings
from dpaste.models import Snippet
from dpaste.highlight import LEXER_LIST_ALL, LEXER_LIST, LEXER_DEFAULT

#===============================================================================
# Snippet Form and Handling
#===============================================================================

class SnippetForm(forms.ModelForm):

    lexer = forms.ChoiceField(
        choices=LEXER_LIST,
        initial=LEXER_DEFAULT,
    )

    def __init__(self, request, *args, **kwargs):
        super(SnippetForm, self).__init__(*args, **kwargs)
        self.request = request
        if self.request.session.get('userprefs') and \
           self.request.session['userprefs'].get('display_all_lexer', False):
            self.fields['lexer'].choices = LEXER_LIST_ALL
            self.fields['lexer'].help_text = u'Youre displaying the whole bunch of lexers!'
            self.fields['author'].initial = self.request.session['userprefs'].get('default_name', '')

    def save(self, parent=None, *args, **kwargs):

        # Set parent snippet
        if parent:
            print dir(self.instance)
            self.instance.parent = parent

        # Save snippet in the db
        super(SnippetForm, self).save(*args, **kwargs)

        # Add the snippet to the user session list
        if self.request.session.get('snippet_list', False):
            if len(self.request.session['snippet_list']) >= getattr(settings, 'MAX_SNIPPETS_PER_USER', 10):
                self.request.session['snippet_list'].pop(0)
            self.request.session['snippet_list'] += [self.instance.pk]
        else:
            self.request.session['snippet_list'] = [self.instance.pk]

        return self.request, self.instance

    class Meta:
        model = Snippet
        fields = (
            'title',
            'content',
            'author',
            'lexer',
        )


#===============================================================================
# User Settings
#===============================================================================

USERPREFS_FONT_CHOICES = [(None, 'Default')] + [
    (i, i) for i in sorted((
        'Monaco',
        'Bitstream Vera Sans Mono',
        'Courier New',
        'Consolas',
    ))
]

USERPREFS_SIZES = [(None, 'Default')] + [(i, '%dpx' % i) for i in range(5, 25)]

class UserSettingsForm(forms.Form):

    default_name = forms.CharField(required=False)
    display_all_lexer = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput
    )
    font_family = forms.ChoiceField(required=False, choices=USERPREFS_FONT_CHOICES)
    font_size = forms.ChoiceField(required=False, choices=USERPREFS_SIZES)
    line_height = forms.ChoiceField(required=False, choices=USERPREFS_SIZES)
