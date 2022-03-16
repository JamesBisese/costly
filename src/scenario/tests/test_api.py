from django.urls import reverse
from rest_framework import serializers
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import Client

from authtools.models import User
from scenario.models import CostItem, Project, Structures

from scenario.serializers import UserSerializer, ProjectSerializer, \
    ScenarioListSerializer, ScenarioSerializer, ScenarioAuditSerializer, \
    StructureSerializer, CostItemSerializer, CostItemDefaultCostSerializer, \
    ScenarioCostItemUserCostsSerializer, CostItemDefaultEquationsSerializer, \
    StructureCostItemDefaultFactorsSerializer, StructureCostItemUserFactorsSerializer

class AccountTests(APITestCase):
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

    def test_create_costitem(self):
        """
        Ensure admin and staff can create a costitem object, but not non-staff
        """
        self.client = Client()

        logged_in = self.client.login(email=self.admin_user.email, password=self.admin_user_password_tx)
        self.assertTrue(logged_in)

        url = reverse('scenario:costitem-list')
        data = {'code': 'costly',
                'name': 'DabApps',
                'units': 'SF',
                'help_text': 'boo'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CostItem.objects.count(), 1)
        self.assertEqual(CostItem.objects.get().code, data['code'])
        self.assertEqual(CostItem.objects.get().name, data['name'])
        self.assertEqual(CostItem.objects.get().units, data['units'])
        self.assertEqual(CostItem.objects.get().help_text, data['help_text'])

        # delete the same object
        url = reverse('scenario:costitem-detail', args=[CostItem.objects.get().id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CostItem.objects.count(), 0)

        # logout the admin user
        self.client.logout()

        logged_in = self.client.login(email=self.non_staff_user.email, password=self.non_staff_user_password_tx)
        self.assertTrue(logged_in)

        url = reverse('scenario:costitem-list')
        data = {'code': 'costly',
                'name': 'DabApps',
                'units': 'SF',
                'help_text': 'boo'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(CostItem.objects.count(), 0)

        self.client.logout()

        logged_in = self.client.login(email=self.staff_user.email, password=self.staff_user_password_tx)
        self.assertTrue(logged_in)

        url = reverse('scenario:costitem-list')
        data = {'code': 'costly',
                'name': 'DabApps',
                'units': 'SF',
                'help_text': 'boo'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CostItem.objects.count(), 1)

        # delete the same object
        url = reverse('scenario:costitem-detail', args=[CostItem.objects.get().id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CostItem.objects.count(), 0)

        # now recreate it, and see if non-staff can delete it
        url = reverse('scenario:costitem-list')
        data = {'code': 'costly',
                'name': 'DabApps',
                'units': 'SF',
                'help_text': 'boo'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CostItem.objects.count(), 1)

        self.client.logout()

        logged_in = self.client.login(email=self.non_staff_user.email, password=self.non_staff_user_password_tx)
        self.assertTrue(logged_in)

        # try to delete the same object and it will not work
        url = reverse('scenario:costitem-detail', args=[CostItem.objects.get().id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(CostItem.objects.count(), 1)

        self.client.logout()

        logged_in = self.client.login(email=self.staff_user.email, password=self.staff_user_password_tx)
        self.assertTrue(logged_in)

        # delete the same object as staff
        url = reverse('scenario:costitem-detail', args=[CostItem.objects.get().id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CostItem.objects.count(), 0)

    def test_create_costitem_default_cost(self):
        """
        NOTE: I am going to do this in test_models first

        Ensure admin and staff can create a costitem object, but not non-staff
        """
        self.client = Client()

        logged_in = self.client.login(email=self.admin_user.email, password=self.admin_user_password_tx)
        self.assertTrue(logged_in)

        url = reverse('scenario:costitem-list')
        data = {'code': 'costly',
                'name': 'DabApps',
                'units': 'SF',
                'help_text': 'boo'}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CostItem.objects.count(), 1)
        self.assertEqual(CostItem.objects.get().code, data['code'])
        self.assertEqual(CostItem.objects.get().name, data['name'])
        self.assertEqual(CostItem.objects.get().units, data['units'])
        self.assertEqual(CostItem.objects.get().help_text, data['help_text'])

        costitem = CostItem.objects.get()
        # create the


        # delete the same object
        url = reverse('scenario:costitem-detail', args=[CostItem.objects.get().id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CostItem.objects.count(), 0)

        # logout the admin user
        self.client.logout()

    def test_create_structure(self):
        """
        Ensure admin and staff can create a costitem object, but not non-staff
        """
        self.client = Client()

        logged_in = self.client.login(email=self.admin_user.email, password=self.admin_user_password_tx)
        self.assertTrue(logged_in)

        url = reverse('scenario:structures-list')
        data = {'code': 'door',
                'name': 'Doorway structure',
                'classification': 'conventional',
                'units': 'SF',
                'units_html': 'sf',
                'help_text': 'boo'}

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Structures.objects.count(), 1)
        self.assertEqual(Structures.objects.get().code, data['code'])
        self.assertEqual(Structures.objects.get().name, data['name'])
        self.assertEqual(Structures.objects.get().units, data['units'])
        self.assertEqual(Structures.objects.get().help_text, data['help_text'])

        # delete the same object
        url = reverse('scenario:structures-detail', args=[Structures.objects.get().id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Structures.objects.count(), 0)

        # logout the non_staff_user
        self.client.logout()

        logged_in = self.client.login(email=self.non_staff_user.email, password=self.non_staff_user_password_tx)
        self.assertTrue(logged_in)

        url = reverse('scenario:structures-list')

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Structures.objects.count(), 0)

        self.client.logout()

        logged_in = self.client.login(email=self.staff_user.email, password=self.staff_user_password_tx)
        self.assertTrue(logged_in)

        url = reverse('scenario:structures-list')

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Structures.objects.count(), 1)

        # delete the same object
        url = reverse('scenario:structures-detail', args=[Structures.objects.get().id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Structures.objects.count(), 0)

        # now recreate it, and see if non-staff can delete it
        url = reverse('scenario:structures-list')

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Structures.objects.count(), 1)

        self.client.logout()

        logged_in = self.client.login(email=self.non_staff_user.email, password=self.non_staff_user_password_tx)
        self.assertTrue(logged_in)

        # try to delete the same object and it will not work
        url = reverse('scenario:structures-detail', args=[Structures.objects.get().id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(Structures.objects.count(), 1)

        self.client.logout()

        logged_in = self.client.login(email=self.staff_user.email, password=self.staff_user_password_tx)
        self.assertTrue(logged_in)

        # delete the same object as staff
        url = reverse('scenario:structures-detail', args=[Structures.objects.get().id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Structures.objects.count(), 0)
