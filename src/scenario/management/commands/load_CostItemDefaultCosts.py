from django.contrib import auth
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
import csv
import argparse
from djmoney.money import Money
# from moneyfield import MoneyField
from scenario.models import CostItem, CostItemDefaultCosts
from decimal import *
#
# data is loaded from csv file
#
#
# (venv) C:\inetpub\wwwdjango\costly\src>python manage.py create_CostItemDefaultCosts \
#                   --csvfile "C:\Data_and_Tools\raleigh_cost_tool\working\data\CostItemDefaultAssumptions_costs.csv"
#
class Command(BaseCommand):
  help = 'Tool to load CostItemDefaultCosts table.'

  default_file_path = r".\scenario\static\scenario\data\CostItemDefaultCosts.csv"

  def add_arguments(self, parser):
      parser.add_argument('--csvfile', type=argparse.FileType('r'),
                          default=self.default_file_path)

      # Named (optional) arguments
      parser.add_argument(
          '--delete',
          action='store_true',
          help='Delete existing content before inserting new data',
      )

  def handle(self, *args, **options):

    # delete existing rows (for now)
    if options['delete']:
        count_nu = CostItemDefaultCosts.objects.count()
        self.stdout.write('Deleting {} existing rows'.format(count_nu))
        CostItemDefaultCosts.objects.all().delete()



    # create each cost item shown in the list above
    with options['csvfile'] as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:

            # set blanks as null so they remove any previos value that might have been added
            field_list = ['replacement_life',
                          'o_and_m_pct',
                          'rsmeans_va',
                          'db_25pct_va',
                          'db_50pct_va',
                          'db_75pct_va']
            for field in field_list:
                if row[field] == '':
                    row[field] = None

            try:
                cost_item = CostItem.objects.get(code=row['code'])
            except CostItem.DoesNotExist:
                # we have no object!  do something
                raise ValueError('CostItem "{}" doesnt exist'.format(row['code']))

            if not CostItemDefaultCosts.objects.filter(costitem=cost_item).exists():

                i = CostItemDefaultCosts.objects.create(
                                costitem=cost_item,
                                replacement_life=row['replacement_life'],
                                o_and_m_pct=row['o_and_m_pct'],
                                rsmeans_va=row['rsmeans_va'],
                                db_25pct_va=row['db_25pct_va'],
                                db_50pct_va=row['db_50pct_va'],
                                db_75pct_va=row['db_75pct_va'],
                                                    )

                print('created "{}"'.format(row['code']))
            else:
                c = CostItemDefaultCosts.objects.get(costitem__code=row['code'])
                changed_fields = set()
                for field_nm in ('replacement_life',
                                 'o_and_m_pct',
                                 'rsmeans_va',
                                 'db_25pct_va',
                                 'db_50pct_va',
                                 'db_75pct_va'):
                    val = getattr(c, field_nm)

                    if (isinstance(val, Money)):
                        val = val.amount
                        field_val = Decimal("{0:.2f}".format(float(row[field_nm])))
                        if val != field_val:
                            changed_fields.add(field_nm)
                            print("money '{}' ne '{}'".format(str(val), str(field_val)))
                            setattr(c, field_nm, field_val)
                    elif str(val) != str(row[field_nm]):
                        changed_fields.add(field_nm)
                        print("'{}' ne '{}'".format(val, row[field_nm]))
                        setattr(c, field_nm, row[field_nm])

                if len(changed_fields) > 0:
                    print('updated "{}" field(s): '.format(row['code']) + ', '.join(changed_fields))
                    c.save()
                else:
                    print('no updates for "{}"'.format(row['code']))

                # c = CostItemDefaultCosts.objects.get(costitem=cost_item)
                #
                # c.replacement_life = row['replacement_life']
                # c.o_and_m_pct = row['o_and_m_pct']
                # c.rsmeans_va = row['rsmeans_va']
                # c.db_25pct_va = row['db_25pct_va']
                # c.db_50pct_va = row['db_50pct_va']
                # c.db_75pct_va = row['db_75pct_va']
                # c.equation = row['equation_tx']
                #
                # c.save()
                # print('CostItemDefaultCosts "{}" exists already, updated'.format(cost_item))

    count_nu = CostItemDefaultCosts.objects.count()
    self.stdout.write('CostItemDefaultCosts.objects.count() == {}'.format(count_nu))
