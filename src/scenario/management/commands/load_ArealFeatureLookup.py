from django.core.management.base import BaseCommand
import csv
import argparse

from scenario.models import ArealFeatureLookup

from scenario.scenario_frameworks import TEMPLATE_SCENARIO

#
# data is loaded from csv file
#
#
# (venv) C:\inetpub\wwwdjango\gsicosttool\src> \
#               python manage.py load_CostItems \
#                   --csvfile "C:\Data_and_Tools\raleigh_cost_tool\working\data\CostItemDefaultAssumptions_costs.csv"
#
class Command(BaseCommand):
    help = 'Tool to help automate creating ArealFeatureLookup model only - prints to screen.'

    # default_file_path = r".\scenario\static\scenario\data\ArealFeatureLookup.csv"
    #
    # def add_arguments(self, parser):
    #     parser.add_argument('--csvfile', type=argparse.FileType('r'),
    #                         default=self.default_file_path)

    def handle(self, *args, **options):

        doc = TEMPLATE_SCENARIO

        # print(doc.siteData.areal_features)

        labels = doc['siteData']['areal_features']['labels']


        # create each cost item shown in the list above

        # first truncate the table to add new values.
        # NOTE: this also truncates CostItemDefaultCosts - so that will need to be reloaded
        # CostItemDefaultAssumptions.objects.all().delete()

        ArealFeatureLookup.objects.all().delete()

        sort_nu = 0
        for code in labels:
            name = labels[code]
            sort_nu += 1

            print(code + '--' + labels[code])
            if not ArealFeatureLookup.objects.filter(code=code).exists():

                i = ArealFeatureLookup.objects.create(code=code,
                                             name=name,
                                             sort_nu=sort_nu,
                                             units='SF',
                                             units_html='SF',
                                             help_text = 'TBD'
                                            )
                print('created "{}"'.format(code))
            else:
                c = ArealFeatureLookup.objects.get(code=code)
                changed_fields = set()
                if str(getattr(c, 'name')) != name:
                    changed_fields.add(name)
                    print("'{}' ne '{}'".format(getattr(c, 'name'), name))
                    setattr(c, 'sort_nu', name)
                if str(getattr(c, 'sort_nu')) != sort_nu:
                    changed_fields.add(sort_nu)
                    print("'{}' ne '{}'".format(getattr(c, 'sort_nu'), sort_nu))
                    setattr(c, 'sort_nu', sort_nu)

                if len(changed_fields) > 0:
                    print('updated "{}" field(s): '.format(code) + ', '.join(changed_fields))
                    c.save()
                else:
                    print('no updates for "{}"'.format(code))

        count_nu = ArealFeatureLookup.objects.count()
        self.stdout.write('ArealFeatureLookup.objects.count() == {}'.format(count_nu))
