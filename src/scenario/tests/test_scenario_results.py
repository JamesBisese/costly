from decimal import *
import json
import logging
import unittest
import time

from django.db import IntegrityError, transaction
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase
from psycopg2.errors import UniqueViolation
from authtools.models import User
from scenario.models import Project, Scenario, \
    ArealFeatureLookup, Structures, \
    CostItem, \
    CostItemDefaultCosts, CostItemDefaultEquations, \
    StructureCostItemDefaultFactors, \
    ScenarioCostItemUserCosts, \
    StructureCostItemUserFactors, \
    ScenarioArealFeature, ScenarioStructure

from scenario.views import comparison_column

logger = logging.getLogger('developer')
logger.setLevel(logging.INFO)

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)

class BaseLookupTestCase(TestCase):
    units = 'SF'
    structure_code = 'bioretention_cell'
    structure_name = 'Bioretention Cells'

    costitem_code = 'mulch'
    costitem_name = "Mulch"

    """
    The only differences are
    ArealFeatureLookup has 'units_html'
    Structures has 'classification'

    """
    my_model = None  # same tests for ArealFeatureLookup, Structures, CostItem

    def setUp(self):
        pass


class ScenarioCostsTestCase(BaseLookupTestCase):
    """
    create 1 Scenario, with 1 Structure, and 1 CostItem all the required relations, then test the costs generated

    Note: this would have been great to start with, rather than do this far in ...

    """
    project_title = 'FOO'
    scenario_title = 'SCENARIO FOO'

    project = None
    scenario = None
    planning_and_design_factor = 15.0

    structure = None
    costitem = None
    costitem_default_equation = None
    scenario_costitem = None
    scenario_structure = None
    structure_costitem_user_factors = None

    def setUp(self):
        self.myStartTime = time.time()

        costitem_meta = {
            'code': self.costitem_code,
            'name': self.costitem_name,
            'units': self.units,
            'help_text': self.costitem_name + " Help Test"
        }
        self.costitem = CostItem.objects.create(**costitem_meta)

        costitem_meta = {
            'code': 'permanent_cover',
            'name': 'Permanent Cover',
            'units': self.units,
            'help_text': "Permanent Cover Help Test"
        }
        self.costitem2 = CostItem.objects.create(**costitem_meta)

        structure_meta = {
            'code': self.structure_code,
            'name': self.structure_name,
            'classification': 'nonconventional',
            'units': self.units,
            'units_html': self.units,
            'help_text': self.structure_name + " Help Test"
        }
        self.structure = Structures.objects.create(**structure_meta)

        structure_meta = {
            'code': 'wetland',
            'name': 'Stormwater Wetland',
            'classification': 'conventional',
            'units': self.units,
            'units_html': self.units,
            'help_text': "Stormwater Wetland Help Test"
        }
        self.structure2 = Structures.objects.create(**structure_meta)

        user = User.objects.create(
            name='testing',
            email='tester@acme.com',
            password='Abcfff$#$566',
            is_staff=True,
            is_active=True
        )
        user.save()
        self.project = Project.objects.create(
            user=user,
            project_title=self.project_title,
            project_area=1000,
            land_unit_cost=2.40

        )
        self.project.save()
        self.scenario = Scenario.objects.create(
            project=self.project,
            scenario_title=self.scenario_title,
            study_life=40,
            planning_and_design_factor=self.planning_and_design_factor
        )
        self.scenario.save()

        self.costitem_default_equation = CostItemDefaultEquations.objects.create(
            costitem=self.costitem,
            equation_tx='=x*area*depth*density*$',
            replacement_life=5,
            o_and_m_pct=20,
        )
        self.costitem_default_equation.save()
        self.assertIsNotNone(self.costitem_default_equation)

        self.costitem_default_equation2 = CostItemDefaultEquations.objects.create(
            costitem=self.costitem2,
            equation_tx='=x*area*$',
            replacement_life=5,
            o_and_m_pct=20,
        )
        self.costitem_default_equation2.save()

        self.scenario_costitem = ScenarioCostItemUserCosts.objects.create(
            scenario=self.scenario,
            costitem=self.costitem,
            cost_source='user',
            user_input_cost='1999.99',
            base_year=2022,
            replacement_life=15,
            o_and_m_pct=5,
        )
        self.scenario_costitem.save()
        self.assertIsNotNone(self.scenario_costitem)

        self.costitem_default_costs2 = CostItemDefaultCosts.objects.create(
            costitem=self.costitem2,
            value_numeric=688.99,
            valid_start_date_tx='2022',
        )
        self.costitem_default_costs2.save()
        self.assertIsNotNone(self.costitem_default_costs2)


        self.scenario_structure = ScenarioStructure.objects.create(
            scenario=self.scenario,
            structure=self.structure,
            area=1000,
            is_checked=True
        )
        self.scenario_structure.save()
        self.assertIsNotNone(self.scenario_structure)

        self.structure_costitem_default_factors = StructureCostItemDefaultFactors.objects.create(
            structure=self.structure,
            costitem=self.costitem,
            a_area=2,
            z_depth=1,
            d_density=1,
            n_number=0,
        )
        self.structure_costitem_default_factors.save()
        self.assertIsNotNone(self.structure_costitem_default_factors)

        # self.structure_costitem_user_factors = StructureCostItemUserFactors.objects.create(
        #     scenario=self.scenario,
        #     structure=self.structure,
        #     costitem=self.costitem,
        #
        #     checked=True,
        #     a_area=2,
        #     z_depth=1,
        #     d_density=1,
        #     n_number=0,
        # )
        # self.structure_costitem_user_factors.save()
        # self.assertIsNotNone(self.structure_costitem_user_factors)


    def tearDown(self):
        t = time.time() - self.myStartTime
        logger.debug('%s: %.3f seconds' % (self.id(), t))

    def test_scenario_most_simple_costs(self):
        """

        this is very simple.  1 structure, with 1 costitem.  so a single structure.classification

        :return:
        """

        """ make sure everything got made in setup """
        self.assertIsNotNone(self.structure)
        self.assertIsNotNone(self.costitem)
        self.assertIsNotNone(self.project)
        self.assertIsNotNone(self.scenario)

        self.assertIsNotNone(self.costitem_default_equation)
        self.assertIsNotNone(self.scenario_costitem)
        self.assertIsNotNone(self.scenario_structure)
        self.assertIsNotNone(self.structure_costitem_default_factors)

        scenario_costs = self.scenario.get_costs()

        # logger.debug("scenario costs is:\n{}".format(json.dumps(scenario_costs, indent=2, cls=DjangoJSONEncoder)))

        # make sure the costs for the single structure/costitem are the same as the overall costs
        self.assertEqual(self.scenario.planning_and_design_factor, self.planning_and_design_factor)

        # make sure the items are in the correct place
        ss = self.scenario_structure.structure
        sci = self.structure_costitem_default_factors

        self.assertTrue(
            ss.code in scenario_costs[ss.classification]['structures']
        )
        self.assertEqual(
            scenario_costs[ss.classification]['structures'][ss.code]['structure']['area'],
            self.scenario_structure.area
        )

        slc_class = scenario_costs['structure_life_cycle_costs'][ss.classification]

        self.assertTrue(
            ss.code in slc_class['structures']
        )
        self.assertEqual(
            scenario_costs[ss.classification]['structures'][ss.code]['cost_data'][sci.costitem.code]['results']['value_unformatted'],
            scenario_costs[ss.classification]['sum_value']
        )
        plc = scenario_costs['project_life_cycle_costs']['total']
        self.assertTrue(
            plc['planning_and_design'] > 0
        )
        self.assertEqual(
            plc['construction'] + plc['planning_and_design'] + plc['o_and_m'] + plc['replacement'], plc['sum']
        )
        plcs = scenario_costs['project_life_cycle_costs'][ss.classification]['costs']

        self.assertEqual(
            plc['sum'], plcs['sum']
        )

        slc = slc_class['costs']

        self.assertEqual(
            plc['construction'], slc['construction']
        )
        self.assertEqual(
            plc['planning_and_design'], slc['planning_and_design']
        )
        self.assertEqual(
            plc['o_and_m'], slc['o_and_m_sum']
        )
        self.assertEqual(
            plc['replacement'], slc['replacement_sum']
        )

        self.assertEqual(
            plc['sum'], slc['sum']
        )

        # "project_life_cycle_costs": {
        #     "total": {
        #         "construction": 3999980.0,
        #         "planning_and_design": 599997.0,
        #         "o_and_m": 4717786.0,
        #         "replacement": 4323709.0,
        #         "sum": 13641472.0 <- CORRECT
        #     },
        # "structure_life_cycle_costs": {
        #     "nonconventional": {
        #          ...
        #     },
        #     "conventional": {
        #         "meta": {
        #             "name": "Conventional (GSI) Structures"
        #         },
        #         "costs": {
        #             "sum": 9041495.0, <- ERROR
        #             "construction": 3999980.0,
        #             "planning_and_design": 599997.0,
        #             "o_and_m_sum": 4717786.0,
        #             "replacement_sum": 4323709.0
        #         },

        # logger.info('TODO sums are wrong in scenario_costs[\'structure_life_cycle_costs\'][ss.classification][\'costs\']')
        self.assertEqual(
            slc['construction'] + slc['planning_and_design'] + slc['o_and_m_sum'] + slc['replacement_sum'], slc['sum']
        )

        self.assertEqual(
            slc['construction'] + slc['planning_and_design'] + slc['o_and_m_sum'] + slc['replacement_sum'], plc['sum']
        )

        # there is a lot of nesting, which I think is okay, but confusing with this small data set
        slsci = slc_class['structures'][ss.code]['cost_items'][sci.costitem.code]['costs']

        self.assertTrue(
            slsci['planning_and_design'] > 0
        )

        self.assertEqual(
            slsci['construction'], slc['construction']
        )
        self.assertEqual(
            slsci['planning_and_design'], slc['planning_and_design']
        )
        self.assertEqual(
            slsci['o_and_m'], slc['o_and_m_sum']
        )
        self.assertEqual(
            slsci['replacement'], slc['replacement_sum']
        )

    def test_scenario_slightly_less_simple_costs(self):
        """

        this is very simple.  1 structure, with 1 costitem.  so a single structure.classification

        add another structure with a different classification

        :return:
        """
        self.scenario_structure2 = ScenarioStructure.objects.create(
            scenario=self.scenario,
            structure=self.structure2,
            area=1000,
            is_checked=True
        )
        self.scenario_structure2.save()
        self.assertIsNotNone(self.scenario_structure2)

        self.structure_costitem_default_factors2 = StructureCostItemDefaultFactors.objects.create(
            structure=self.structure2,
            costitem=self.costitem2,

            a_area=2,
            z_depth=1,
            d_density=1,
            n_number=0,
        )
        self.structure_costitem_default_factors2.save()
        self.assertIsNotNone(self.structure_costitem_default_factors2)


        scenario_costs = self.scenario.get_costs()

        # logger.debug("scenario costs is:\n{}".format(json.dumps(scenario_costs, indent=2, cls=DjangoJSONEncoder)))

        # make sure the costs for the single structure/costitem are the same as the overall costs
        self.assertEqual(self.scenario.planning_and_design_factor, self.planning_and_design_factor)

        # make sure the items are in the correct place
        ss = self.scenario_structure.structure
        sci = self.structure_costitem_default_factors

        self.assertTrue(ss.code in scenario_costs[ss.classification]['structures'])
        self.assertEqual(
            scenario_costs[ss.classification]['structures'][ss.code]['structure']['area'],
            self.scenario_structure.area
        )

        slc_class = scenario_costs['structure_life_cycle_costs'][ss.classification]
        self.assertTrue(ss.code in slc_class['structures'])
        self.assertEqual(
            scenario_costs[ss.classification]['structures'][ss.code]['cost_data'][sci.costitem.code]['results'][
                'value_unformatted'],
            scenario_costs[ss.classification]['sum_value']
        )

        plc = scenario_costs['project_life_cycle_costs']['total']
        self.assertTrue(
            plc['planning_and_design'] > 0
        )
        self.assertEqual(
            plc['construction'] + plc['planning_and_design'] + plc['o_and_m'] + plc['replacement'], plc['sum']
        )
        plcs = scenario_costs['project_life_cycle_costs'][ss.classification]['costs']


        # now the costs for the second structure
        ss2 = self.scenario_structure2.structure
        sci2 = self.structure_costitem_default_factors2

        self.assertTrue(ss2.code in scenario_costs[ss2.classification]['structures'])
        self.assertEqual(
            scenario_costs[ss2.classification]['structures'][ss2.code]['structure']['area'],
            self.scenario_structure2.area
        )

        slc_class2 = scenario_costs['structure_life_cycle_costs'][ss2.classification]
        self.assertTrue(ss2.code in slc_class2['structures'])
        self.assertEqual(
            scenario_costs[ss2.classification]['structures'][ss2.code]['cost_data'][sci2.costitem.code]['results'][
                'value_unformatted'],
            scenario_costs[ss2.classification]['sum_value']
        )

        plcs2 = scenario_costs['project_life_cycle_costs'][ss2.classification]['costs']

        # end new

        self.assertEqual(
            plc['sum'], plcs['sum'] + plcs2['sum']
        )

        slc = slc_class['costs']
        slc2 = slc_class2['costs']

        self.assertEqual(
            plc['construction'], slc['construction'] + slc2['construction']
        )
        self.assertEqual(
            plc['planning_and_design'], slc['planning_and_design'] + slc2['planning_and_design']
        )
        self.assertEqual(
            plc['o_and_m'], slc['o_and_m_sum'] + slc2['o_and_m_sum']
        )
        self.assertEqual(
            plc['replacement'], slc['replacement_sum'] + slc2['replacement_sum']
        )

        self.assertEqual(
            plc['sum'], slc['sum'] + slc2['sum']
        )

        self.assertEqual(
            slc['construction'] + slc['planning_and_design'] + slc['o_and_m_sum'] + slc['replacement_sum'], slc['sum']
        )

        self.assertEqual(
            plc['sum'],
            slc['construction'] + slc['planning_and_design'] + slc['o_and_m_sum'] + slc['replacement_sum']
                + slc2['construction'] + slc2['planning_and_design'] + slc2['o_and_m_sum'] + slc2['replacement_sum']
        )

        # there is a lot of nesting, which I think is okay, but confusing with this small data set
        slsci = slc_class['structures'][ss.code]['cost_items'][sci.costitem.code]['costs']

        self.assertTrue(
            slsci['planning_and_design'] > 0
        )
        self.assertEqual(
            slsci['construction'], slc['construction']
        )
        self.assertEqual(
            slsci['planning_and_design'], slc['planning_and_design']
        )
        self.assertEqual(
            slsci['o_and_m'], slc['o_and_m_sum']
        )
        self.assertEqual(
            slsci['replacement'], slc['replacement_sum']
        )

        slsci2 = slc_class2['structures'][ss2.code]['cost_items'][sci2.costitem.code]['costs']

        self.assertTrue(
            slsci2['planning_and_design'] > 0
        )
        self.assertEqual(
            slsci2['construction'], slc2['construction']
        )
        self.assertEqual(
            slsci2['planning_and_design'], slc2['planning_and_design']
        )
        self.assertEqual(
            slsci2['o_and_m'], slc2['o_and_m_sum']
        )
        self.assertEqual(
            slsci2['replacement'], slc2['replacement_sum']
        )


    def test_scenario_costitem_equation(self):
        """

        this is very simple.  1 structure, with 1 costitem.  so a single structure.classification

        :return:
        """

        """ make sure everything got made in setup """


        scenario_costs = self.scenario.get_costs()

        costitem_default_equation = CostItemDefaultEquations.objects.get(
            costitem=self.costitem,
        )
        self.assertIsNotNone(costitem_default_equation)
        costitem_default_equation.equation_tx = '=x*area*$'
        costitem_default_equation.save()

        scenario_costs2 = self.scenario.get_costs()

        self.assertNotEqual(scenario_costs, scenario_costs2)

        # check the equations are different
        ss = self.scenario_structure.structure
        ci_results = scenario_costs[ss.classification]['structures'][ss.code]['cost_data'][self.costitem.code]['results']

        ci_results2 = scenario_costs2[ss.classification]['structures'][ss.code]['cost_data'][self.costitem.code][
            'results']

        self.assertNotEqual(ci_results['equation'], ci_results2['equation'])

        self.assertNotEqual(ci_results['equation_calc'], ci_results2['equation_calc'])

        # now double the PER UNIT COST and see that the 'construction' value doubles
        scenario_costs = self.scenario.get_costs()
        self.assertEqual(self.scenario_costitem.user_input_cost.amount, Decimal('1999.99'))

        self.scenario_costitem.user_input_cost.amount = Decimal('1999.99') * 2
        self.scenario_costitem.save()

        scenario_costs2 = self.scenario.get_costs()
        ci_results = scenario_costs[ss.classification]['structures'][ss.code]['cost_data'][self.costitem.code]['results']
        ci_results2 = scenario_costs2[ss.classification]['structures'][ss.code]['cost_data'][self.costitem.code]['results']

        self.assertNotEqual(ci_results['value_unformatted'], ci_results2['value_unformatted'])
        self.assertEqual(ci_results['value_unformatted'], ci_results2['value_unformatted']/2)

        # now double the a_area factor
        scenario_costs = self.scenario.get_costs()
        self.assertEqual(self.structure_costitem_default_factors.a_area, 2)
        self.structure_costitem_default_factors.a_area = self.structure_costitem_default_factors.a_area * 2
        self.structure_costitem_default_factors.save()

        scenario_costs2 = self.scenario.get_costs()
        ci_results = scenario_costs[ss.classification]['structures'][ss.code]['cost_data'][self.costitem.code]['results']
        ci_results2 = scenario_costs2[ss.classification]['structures'][ss.code]['cost_data'][self.costitem.code]['results']

        self.assertNotEqual(ci_results['value_unformatted'], ci_results2['value_unformatted'])
        self.assertEqual(ci_results['value_unformatted'], ci_results2['value_unformatted']/2)

        # now double the structure area
        scenario_costs = self.scenario.get_costs()
        self.assertEqual(self.scenario_structure.area, 1000)
        self.scenario_structure.area = self.scenario_structure.area * 2
        self.scenario_structure.save()

        scenario_costs2 = self.scenario.get_costs()
        ci_results = scenario_costs[ss.classification]['structures'][ss.code]['cost_data'][self.costitem.code]['results']
        ci_results2 = scenario_costs2[ss.classification]['structures'][ss.code]['cost_data'][self.costitem.code]['results']

        self.assertNotEqual(ci_results['value_unformatted'], ci_results2['value_unformatted'])
        self.assertEqual(ci_results['value_unformatted'], ci_results2['value_unformatted'] / 2)


    def test_scenario_compare(self):
        """

        make 2 scenarios and make sure you can compare them, even if there is minimal data.
        This was used to test and fix an unhandled exception when impervious or pervious area was None

        :return:
        """

        # note: no Pervious or Impervious Areas for either scenario
        scenario2 = Scenario.objects.create(
            project=self.project,
            scenario_title=self.scenario_title + '(2)',
            study_life=40,
            planning_and_design_factor=self.planning_and_design_factor
        )
        scenario2.save()

        self.assertEqual(scenario2.pervious_area, 0)

        scenario_costs = comparison_column(self.scenario, scenario2)

        self.assertIsNotNone(scenario_costs)

        scenario2.impervious_area = None
        scenario2.pervious_area = None
        scenario2.save()

        self.assertIsNone(scenario2.pervious_area)

        scenario_costs = comparison_column(self.scenario, scenario2)

        self.assertIsNotNone(scenario_costs)

        scenario2.impervious_area = 100
        scenario2.pervious_area = 200
        scenario2.save()

        self.assertNotEqual(self.scenario.pervious_area, scenario2.pervious_area)

        scenario_costs = comparison_column(self.scenario, scenario2)

        self.assertIsNotNone(scenario_costs)

        scenario_costs = comparison_column(scenario2, self.scenario)

        self.assertIsNotNone(scenario_costs)

