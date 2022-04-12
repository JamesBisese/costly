import json
import logging

from django.conf import settings

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger('developer')
logger.setLevel(logging.INFO)


class WebUITest(LiveServerTestCase):

    # address running server
    uri = 'http://127.0.0.1:94'

    admin_user = None
    admin_user_email = 'admin@tetratech.com'
    admin_user_password_tx = 'cost2018'
    staff_user = None
    staff_user_email = 'staff@tetratech.com'
    staff_user_password_tx = 'cost2018'
    non_staff_user = None
    non_staff_user_email = 'user4@tetratech.com'
    non_staff_user_password_tx = 'user4022'

    def setUp(self):
        pass

    def test_zing(self):
        opts = Options()
        opts.add_argument("--window-size=1440,1440")
        selenium = webdriver.Chrome(options=opts)
        # Choose your url to visit
        selenium.get(self.uri + '/login')

        version_info = selenium.find_element(By.ID, 'version_information')
        logger.debug('version_info: {}'.format(version_info.text))

        # now login as administrator
        box = selenium.find_element(By.ID, 'id_acknowledge_terms')
        selenium.execute_script("arguments[0].click()", box)
        selenium.find_element(By.ID, 'id_username').send_keys(self.admin_user_email)
        selenium.find_element(By.ID, 'id_password').send_keys(self.admin_user_password_tx)
        selenium.find_element(By.ID, 'submit-id-sign_in').click()

        selenium.implicitly_wait(2)
        #
        # pre = selenium.find_element(By.TAG_NAME, "pre").text
        # users_data = json.loads(pre)
        # print(json.dumps(users_data, indent=2))
        #
        selenium.get(self.uri + '/api/projects/?format=datatables')

        selenium.implicitly_wait(2)

        pre = selenium.find_element(By.TAG_NAME, "pre").text
        project_data = json.loads(pre)

        # TODO figure out what to assert
        for p in project_data['data']:
            print(p['id'])
        # print(json.dumps(project_data, indent=2))

    def test_nav_bar(self):
        opts = Options()
        opts.add_argument("--window-size=1440,1440")
        selenium = webdriver.Chrome(options=opts)
        # Choose your url to visit
        selenium.get(self.uri + '/')

        version_info = selenium.find_element(By.ID, 'version_information')
        logger.debug('version_info: {}'.format(version_info.text))

        self.assertEqual(version_info.text, settings.VERSION_INFORMATION)

        nav_links = selenium.find_elements(By.CLASS_NAME, 'nav-link')
        links = set()
        for link in nav_links:
            logger.debug("ANON {} '{}'".format(link.get_attribute('href'), link.get_attribute('text')))
            links.add(link.get_attribute('text'))

        # removed on COR request in Feb 2022
        # self.assertTrue('WHY IS RALEIGH INVESTING IN GSI' in links)
        self.assertTrue('HOW IS THE GSI COST TOOL SETUP' in links)
        self.assertFalse('REFERENCES' in links)
        self.assertFalse('AUDIT' in links)
        self.assertFalse('PROJECTS' in links)
        self.assertTrue('Log in' in links)
        self.assertTrue('Create New Account' in links)

        # now login as administrator

        selenium.get(self.uri + '/login')

        box = selenium.find_element(By.ID, 'id_acknowledge_terms')
        selenium.execute_script("arguments[0].click()", box)
        selenium.find_element(By.ID, 'id_username').send_keys(self.admin_user_email)
        selenium.find_element(By.ID, 'id_password').send_keys(self.admin_user_password_tx)
        selenium.find_element(By.ID, 'submit-id-sign_in').click()

        nav_links = selenium.find_elements(By.CLASS_NAME, 'nav-link')
        links = set()
        for link in nav_links:
            logger.debug("ADMIN {} '{}'".format(link.get_attribute('href'), link.get_attribute('text')))
            links.add(link.get_attribute('text'))

        self.assertTrue('INSTRUCTIONS' in links)
        self.assertTrue('REFERENCES' in links)
        self.assertTrue('AUDIT' in links)
        self.assertTrue('PROJECTS' in links)
        self.assertTrue('Admin Page' in links)

        for link in nav_links:
            if 'SUBMENU' in link.get_attribute('href'):
                link.click()
                break

        for link in nav_links:
            if link.get_attribute('text') == 'Logout':
                link.click()
                break

        selenium.implicitly_wait(2)

        nav_links = selenium.find_elements(By.CLASS_NAME, 'nav-link')
        links = set()
        for link in nav_links:
            # print("ANON2 {} '{}'".format(link.get_attribute('href'), link.get_attribute('text')))
            links.add(link.get_attribute('text'))

        self.assertTrue('REFERENCES' not in links)
        self.assertTrue('AUDIT' not in links)
        self.assertTrue('PROJECTS' not in links)
        self.assertTrue('Log in' in links)

        # now login as STAFF

        nav_links = selenium.find_elements(By.CLASS_NAME, 'nav-link')
        for link in nav_links:
            if link.get_attribute('text') == 'Log in':
                link.click()
                break

        box = selenium.find_element(By.ID, 'id_acknowledge_terms')
        selenium.execute_script("arguments[0].click()", box)
        selenium.find_element(By.ID, 'id_username').send_keys(self.staff_user_email)
        selenium.find_element(By.ID, 'id_password').send_keys(self.staff_user_password_tx)
        selenium.find_element(By.ID, 'submit-id-sign_in').click()

        nav_links = selenium.find_elements(By.CLASS_NAME, 'nav-link')
        links = set()
        for link in nav_links:
            logger.debug("STAFF {} '{}'".format(link.get_attribute('href'), link.get_attribute('text')))
            links.add(link.get_attribute('text'))

        self.assertTrue('INSTRUCTIONS' in links)
        self.assertTrue('REFERENCES' in links)
        self.assertTrue('AUDIT' in links)
        self.assertTrue('PROJECTS' in links)
        self.assertFalse('Admin Page' in links)

        for link in nav_links:
            if 'SUBMENU' in link.get_attribute('href'):
                link.click()
                break

        for link in nav_links:
            if link.get_attribute('text') == 'Logout':
                link.click()
                break

        selenium.implicitly_wait(2)

        nav_links = selenium.find_elements(By.CLASS_NAME, 'nav-link')
        links = set()
        for link in nav_links:
            links.add(link.get_attribute('text'))

        self.assertFalse('REFERENCES' in links)
        self.assertFalse('AUDIT' in links)
        self.assertFalse('PROJECTS' in links)

        # now login as NON-STAFF

        nav_links = selenium.find_elements(By.CLASS_NAME, 'nav-link')
        for link in nav_links:
            if link.get_attribute('text') == 'Log in':
                link.click()
                break

        box = selenium.find_element(By.ID, 'id_acknowledge_terms')
        selenium.execute_script("arguments[0].click()", box)
        selenium.find_element(By.ID, 'id_username').send_keys(self.non_staff_user_email)
        selenium.find_element(By.ID, 'id_password').send_keys(self.non_staff_user_password_tx)
        selenium.find_element(By.ID, 'submit-id-sign_in').click()

        nav_links = selenium.find_elements(By.CLASS_NAME, 'nav-link')
        links = set()
        for link in nav_links:
            logger.debug("NONSTAFF {} '{}'".format(link.get_attribute('href'), link.get_attribute('text')))
            links.add(link.get_attribute('text'))

        self.assertTrue('INSTRUCTIONS' in links)
        self.assertTrue('REFERENCES' in links)
        self.assertFalse('AUDIT' in links)
        self.assertTrue('PROJECTS' in links)
        self.assertFalse('Create New Account' in links)

        for link in nav_links:
            if 'SUBMENU' in link.get_attribute('href'):
                link.click()
                break

        for link in nav_links:
            if link.get_attribute('text') == 'Logout':
                link.click()
                break

        selenium.implicitly_wait(2)

        nav_links = selenium.find_elements(By.CLASS_NAME, 'nav-link')
        links = set()
        for link in nav_links:
            links.add(link.get_attribute('text'))

        self.assertFalse('REFERENCES' in links)
        self.assertFalse('AUDIT' in links)
        self.assertFalse('PROJECTS' in links)
