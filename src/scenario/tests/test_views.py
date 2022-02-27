import logging
import json

from django.test import TestCase
from django.urls import reverse
from django.test import Client

logger = logging.getLogger('developer')
logger.setLevel(logging.DEBUG)

from authtools.models import User

from scenario.models import Project, Scenario, ArealFeatureLookup, Structures, \
    CostItem, \
    CostItemDefaultCosts, CostItemDefaultEquations, \
    StructureCostItemDefaultFactors, \
    ScenarioCostItemUserCosts, \
    StructureCostItemUserFactors, \
    ScenarioArealFeature, ScenarioStructure

class ContextListViewTest(TestCase):
    admin_user = None
    admin_user_password_tx = 'Abcfff$#$566ADMIN'
    staff_user = None
    staff_user_password_tx = 'Abcfff$#$566STAFF'
    non_staff_user = None
    non_staff_user_password_tx = 'Abcfff$#$566NONSTAFF'

    project1 = None

    anon_client = None
    admin_user_client = None
    staff_user_client = None
    non_staff_user_client = None

    def setUp(self):
        self.admin_user = User.objects.create_user(
            name='Admin User',
            email='admin_user@acme.com',
            password=self.admin_user_password_tx,
            is_superuser=True,
            is_staff=True,
            is_active=True
        )
        self.staff_user = User.objects.create_user(
            name='Staff User',
            email='staff_user@acme.com',
            password=self.staff_user_password_tx,
            is_staff=True,
            is_active=True
        )
        self.non_staff_user = User.objects.create_user(
            name='Non Staff User',
            email='non_staff_user@acme.com',
            password=self.non_staff_user_password_tx,
            is_staff=False,
            is_active=True
        )

        self.staff_user_project = Project.objects.create(
            user=self.staff_user,
            project_title="FOO",
            project_area=1000,
            land_unit_cost=2.40
        )
        self.admin_user.save()
        self.staff_user.save()
        self.non_staff_user.save()

        self.staff_user_project.save()

    def test_for_login_restriction_permission_and_template(self):
        # Create Client
        self.anon_client = Client()

        # Try to call the Restricted View as Anonymous
        # Check for Login Prompt Redirection
        response = self.anon_client.get(reverse('scenario:index'))
        self.assertRedirects(response, '/login/?next=/project/')

        response = self.anon_client.get(reverse('scenario:project_delete', args=[self.staff_user_project.pk]))
        self.assertRedirects(response, '/login/?next=' + reverse('scenario:project_delete', args=[self.staff_user_project.pk]))

        response = self.anon_client.get(reverse('scenario:scenario_index'))
        self.assertRedirects(response, '/login/?next=' + reverse('scenario:scenario_index'))

        response = self.anon_client.get(reverse('scenario:scenario_delete', args=[self.staff_user_project.pk]))
        self.assertRedirects(response, '/login/?next=' + reverse('scenario:scenario_delete', args=[self.staff_user_project.pk]))

        # Try to call the Restricted View as
        self.admin_user_client = Client()
        self.staff_user_client = Client()
        self.non_staff_user_client = Client()

        # we don't use username for login.  only email
        logged_in = self.staff_user_client.login(username=self.staff_user.name, password=self.staff_user_password_tx)
        self.assertFalse(logged_in)

        logged_in = self.staff_user_client.login(email=self.staff_user.email, password=self.staff_user_password_tx)
        self.assertTrue(logged_in)

        logged_in = self.staff_user_client.login(email=self.staff_user.email, password=self.staff_user_password_tx + 'FOOBAR')
        self.assertFalse(logged_in)

        logged_in = self.admin_user_client.login(email=self.admin_user.email, password=self.admin_user_password_tx)
        self.assertTrue(logged_in)

        logged_in = self.non_staff_user_client.login(email=self.non_staff_user.email, password=self.non_staff_user_password_tx)
        self.assertTrue(logged_in)

        # Test restrictions. Test the HTML page and the API connected to that page

        # audit pages

        response = self.anon_client.get(reverse('scenario:audit_scenarios'))
        self.assertRedirects(response, '/admin/login/?next=' + reverse('scenario:audit_scenarios'), status_code=302, fetch_redirect_response=False)

        response = self.non_staff_user_client.get(reverse('scenario:audit_scenarios'))
        self.assertRedirects(response, '/admin/login/?next=' + reverse('scenario:audit_scenarios'), fetch_redirect_response=False)

        response = self.staff_user_client.get(reverse('scenario:audit_scenarios'))
        self.assertEqual(response.status_code, 200)

        # Project List

        response = self.anon_client.get(reverse('scenario:project_index'))
        self.assertRedirects(response, '/login/?next=' + reverse('scenario:project_index'),
                             status_code=302, fetch_redirect_response=False)

        response = self.non_staff_user_client.get(reverse('scenario:project_index'))
        self.assertEqual(response.status_code, 200)

        response = self.staff_user_client.get(reverse('scenario:project_index'))
        self.assertEqual(response.status_code, 200)

        # Edit Project

        response = self.anon_client.get(reverse('scenario:project_update', args=[self.staff_user_project.pk]))
        self.assertRedirects(response, '/login/?next=' + reverse('scenario:project_update', args=[self.staff_user_project.pk]),
                             status_code=302, fetch_redirect_response=False)

        response = self.non_staff_user_client.get(reverse('scenario:project_update', args=[self.staff_user_project.pk]))
        self.assertEqual(response.status_code, 404)

        response = self.staff_user_client.get(reverse('scenario:project_update', args=[self.staff_user_project.pk]))
        self.assertEqual(response.status_code, 200)

        # Scenario CREATE

        response = self.anon_client.get(reverse('scenario:project_scenario_create', args=[self.staff_user_project.pk]))
        self.assertRedirects(response, '/login/?next=' + reverse('scenario:project_scenario_create', args=[self.staff_user_project.pk]),
                             status_code=302, fetch_redirect_response=False)

        response = self.non_staff_user_client.get(reverse('scenario:project_scenario_create', args=[self.staff_user_project.pk]))
        self.assertEqual(response.status_code, 404)

        response = self.staff_user_client.get(reverse('scenario:project_scenario_create', args=[self.staff_user_project.pk]))
        self.assertEqual(response.status_code, 200)

        # now try and create a valid scenario for this project

        scenario_title = 'TESTING FOOBAR'
        response = self.staff_user_client.post(reverse('scenario:project_scenario_create', args=[self.staff_user_project.pk]),
                                                       { 'project_id': self.staff_user_project.pk,
                                                         'scenario_title': scenario_title}
                                                       )
        self.assertEqual(response.status_code, 200)

        response = self.staff_user_client.get("/api/scenario_list/?project={}".format(self.staff_user_project.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(scenario_title, response.data['results'][0]['scenario_title'])
        # same thing using reverse
        # name = 'scenario:scenariolist-list'
        # reverse_name = reverse(name, args=[self.staff_user_project.pk])
        # logger.debug('staff_user_client test for %s: %s' % (name, reverse_name))
        # response = self.staff_user_client.get(reverse_name)
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(scenario_title, response.data['results'][0]['scenario_title'])

        # and test that datatables format works too
        response = self.staff_user_client.get("/api/scenario_list/?project={}&format=datatables".format(self.staff_user_project.pk))
        self.assertEqual(response.status_code, 200)

        #TODO this changed from response.data[0] to response.data['data'][0] and i don't know when or why
        self.assertEqual(response.data['data'][0]['scenario_title'], scenario_title)

        # and make sure that non-authorized users can't get to the data
        response = self.non_staff_user_client.get("/api/scenario_list/?project={}&format=datatables".format(self.staff_user_project.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), 0)
        self.assertEqual(json.loads(response.content)['recordsTotal'], 0)

        scenario_title2 = 'TESTING FOOBAR NUMBER 2'
        response = self.staff_user_client.post(reverse('scenario:project_scenario_create', args=[self.staff_user_project.pk]),
                                                       { 'project_id': self.staff_user_project.pk,
                                                         'scenario_title': scenario_title2}
                                                       )
        self.assertEqual(response.status_code, 200)

        response = self.staff_user_client.get("/api/scenario_list/?project={}".format(self.staff_user_project.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)


    def test_for_anon_restriction(self):
        """
        make sure that all the APIs require that the user is logged in.
        they should be protected because they have mixin LoginRequiredMixin
        """
        self.anon_client = Client()

        for name in ['scenario:user-list',
                     'scenario:projects-list',
                     'scenario:scenario-list',
                     'scenario:scenariolist-list',
                     'scenario:scenarioaudit-list',
                     'scenario:costitem-list',
                     'scenario:structures-list',
                     'scenario:costitemdefaultcosts-list',
                     'scenario:costitemdefaultequations-list',
                     'scenario:structurecostitemdefaultfactors-list',
                     'scenario:scenariocostitemusercosts-list',
                     'scenario:structurecostitemuserfactors-list',
                     ]:

            reverse_name = reverse(name)
            # logger.debug('anon test for %s: %s' % (name, reverse_name))

            response = self.anon_client.get(reverse_name)
            self.assertRedirects(response, '/login/?next=' + reverse_name,
                                 status_code=302, fetch_redirect_response=False)


    def test_for_login_restriction_non_staff(self):
        """
        make sure that all the APIs require that the user is logged in.
        they should be available
        """
        self.non_staff_user_client = Client()
        logged_in = self.non_staff_user_client.login(email=self.non_staff_user.email,
                                                     password=self.non_staff_user_password_tx)
        self.assertTrue(logged_in)

        for name in [
                     'scenario:costitem-list',
                     'scenario:structures-list',
                     'scenario:costitemdefaultcosts-list',
                     'scenario:costitemdefaultequations-list',
                     'scenario:structurecostitemdefaultfactors-list',
                     ]:

            reverse_name = reverse(name)
            # logger.debug('anon test for %s: %s' % (name, reverse_name))

            response = self.non_staff_user_client.get(reverse_name)
            self.assertEqual(response.status_code, 200)

        """ these return 200, but only with the users own data"""
        for name in ['scenario:user-list',
                     'scenario:projects-list',
                     'scenario:scenario-list',
                     'scenario:scenariolist-list',
                     'scenario:scenarioaudit-list',
                     # 'scenario:costitem-list',
                     # 'scenario:structures-list',
                     # 'scenario:costitemdefaultcosts-list',
                     # 'scenario:costitemdefaultequations-list',
                     # 'scenario:structurecostitemdefaultfactors-list',
                     'scenario:scenariocostitemusercosts-list',
                     'scenario:structurecostitemuserfactors-list',
                     ]:

            reverse_name = reverse(name)
            # logger.debug('anon test for %s: %s' % (name, reverse_name))

            response = self.non_staff_user_client.get(reverse_name)
            self.assertEqual(response.status_code, 200)

            # self.assertRedirects(response, '/login/?next=' + reverse_name,
            #                      status_code=302, fetch_redirect_response=False)

