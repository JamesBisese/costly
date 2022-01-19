from django.core.management.base import BaseCommand
import csv
import argparse
from django.conf import settings

from scenario.models import Scenario, \
    ArealFeatures, \
    ArealFeatureLookup, ScenarioArealFeature


#
# snippet used to copy data from the 2 (NonConventional and Conventional) Structure tables
# to the proposed ScenarioStructure table
#

#
class Command(BaseCommand):
    help = 'snippet used to copy data to the ScenarioArealFeature table.'

    def handle(self, *args, **options):

        """ migrate the ArealFeature data to ScenarioArealFeature """

        ScenarioArealFeature.objects.all().delete()

        areal_features = ArealFeatureLookup.objects.all().order_by('sort_nu')
        existing_areal_features = ArealFeatures.objects.all().order_by('id')
        for row in existing_areal_features:
            scenario = Scenario.objects.filter(areal_features_id=row.id).first()

            # skip any stranded rows in the existing_structures
            if scenario is None:
                print(
                    'did not find scenario with id "{}"'.format(row.id))
                continue
            # print(
            #     'found scenario with id "{}"'.format(row.id))

            for areal_feature in areal_features:
                if hasattr(row, areal_feature.code + '_area'):
                    area_value = getattr(row, areal_feature.code + '_area', None)
                if hasattr(row, areal_feature.code + '_checkbox'):
                    checkbox_value = getattr(row, areal_feature.code + '_checkbox', None)

                # print(
                #     'found "{}" {} {} {}'.format(scenario.scenario_title, areal_feature.code, area_value, checkbox_value))

                # DELETE
                if area_value == None and checkbox_value is False:
                    if ScenarioArealFeature.objects.filter(scenario=scenario, areal_feature=areal_feature).exists():
                        c = ScenarioArealFeature.objects.get(scenario=scenario, areal_feature=areal_feature)
                        print('deleted "{}" {} {} {}'.format(scenario.scenario_title, areal_feature.code, area_value,
                                                             checkbox_value))
                        c.delete()

                elif area_value is not None or checkbox_value is True:
                    # print('"{}" {} {} {}'.format(scenario.scenario_title, areal_feature.code, area_value, checkbox_value))
                    # CREATE
                    if not ScenarioArealFeature.objects.filter(scenario=scenario, areal_feature=areal_feature).exists():
                        c = ScenarioArealFeature.objects.create(scenario=scenario,
                                                                areal_feature=areal_feature,
                                                                area=area_value,
                                                                is_checked=checkbox_value
                        )
                        c.save()
                        print('created "{}" {} {} {}'.format(scenario.scenario_title, areal_feature.code, area_value, checkbox_value))
                    else:
                        # UPDATE
                        c = ScenarioArealFeature.objects.get(scenario=scenario, areal_feature=areal_feature)
                        changed_fields = set()

                        if c.area != area_value:
                            setattr(c, 'area', area_value)
                            changed_fields.add('area')

                        if c.is_checked != checkbox_value:
                            setattr(c, 'is_checked', area_value)
                            changed_fields.add('is_checked')

                        if len(changed_fields) > 0:
                            print('updated "{}" {} {} {}'.format(scenario.scenario_title, areal_feature.code, area_value, checkbox_value))
                            c.save()
                        else:
                            print('no updates for "{}" {} {} {}'.format(scenario.scenario_title, areal_feature.code, area_value, checkbox_value))






