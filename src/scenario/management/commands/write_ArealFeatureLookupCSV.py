from django.core.management.base import BaseCommand
import csv

from scenario.models import ArealFeatureLookup

#
# write data from ArealFeatureLookup on dev computer into a CSV for loading on new instance.
# this is a one-off I think
#
# (venv) C:\inetpub\wwwdjango\gsicosttool\src> python manage.py write_ArealFeatureLookupCSV
#
class Command(BaseCommand):
    help = 'Tool to help automate creating ArealFeatureLookup model only - prints to screen.'

    default_file_path = r".\scenario\static\scenario\data\ArealFeatureLookup.csv"

    def handle(self, *args, **options):
        areal_features = ArealFeatureLookup.objects.all()

        with open(self.default_file_path, 'w', newline='') as csvfile:
            w = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
            w.writerow(['sort_nu','code','name','units','units_html','help_text'])
            for a in areal_features:
                w.writerow([a.sort_nu, a.code, a.name, a.units, a.units_html, a.help_text])

        self.stdout.write('wrote {} records to file {}'.format(areal_features.count(), self.default_file_path))
