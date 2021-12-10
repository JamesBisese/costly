from django.core.management.base import BaseCommand
import csv
import argparse
from django.conf import settings

from scenario.models import Project


#
# snippet used to update Project.modified_date to null since I added the field late an
# accidentally set the value to the same as the default create_date
#
#
# (venv) C:\inetpub\wwwdjango\gsicosttool\src>c
#
class Command(BaseCommand):
    help = 'snippet used to update Project.modified_date to null only.'

    def handle(self, *args, **options):

        projects = Project.objects.all()
        for project in projects:
            print('Project "{} {}" '.format(project.id, project.modified_date))
            project.create_date = '2021-01-01 00:00:00.000000-00:00'
            project.modified_date = None
            print('Project "{} {}" '.format(project.id, project.modified_date))
            project.save()

