import logging
import unittest
import time

from django.db import IntegrityError, transaction
from django.core.exceptions import ObjectDoesNotExist, ValidationError
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

logger = logging.getLogger('developer')
logger.setLevel(logging.DEBUG)

class ProjectTestCase(TestCase):
    user = None
    user2 = None
    user3 = None
    def setUp(self):
        self.user = User.objects.create(
            name='testing',
            email='tester@acme.com',
            password='Abcfff$#$566',
            is_staff=True,
            is_active=True
        )
        self.user2 = User.objects.create(
            name='testing22',
            email='tester22@acme.com',
            password='Abcfff$#$56622',
            is_staff=True,
            is_active=True
        )
        self.user3 = User.objects.create(
            name='testing33',
            email='tester33@acme.com',
            password='Abcfff$#$56633',
            is_staff=False,
            is_active=False
        )
        Project.objects.create(
            user=self.user,
            project_title="FOO",
            project_area=1000,
            land_unit_cost=2.40

        )
        Project.objects.create(
            user=self.user,
            project_title="BAR",
            project_area=1001,
            land_unit_cost=2.50
        )

    def test_project_has_minimum_attributes(self):
        p = Project.objects.get(project_title="FOO")

        self.assertEqual(p.project_title, "FOO")
        self.assertEqual(p.project_area, '1000')  # TODO project_area should be area and it should be a float

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                p.project_title = 'BAR'
                p.save()

        with self.assertRaises(ValidationError) as cm:
            p.project_title = ''
            p.full_clean()
        self.assertTrue('project_title' in cm.exception.message_dict)
        p.project_title = 'FOO'

        with transaction.atomic():
            with self.assertRaises(Exception):
                Project.objects.create(
                    user=self.user,
                    project_title="FOO",
                    project_area=1000,
                    land_unit_cost=2.40
                )

        with transaction.atomic():
            p2 = Project.objects.create(
                user=self.user2,
                project_title="FOO",
                project_area=1000,
                land_unit_cost=2.40
            )
            self.assertTrue(p.project_title == 'FOO')
            self.assertTrue(p2.project_title == 'FOO')


    def test_project_permissions(self):
        p = Project.objects.get(project_title="FOO")

        self.assertFalse(self.user3.has_perm('scenario.add__project'))

        with transaction.atomic():
            # note: self.user3 is not the one creating this project.
            p2 = Project.objects.create(
                user=self.user3,
                project_title="FOO",
                project_area=1000,
                land_unit_cost=2.40
            )
            p2.full_clean()
            p2.save()
            # print(p2.project_title)


class BaseLookupTestCase(TestCase):
    units = 'SF'
    alpha_code = 'swale'
    alpha_name = 'Swale Test'

    beta_code = 'lake'
    beta_name = "Lake Test"

    """
    The only differences are
    ArealFeatureLookup has 'units_html'
    Structures has 'classification'
    
    """
    my_model = None # same tests for ArealFeatureLookup, Structures, CostItem

    def setUp(self):
        pass


class BaseLookupTestCaseMixin:
    def test_has_minimum_attributes(self):
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                m = self.my_model.objects.create(name=self.alpha_name,
                                            units=self.units,
                                            help_text=self.alpha_name + " Help Test")
                m.save()

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                m = self.my_model.objects.create(code=self.alpha_code,
                                            units=self.units,
                                            help_text=self.alpha_name + " Help Test")
                m.save()

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                m = self.my_model.objects.create(code=self.alpha_code, name=self.alpha_name,
                                            help_text=self.alpha_name + " Help Test")
                m.save()

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                m = self.my_model.objects.create(code=self.alpha_code, name=self.alpha_name,
                                            units=self.units)
                m.save()

    def test_exists(self):
        alpha = self.my_model.objects.get(code=self.alpha_code)
        beta = self.my_model.objects.get(code=self.beta_code)

        self.assertEqual(alpha.name, self.alpha_name)
        self.assertEqual(beta.name, self.beta_name)

        with self.assertRaises(ObjectDoesNotExist):
            self.my_model.objects.get(code=self.alpha_code + 'FOOBAR')

        with self.assertRaises(ObjectDoesNotExist):
            self.my_model.objects.get(name=self.alpha_name + 'FOOBAR')

        self.assertTrue(self.my_model.objects.filter(units=self.units))
        self.assertFalse(self.my_model.objects.filter(units='FOOBAR'))

    def test_integrity_error(self):
        alpha = self.my_model.objects.get(code=self.alpha_code)
        beta = self.my_model.objects.get(code=self.beta_code)

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                m = self.my_model.objects.create(code=self.alpha_code, name=self.alpha_name,
                                            units=self.units, help_text=self.alpha_name + " Help Test")
                m.save()

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                alpha.code = beta.code
                alpha.save()

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                alpha.name = beta.name
                alpha.save()


class ArealFeatureLookupTestCase(BaseLookupTestCase, BaseLookupTestCaseMixin):
    @classmethod
    # def setUp(cls):
    #     super().setUpClass()
    #     cls.my_model = CostItem

    def setUp(self):
        self.my_model = ArealFeatureLookup
        alpha = {
            'code': self.alpha_code, 'name': self.alpha_name,
            'units': self.units,
            'help_text': self.alpha_name + " Help Test"
        }
        beta = {
            'code': self.beta_code, 'name': self.beta_name,
            'units': self.units,
            'help_text': self.beta_name + " Help Test"
        }
        alpha['units_html'] = alpha['units']
        beta['units_html'] = beta['units']

        self.my_model.objects.create(**alpha)
        self.my_model.objects.create(**beta)


class StructureTestCase(BaseLookupTestCase, BaseLookupTestCaseMixin):
    @classmethod
    # def setUp(cls):
    #     super().setUpClass()
    #     cls.my_model = CostItem

    def setUp(self):
        self.my_model = Structures
        alpha = {
            'code': self.alpha_code, 'name': self.alpha_name,
            'units': self.units,
            'help_text': self.alpha_name + " Help Test"
        }
        beta = {
            'code': self.beta_code, 'name': self.beta_name,
            'units': self.units,
            'help_text': self.beta_name + " Help Test"
        }

        alpha['units_html'] = alpha['units']
        alpha['classification'] = 'conventional'

        beta['units_html'] = beta['units']
        beta['classification'] = 'conventional'

        self.my_model.objects.create(**alpha)
        self.my_model.objects.create(**beta)

    def test_classification(self):
        alpha = self.my_model.objects.get(code=self.alpha_code)

        with transaction.atomic():
            alpha.classification = 'nonconventional'
            alpha.save()

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                alpha.classification = 'FOOBAR'
                alpha.save()


class CostItemTestCase(BaseLookupTestCase, BaseLookupTestCaseMixin):
    def setUp(self):
        self.my_model = CostItem
        alpha = {
            'code': self.alpha_code, 'name': self.alpha_name,
            'units': self.units,
            'help_text': self.alpha_name + " Help Test"
        }
        beta = {
            'code': self.beta_code, 'name': self.beta_name,
            'units': self.units,
            'help_text': self.beta_name + " Help Test"
        }

        self.my_model.objects.create(**alpha)
        self.my_model.objects.create(**beta)


class CostItemDefaultCostsTestCase(BaseLookupTestCase):
    def setUp(self):
        self.my_model = CostItem
        alpha = {
            'code': self.alpha_code, 'name': self.alpha_name,
            'units': self.units,
            'help_text': self.alpha_name + " Help Test"
        }
        beta = {
            'code': self.beta_code, 'name': self.beta_name,
            'units': self.units,
            'help_text': self.beta_name + " Help Test"
        }

        self.my_model.objects.create(**alpha)
        self.my_model.objects.create(**beta)


    def test_cost_item_unique(self):
        alpha = self.my_model.objects.get(code=self.alpha_code)
        with transaction.atomic():
            with transaction.atomic():
                m = CostItemDefaultCosts.objects.create(costitem=alpha, )
                m.save()

        with self.assertRaises(IntegrityError):
            m = CostItemDefaultCosts.objects.create(costitem=alpha, )
            m.save()

            m2 = CostItemDefaultCosts.objects.create(costitem=alpha,)
            m2.save()

    def test_minimum_attributes(self):
        alpha = self.my_model.objects.get(code=self.alpha_code)
        with transaction.atomic():
            with transaction.atomic():
                m = CostItemDefaultCosts.objects.create(costitem=alpha, )
                m.save()

        with self.assertRaises(IntegrityError):
            m = CostItemDefaultCosts.objects.create(costitem=alpha, )
            m.save()

            m2 = CostItemDefaultCosts.objects.create(costitem=alpha,)
            m2.save()


class CostItemDefaultEquationsTestCase(BaseLookupTestCase):
    def setUp(self):
        self.my_model = CostItem
        alpha = {
            'code': self.alpha_code, 'name': self.alpha_name,
            'units': self.units,
            'help_text': self.alpha_name + " Help Test"
        }
        beta = {
            'code': self.beta_code, 'name': self.beta_name,
            'units': self.units,
            'help_text': self.beta_name + " Help Test"
        }

        CostItem.objects.create(**alpha)
        CostItem.objects.create(**beta)


    def test_cost_item_unique(self):
        alpha = CostItem.objects.get(code=self.alpha_code)
        with transaction.atomic():
            with transaction.atomic():
                m = CostItemDefaultEquations.objects.create(costitem=alpha, )
                m.save()

                self.assertEqual(m.o_and_m_pct, 0)

                m.o_and_m_pct = 75
                m.save()
                self.assertEqual(m.o_and_m_pct, 75)

                m.o_and_m_pct = 200
                with self.assertRaises(ValidationError):
                    m.full_clean()

        with transaction.atomic():
            m = CostItemDefaultEquations.objects.create(costitem=alpha, o_and_m_pct=900)
            with self.assertRaises(ValidationError):
                m.full_clean()

        with transaction.atomic():
            # with self.assertRaises(IntegrityError):
            m = CostItemDefaultEquations.objects.get(costitem=alpha,)
            m.o_and_m_pct = 200
            m.save()

        with self.assertRaises(IntegrityError):
            m = CostItemDefaultEquations.objects.create(costitem=alpha, )
            m.save()

            m2 = CostItemDefaultEquations.objects.create(costitem=alpha,)
            m2.save()


class StructureCostItemDefaultFactorsTestCase(BaseLookupTestCase):
    def setUp(self):
        self.my_model = CostItem
        alpha = {
            'code': self.alpha_code, 'name': self.alpha_name,
            'units': self.units,
            'help_text': self.alpha_name + " Help Test"
        }
        beta = {
            'code': self.beta_code, 'name': self.beta_name,
            'units': self.units,
            'help_text': self.beta_name + " Help Test"
        }
        CostItem.objects.create(**alpha)
        CostItem.objects.create(**beta)

        self.my_model = Structures
        alpha_structure = {
            'code': self.alpha_code, 'name': self.alpha_name,
            'classification': 'conventional',
            'units': self.units,
            'units_html': self.units,
            'help_text': self.alpha_name + " Help Test"
        }
        beta_structure = {
            'code': self.beta_code, 'name': self.beta_name,
            'classification': 'conventional',
            'units': self.units,
            'units_html': self.units,
            'help_text': self.beta_name + " Help Test"
        }

        Structures.objects.create(**alpha_structure)
        Structures.objects.create(**beta_structure)

    def test_minimum_attributes(self):
        alpha_cost_item = CostItem.objects.get(code=self.alpha_code)
        alpha_structure = Structures.objects.get(code=self.alpha_code)

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                StructureCostItemDefaultFactors.objects.create()

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                m = StructureCostItemDefaultFactors.objects.create(structure=alpha_structure, )
                m.save()

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                m = StructureCostItemDefaultFactors.objects.create(costitem=alpha_cost_item, )
                m.save()

        with transaction.atomic():
            m = StructureCostItemDefaultFactors.objects.create(structure=alpha_structure, costitem=alpha_cost_item,)
            m.save()

        with self.assertRaises(IntegrityError):
            StructureCostItemDefaultFactors.objects.create(structure=alpha_structure, costitem=alpha_cost_item,)
            StructureCostItemDefaultFactors.objects.create(structure=alpha_structure, costitem=alpha_cost_item,)


class ScenarioTestCase(TestCase):
    def setUp(self):

        user = User.objects.create(
            name='testing',
            email='tester@acme.com',
            password='Abcfff$#$566',
            is_staff=True,
            is_active=True
        )
        Project.objects.create(
            user=user,
            project_title="FOO",
            project_area=1000,
            land_unit_cost=2.40

        )
        Project.objects.create(
            user=user,
            project_title="BAR",
            project_area=1001,
            land_unit_cost=2.50
        )

    def test_scenario_has_minimum_attributes(self):
        foo = Project.objects.get(project_title="FOO")

        with transaction.atomic():
            with self.assertRaises(IntegrityError) as err:
                Scenario.objects.create(scenario_title='SCENARIO FOO', project=foo, )
                Scenario.objects.create(scenario_title='SCENARIO FOO', project=foo, )

            self.assertTrue('duplicate key value' in err.exception.args[0])

        s = Scenario.objects.create(scenario_title='SCENARIO FOO', project=foo,)
        s.full_clean()

        with self.assertRaises(ValidationError) as cm:
            s.scenario_title = ''
            s.full_clean()
        self.assertTrue('scenario_title' in cm.exception.message_dict)

        with self.assertRaises(ValidationError) as cm:
            s.planning_and_design_factor = 'f' * 20
            s.full_clean()
        self.assertTrue('planning_and_design_factor' in cm.exception.message_dict)

        with self.assertRaises(ValidationError) as cm:
            s.nutrient_req_met = 'foobar'
            s.full_clean()
        self.assertTrue('nutrient_req_met' in cm.exception.message_dict)

        with self.assertRaises(ValidationError) as cm:
            s.captures_90pct_storm = 'foobar'
            s.full_clean()
        self.assertTrue('captures_90pct_storm' in cm.exception.message_dict)

        with self.assertRaises(ValidationError) as cm:
            s.meets_peakflow_req = 'foobar'
            s.full_clean()
        self.assertTrue('meets_peakflow_req' in cm.exception.message_dict)

        with self.assertRaises(ValidationError) as cm:
            s.pervious_area = 12.5
            s.full_clean()
        self.assertTrue(s.pervious_area == int(12.5))


class ScenarioCostItemUserCostTestCase(BaseLookupTestCase):
    """
    create a Scenario with 1 structure and 1 CostItem and
    then test creating custom
        ScenarioCostItemUserCosts
        ScenarioStructure
        StructureCostItemUserFactors

    """
    project_title = 'FOO'
    scenario_title = 'SCENARIO FOO'

    def setUp(self):
        self.myStartTime = time.time()
        alpha = {
            'code': self.alpha_code, 'name': self.alpha_name,
            'units': self.units,
            'help_text': self.alpha_name + " Help Test"
        }
        beta = {
            'code': self.beta_code, 'name': self.beta_name,
            'units': self.units,
            'help_text': self.beta_name + " Help Test"
        }
        CostItem.objects.create(**alpha)
        CostItem.objects.create(**beta)

        alpha_structure = {
            'code': self.alpha_code, 'name': self.alpha_name,
            'classification': 'conventional',
            'units': self.units,
            'units_html': self.units,
            'help_text': self.alpha_name + " Help Test"
        }
        beta_structure = {
            'code': self.beta_code, 'name': self.beta_name,
            'classification': 'conventional',
            'units': self.units,
            'units_html': self.units,
            'help_text': self.beta_name + " Help Test"
        }
        Structures.objects.create(**alpha_structure)
        Structures.objects.create(**beta_structure)

        user = User.objects.create(
            name='testing',
            email='tester@acme.com',
            password='Abcfff$#$566',
            is_staff=True,
            is_active=True
        )
        user.save()
        project_foo = Project.objects.create(
            user=user,
            project_title=self.project_title,
            project_area=1000,
            land_unit_cost=2.40

        )
        project_foo.save()
        scenario_foo = Scenario.objects.create(
            project=project_foo,
            scenario_title=self.scenario_title,
        )
        scenario_foo.save()

    def tearDown(self):
        t = time.time() - self.myStartTime
        logger.debug('%s: %.3f' % (self.id(), t))

    def test_scenario_has_minimum_attributes(self):

        costitem = CostItem.objects.get(code=self.alpha_code)
        self.assertIsNotNone(costitem)

        costitem_default_equation = CostItemDefaultEquations.objects.create(
            costitem=costitem,
            equation_tx='=x*area*depth*density*$',
            replacement_life=5,
            o_and_m_pct=20,
        )
        costitem_default_equation.save()
        self.assertIsNotNone(costitem_default_equation)

        structure = Structures.objects.get(code=self.alpha_code)
        self.assertIsNotNone(structure)

        project = Project.objects.get(project_title=self.project_title)
        self.assertIsNotNone(project)

        scenario = Scenario.objects.get(project=project, scenario_title=self.scenario_title)
        self.assertIsNotNone(scenario)

        scenario_cost_item = ScenarioCostItemUserCosts.objects.create(
            scenario=scenario,
            costitem=costitem,
            cost_source = 'user',
            user_input_cost = '1999.99',
            base_year = 2022,
            replacement_life = 15,
            o_and_m_pct = 5,
        )
        scenario_cost_item.save()
        self.assertIsNotNone(scenario_cost_item)

        scenario_structure = ScenarioStructure.objects.create(
            scenario=scenario,
            structure=structure,
            area=1000,
            is_checked=True
        )
        scenario_structure.save()
        self.assertIsNotNone(scenario_structure)

        structure_costitem_user_factors = StructureCostItemUserFactors.objects.create(
            scenario=scenario,
            structure=structure,
            costitem=costitem,

            checked=True,
            a_area=2,
            z_depth=1,
            d_density=1,
            n_number=0,
        )
        structure_costitem_user_factors.save()
        self.assertIsNotNone(structure_costitem_user_factors)




