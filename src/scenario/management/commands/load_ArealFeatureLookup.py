from django.core.management.base import BaseCommand
import csv
import argparse

from scenario.models import ArealFeatureLookup

#
# data is loaded from csv file
# (venv) $> python manage.py load_CostItems \
#                   --csvfile "C:\Data_and_Tools\raleigh_cost_tool\working\data\ArealFeatureLookup.csv"
#
class Command(BaseCommand):
    help = 'Tool to help automate creating ArealFeatureLookup model only - prints to screen.'

    default_file_path = r".\scenario\static\scenario\data\ArealFeatureLookup.csv"

    def add_arguments(self, parser):
        parser.add_argument('--csvfile', type=argparse.FileType('r'),
                            default=self.default_file_path)

    def handle(self, *args, **options):

        with options['csvfile'] as csvfile:

            reader = csv.DictReader(csvfile)
            for row in reader:
                if not ArealFeatureLookup.objects.filter(code=row['code']).exists():

                    i = ArealFeatureLookup.objects.create(code=row['code'],
                                                     name=row['name'],
                                                     sort_nu=row['sort_nu'],
                                                 units='SF',
                                                 units_html='SF',
                                                 help_text = 'TBD'
                                                )
                    print('created "{}"'.format(row['code']))
                else:
                    c = ArealFeatureLookup.objects.get(code=row['code'])
                    changed_fields = set()
                    if str(getattr(c, 'name')) != row['name']:
                        changed_fields.add(row['name'])
                        print("'{}' ne '{}'".format(getattr(c, 'name'), row['name']))
                        setattr(c, 'sort_nu', row['name'])
                    if str(getattr(c, 'sort_nu')) != row['sort_nu']:
                        changed_fields.add(row['sort_nu'])
                        print("'{}' ne '{}'".format(getattr(c, 'sort_nu'), row['sort_nu']))
                        setattr(c, 'sort_nu', row['sort_nu'])

                    if len(changed_fields) > 0:
                        print('updated "{}" field(s): '.format(row['code']) + ', '.join(changed_fields))
                        c.save()
                    else:
                        print('no updates for "{}"'.format(row['code']))

        count_nu = ArealFeatureLookup.objects.count()
        self.stdout.write('ArealFeatureLookup.objects.count() == {}'.format(count_nu))
