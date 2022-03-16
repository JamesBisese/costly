from django.core.management.base import BaseCommand
import csv
import argparse
from django.conf import settings

from scenario.models import Scenario, CostItem, \
    CostItemDefaultCosts, CostItemDefaultEquations, \
    ScenarioCostItemUserCosts


class Command(BaseCommand):
    """
        one-off script to add 'ScenarioCostItemUserCosts' for each scenario.
        It creates them from the 'most recent' CostItemDefaultCosts
    """
    help = 'snippet used to create ScenarioCostItemUserCosts data for scenarios with no data.  used in updating models'

    def handle(self, *args, **options):

        """ migrate the ArealFeature data to ScenarioArealFeature """

        scenarios = Scenario.objects.all()
        cost_items = CostItem.objects.all()
        cost_item_default_factors = CostItemDefaultEquations.objects. \
            select_related('costitem') \
            .all() \
            .order_by('costitem__sort_nu')
        cost_item_default_costs = CostItemDefaultCosts.objects.\
            select_related('costitem')\
            .all()\
            .order_by('costitem__sort_nu', '-valid_start_date_tx')


        for scenario in scenarios:
            scenario_cost_item_user_costs = ScenarioCostItemUserCosts.objects \
                .select_related('costitem') \
                .filter(scenario=scenario)

            # if scenario_cost_item_user_costs.count() == 0:
            for cost_item in cost_items:
                user_costs = [x for x in scenario_cost_item_user_costs if
                                           x.costitem.code == cost_item.code]

                if len(user_costs) == 0:
                    default_costs = [x for x in cost_item_default_costs if
                                     x.costitem.code == cost_item.code]

                    if len(default_costs) == 0:
                        raise TypeError('unable to find default cost for cost_item "{}"'.format(cost_item.code))

                    # this will raise its own error if there is no default for the cost item
                    cost_item_default_factor = [x for x in cost_item_default_factors if
                                                x.costitem.code == cost_item.code][0]

                    if len(default_costs) > 0:
                        c = ScenarioCostItemUserCosts.objects.create(
                            scenario=scenario,
                            costitem=cost_item,
                            cost_source=str(default_costs[0].id),
                            default_cost=default_costs[0],

                            user_input_cost=None,
                            base_year=None,

                            replacement_life=cost_item_default_factor.replacement_life,
                            o_and_m_pct=cost_item_default_factor.o_and_m_pct
                        )
                        c.save()




