from django.core.management.base import BaseCommand
import csv
import argparse

from scenario.models import CostItem, CostItemDefaultEquations


#
# data is loaded from csv file
#
#
# (venv) C:\inetpub\wwwdjango\gsicosttool\src> \
#               python manage.py load_CostItems \
#                   --csvfile "C:\Data_and_Tools\raleigh_cost_tool\working\data\CostItemDefaultAssumptions_costs.csv"
#
class Command(BaseCommand):
    help = 'Tool to load CostItemDefaultEquations into table from CSV file.'

    default_file_path = r".\scenario\static\scenario\data\CostItemDefaultEquations.csv"

    def add_arguments(self, parser):
        parser.add_argument('--csvfile', type=argparse.FileType('r'), default=self.default_file_path)

    def handle(self, *args, **options):

        # create each cost item shown in the list above
        with options['csvfile'] as csvfile:

            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    cost_item = CostItem.objects.get(code=row['cost_item'])
                except CostItem.DoesNotExist:
                    # we have no object!  do something
                    raise ValueError('CostItem "{}" does not exist. Error in input file'.format(row['cost_item']))

                if not CostItemDefaultEquations.objects.filter(costitem=cost_item).exists():
                    i = CostItemDefaultEquations.objects.create(costitem=cost_item,
                                                 equation_tx=row['equation_tx'],
                                                 replacement_life=row['replacement_life'],
                                                 o_and_m_pct=row['o_and_m_pct'],
                                                 help_text=row['help_text']
                                                )

                    print('created "{}"'.format(row['cost_item']))
                else:
                    c = CostItemDefaultEquations.objects.get(costitem=cost_item)
                    changed_fields = set()
                    for field_nm in ('equation_tx',
                                     'replacement_life',
                                     'o_and_m_pct',
                                     'help_text'):
                        if getattr(c, field_nm) != row[field_nm]:
                            changed_fields.add(field_nm)
                            setattr(c, field_nm, row[field_nm])

                    if len(changed_fields) > 0:
                        print('updated "{}" field(s): '.format(row['cost_item']) + ', '.join(changed_fields))
                        c.save()
                    else:
                        print('no updates for "{}"'.format(row['cost_item']))

            count_nu = CostItemDefaultEquations.objects.count()
            self.stdout.write('CostItemDefaultEquations.objects.count() == {}'.format(count_nu))
