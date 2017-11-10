from django.core.management.base import NoArgsCommand, CommandError, BaseCommand
from createfields.models import Job, ErrorLog
import datetime

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        
        # Datetime for 1 day ago
        one_day_ago = datetime.datetime.now() - datetime.timedelta(hours=24)

        # Delete jobs over 24 hours old
        jobs = Job.objects.filter(created_date__lt = one_day_ago)
        jobs.delete()

        # Delete logs over 24 hours old
        logs = ErrorLog.objects.filter(created_date__lt = one_day_ago)
        logs.delete()


