import datetime
import sys
from optparse import make_option
from django.core.management.base import CommandError, LabelCommand
from dpaste.models import Snippet

class Command(LabelCommand):

    option_list = LabelCommand.option_list + (
        make_option('--max-age', '-m', action='store', dest='max_age_days', 
            help='Max age in days of snippets. Older snippets get purged. Default: 30'),
        make_option('--verbose', '-v', action='store_true', dest='verbose', 
            help='Print count of purged snippets'),
    )

    help = "Purges snippets that are older than 30 days"

    def handle(self, *args, **options):
        max_age_days = int(options.get('max_age_days')) or 30
        max_age = datetime.datetime.now()-datetime.timedelta(days=max_age_days)  
        
        deleted_snippet_count = Snippet.objects.filter(published__lt=max_age).count()
        Snippet.objects.filter(published__lt=max_age).delete()
        
        if options.get('verbose') or False:
            sys.stdout.write(u"%s snippets were deleted cause they are too old.\n" % deleted_snippet_count)