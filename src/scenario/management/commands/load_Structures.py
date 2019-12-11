from django.core.management.base import BaseCommand
import csv
import argparse
from django.conf import settings

from scenario.models import Structures


#
# data is loaded from csv file
#
#
# (venv) C:\inetpub\wwwdjango\costly\src>python manage.py load_Structures \
#                   --csvfile "C:\Data_and_Tools\raleigh_cost_tool\working\data\Stuctures_load.csv"
#
class Command(BaseCommand):
    help = 'Tool to help automate loading Structures model only.'

    default_file_path = r".\scenario\static\scenario\data\Structures.csv"

    def add_arguments(self, parser):
        parser.add_argument('--csvfile', type=argparse.FileType('r'),
                            default=self.default_file_path)


    def handle(self, *args, **options):

        # create each cost item shown in the list above
        with options['csvfile'] as csvfile:

            reader = csv.DictReader(csvfile)
            for row in reader:
                print('Structures "{}" '.format(row['code']))

                if not Structures.objects.filter(code=row['code']).exists():

                    print('Stuctures "{}" will need to be created'.format(row['code']))

                    i = Structures.objects.create(code=row['code'],
                                                 name=row['name'],
                                                 sort_nu=row['sort_nu'],
                                                 units=row['units'],
                                                 units_html=row['units_html'],
                                                 classification=row['classification'],
                                                 help_text = row['help_text']
                                                )

                    print('Structures "{}" created'.format(row['name']))
                else:
                    c = Structures.objects.get(code=row['code'])

                    c.name = row['name']
                    c.sort_nu = row['sort_nu']
                    c.units = row['units']
                    c.units_html = row['units_html']
                    c.classification = row['classification']
                    c.help_text = row['help_text']

                    c.save()
                    print('Structures "{}" exists already, updated'.format(row['name']))