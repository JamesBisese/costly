from django.contrib import auth
from django.contrib.auth import get_user_model
import os
from django.core.management.base import BaseCommand
import csv
import argparse

from scenario.models import CostItem, Structures, CostItemDefaultFactors

#
# Load data from CSV file into table CostItemDefaultFactors
#  should be Structure-CostItem Default Factors
#
#
# (venv) C:\inetpub\wwwdjango\costly\src>python manage.py load_CostItemDefaultAssumptions \
#                   --csvfile ".\scenario\static\scenario\data\CostItemDefaultFactors.csv"
#
class Command(BaseCommand):
    help = 'Tool to load CostItemDefaultFactors into table from CSV file.'

    default_file_path = r".\scenario\static\scenario\data\CostItemDefaultFactors.csv"

    def add_arguments(self, parser):
        parser.add_argument('--csvfile', type=argparse.FileType('r'), default=self.default_file_path)


    def handle(self, *args, **options):

        with options['csvfile'] as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:

                if row['cost_item'] == '':
                    self.stdout.write('CostItem is blank!!!! Maybe extra newline in file ')
                    continue

                try:
                    cost_item = CostItem.objects.get(code=row['cost_item'])
                except CostItem.DoesNotExist:
                    raise Exception("Cost Item '{}' doesn't exist".format(row['cost_item']))

                try:
                    structure = Structures.objects.get(code=row['structure'])
                except:
                    raise Exception("Structures '{}' doesn't exist".format(row['structure']))

                # set blanks as null so they remove any previous value that might have been added
                field_list = ['a_area',
                              'z_depth',
                              'd_density',
                              'n_number']

                for field in field_list:
                    if row[field] == '':
                        row[field] = None

                if not CostItemDefaultFactors.objects.filter(costitem=cost_item, structure=structure).exists():

                    c = CostItemDefaultFactors.objects.create(costitem=cost_item, structure=structure)

                    for field_nm in (field_list):
                        setattr(c, field_nm, row[field_nm])
                    c.save()

                    print('created "{}-{}"'.format(row['structure'],row['cost_item']))
                else:
                    c = CostItemDefaultFactors.objects.get(costitem=cost_item, structure=structure)
                    changed_fields = set()

                    for field_nm in (field_list):
                        if getattr(c, field_nm) != row[field_nm]:
                            changed_fields.add(field_nm)
                            setattr(c, field_nm, row[field_nm])

                    if len(changed_fields) > 0:
                        print('updated "{}-{}" field(s): '.format(row['structure'],row['cost_item']) + ', '.join(changed_fields))
                        c.save()
                    else:
                        print('no updates for "{}-{}"'.format(row['structure'],row['cost_item']))

        count_nu = CostItemDefaultFactors.objects.count()
        self.stdout.write('CostItemDefaultFactors.objects.count()== {}'.format(count_nu))