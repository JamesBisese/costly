# pages/tests.py
from django.http import HttpRequest
from django.test import SimpleTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.test import Client
# from . import views
import json
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

class NewVisitorTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        staging_server = os.environ.get('STAGING_SERVER')
        if staging_server:
            self.live_server_url = 'http://' + staging_server

# class HomePageTests(SimpleTestCase):
#     admin_email = 'admin@tetratech.com'
#     admin_user_password_tx = 'cost2021'
#
#     def test_home_page_status_code(self):
#         response = self.client.get('/')
#         self.assertEquals(response.status_code, 200)
#
#     def test_view_url_by_name(self):
#         response = self.client.get(reverse('home'))
#         self.assertEquals(response.status_code, 200)
#
#     def test_view_uses_correct_template(self):
#         response = self.client.get(reverse('home'))
#         self.assertEquals(response.status_code, 200)
#         self.assertTemplateUsed(response, 'gsicosttool/home.html')
#
#     def test_home_page_contains_correct_html(self):
#         response = self.client.get('/')
#         self.assertContains(response, 'Welcome to the Raleigh GSI Cost Tool!')
#
#     def test_home_page_does_not_contain_incorrect_html(self):
#         response = self.client.get('/')
#         self.assertNotContains(
#             response, 'Hi there! I should not be on the page.')
#
#     def test_create_account(self):
#         self.admin_user_client = Client()
#
#         logged_in = self.admin_user_client.login(email=self.admin_email, password=self.admin_user_password_tx)
#         self.assertTrue(logged_in)
