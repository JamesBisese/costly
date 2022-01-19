from django.core.management.base import BaseCommand
from datetime import timedelta
from django.utils import timezone
from django.contrib.admin.models import LogEntry


class Command(BaseCommand):
    """

    list entries from the django_admin_log

    (venv) C:\inetpub\wwwdjango\gsicosttool\src> python manage.py list_AdminLog

    """
    help = 'Tool to start to understand the django_admin_log to see if it will work as a ChangeLog.'

    def handle(self, *args, **options):
        last_hour = timezone.now() - timedelta(days=10)
        last_hour_changes = LogEntry.objects.filter(action_time__gte=last_hour)

        for row in last_hour_changes:
            print(row)

