from django.core.management.base import BaseCommand
import csv
import argparse
from django.conf import settings

from scenario.models import Scenario, \
    Structures, \
    NonConventionalStructures, ConventionalStructures, \
    ScenarioStructure


#
# snippet used to copy data from the 2 (NonConventional and Conventional) Structure tables
# to the proposed ScenarioStructure table
#

#
class Command(BaseCommand):
    help = 'snippet used to copy data to the ScenarioStructure table.'

    def handle(self, *args, **options):

        """ migrate the NonConventionalStructures data """

        structures = Structures.objects.filter(classification='nonconventional').order_by('sort_nu')
        existing_structures = NonConventionalStructures.objects.all()
        for row in existing_structures:
            scenario = Scenario.objects.filter(nonconventional_structures=row.id).first()

            # skip any stranded rows in the existing_structures
            if scenario is None:
                continue

            for structure in structures:
                if hasattr(row, structure.code + '_area'):
                    area_value = getattr(row, structure.code + '_area', None)
                if hasattr(row, structure.code + '_checkbox'):
                    checkbox_value = getattr(row, structure.code + '_checkbox', None)

                # delete any empty rows
                if area_value == None and checkbox_value is False:
                    if ScenarioStructure.objects.filter(scenario=scenario, structure=structure).exists():
                        c = ScenarioStructure.objects.get(scenario=scenario, structure=structure)
                        print('deleted "{}" {} {} {}'.format(scenario.scenario_title, structure.code, area_value,
                                                             checkbox_value))
                        c.delete()

                elif area_value is not None or checkbox_value is True:
                    print('"{}" {} {} {}'.format(scenario.scenario_title, structure.code, area_value, checkbox_value))

                    if not ScenarioStructure.objects.filter(scenario=scenario, structure=structure).exists():
                        c = ScenarioStructure.objects.create(scenario=scenario, structure=structure,
                            area=area_value,is_checked=checkbox_value
                        )
                        c.save()
                        print('created "{}" {} {} {}'.format(scenario.scenario_title, structure.code, area_value, checkbox_value))
                    else:
                        c = ScenarioStructure.objects.get(scenario=scenario, structure=structure)
                        changed_fields = set()

                        if c.area != area_value:
                            setattr(c, 'area', area_value)
                            changed_fields.add('area')

                        if c.is_checked != checkbox_value:
                            setattr(c, 'is_checked', area_value)
                            changed_fields.add('is_checked')

                        if len(changed_fields) > 0:
                            print('updated "{}" {} {} {}'.format(scenario.scenario_title, structure.code, area_value, checkbox_value))
                            c.save()
                        else:
                            print('no updates for "{}" {} {} {}'.format(scenario.scenario_title, structure.code, area_value, checkbox_value))

        """ migrate the ConventionalStructures data """

        structures = Structures.objects.filter(classification='conventional').order_by('sort_nu')
        existing_structures = ConventionalStructures.objects.all()
        for row in existing_structures:
            scenario = Scenario.objects.filter(conventional_structures=row.id).first()

            # skip any stranded rows in the existing_structures
            if scenario is None:
                continue

            for structure in structures:
                if hasattr(row, structure.code + '_area'):
                    area_value = getattr(row, structure.code + '_area', None)
                if hasattr(row, structure.code + '_checkbox'):
                    checkbox_value = getattr(row, structure.code + '_checkbox', None)

                # delete any empty rows
                if area_value == None and checkbox_value is False:
                    if ScenarioStructure.objects.filter(scenario=scenario, structure=structure).exists():
                        c = ScenarioStructure.objects.get(scenario=scenario, structure=structure)
                        print('deleted "{}" {} {} {}'.format(scenario.scenario_title, structure.code, area_value,
                                                             checkbox_value))
                        c.delete()

                elif area_value is not None or checkbox_value is True:
                    print('"{}" {} {} {}'.format(scenario.scenario_title, structure.code, area_value, checkbox_value))

                    if not ScenarioStructure.objects.filter(scenario=scenario, structure=structure).exists():
                        c = ScenarioStructure.objects.create(scenario=scenario, structure=structure,
                            area=area_value,is_checked=checkbox_value
                        )
                        c.save()
                        print('created "{}" {} {} {}'.format(scenario.scenario_title, structure.code, area_value, checkbox_value))
                    else:
                        c = ScenarioStructure.objects.get(scenario=scenario, structure=structure)
                        changed_fields = set()

                        if c.area != area_value:
                            setattr(c, 'area', area_value)
                            changed_fields.add('area')

                        if c.is_checked != checkbox_value:
                            setattr(c, 'is_checked', area_value)
                            changed_fields.add('is_checked')

                        if len(changed_fields) > 0:
                            print('updated "{}" {} {} {}'.format(scenario.scenario_title, structure.code, area_value, checkbox_value))
                            c.save()
                        else:
                            print('no updates for "{}" {} {} {}'.format(scenario.scenario_title, structure.code, area_value, checkbox_value))




