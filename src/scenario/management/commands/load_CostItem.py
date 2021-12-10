from django.core.management.base import BaseCommand
import csv
import argparse

from scenario.models import CostItem


#
# data is loaded from csv file
#
#
# (venv) C:\inetpub\wwwdjango\gsicosttool\src> \
#               python manage.py load_CostItems \
#                   --csvfile "C:\Data_and_Tools\raleigh_cost_tool\working\data\CostItemDefaultAssumptions_costs.csv"
#
class Command(BaseCommand):
    help = 'Tool to help automate creating CostItem model only - prints to screen.'

    default_file_path = r".\scenario\static\scenario\data\CostItems.csv"

    def add_arguments(self, parser):
        parser.add_argument('--csvfile', type=argparse.FileType('r'),
                            default=self.default_file_path)

    def handle(self, *args, **options):

        # create each cost item shown in the list above
        with options['csvfile'] as csvfile:

            # first truncate the table to add new values.
            # NOTE: this also truncates CostItemDefaultCosts - so that will need to be reloaded
            # CostItemDefaultAssumptions.objects.all().delete()

            # CostItem.objects.all().delete()

            reader = csv.DictReader(csvfile)
            for row in reader:
                if not CostItem.objects.filter(code=row['code']).exists():

                    i = CostItem.objects.create(code=row['code'],
                                                 name=row['name'],
                                                 sort_nu=row['sort_nu'],
                                                 units=row['units'],
                                                 help_text = row['help_text']
                                                )
                    print('created "{}"'.format(row['code']))
                else:
                    c = CostItem.objects.get(code=row['code'])
                    changed_fields = set()
                    for field_nm in ('name',
                                     'sort_nu',
                                     'units',
                                     'help_text'):
                        if str(getattr(c, field_nm)) != str(row[field_nm]):
                            changed_fields.add(field_nm)
                            print("'{}' ne '{}'".format(getattr(c, field_nm), row[field_nm]))
                            setattr(c, field_nm, row[field_nm])

                    if len(changed_fields) > 0:
                        print('updated "{}" field(s): '.format(row['code']) + ', '.join(changed_fields))
                        c.save()
                    else:
                        print('no updates for "{}"'.format(row['code']))

            count_nu = CostItem.objects.count()
            self.stdout.write('CostItem.objects.count() == {}'.format(count_nu))
