import json
import logging

from django.conf import settings

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger('developer')
logger.setLevel(logging.INFO)


# Create your tests here.
class WebUITest(LiveServerTestCase):

    def setUp(self):
        pass

    def test_zing(self):
        opts = Options()
        opts.add_argument("--window-size=1440,1440")
        selenium = webdriver.Chrome(options=opts)
        # Choose your url to visit
        selenium.get('http://127.0.0.1:94/login')

        version_info = selenium.find_element(By.ID, 'version_information')
        logger.debug('version_info: {}'.format(version_info.text))

        # now login as administrator
        selenium.find_element(By.ID, 'id_username').send_keys('admin@tetratech.com')
        selenium.find_element(By.ID, 'id_password').send_keys('cost2018')
        selenium.find_element(By.ID, 'submit-id-sign_in').click()

        # selenium.get('http://127.0.0.1:94/api/users/?format=datatables')
        #
        selenium.implicitly_wait(2)
        #
        # pre = selenium.find_element(By.TAG_NAME, "pre").text
        # users_data = json.loads(pre)
        # print(json.dumps(users_data, indent=2))
        #
        selenium.get('http://127.0.0.1:94/api/projects/?format=datatables')

        selenium.implicitly_wait(2)

        pre = selenium.find_element(By.TAG_NAME, "pre").text
        project_data = json.loads(pre)

        for p in project_data['data']:
            # v = project_data['data'][p]
            print(p['id'])

        print(json.dumps(project_data, indent=2))


    def test_nav_bar(self):
        opts = Options()
        opts.add_argument("--window-size=1440,1440")
        selenium = webdriver.Chrome(options=opts)
        # Choose your url to visit
        selenium.get('http://127.0.0.1:94/')

        version_info = selenium.find_element(By.ID, 'version_information')
        logger.debug('version_info: {}'.format(version_info.text))

        self.assertEqual(version_info.text, settings.VERSION_INFORMATION)

        nav_links = selenium.find_elements(By.CLASS_NAME, 'nav-link')
        links = set()
        for link in nav_links:
            logger.debug("ANON {} '{}'".format(link.get_attribute('href'), link.get_attribute('text')))
            links.add(link.get_attribute('text'))

        self.assertTrue('WHY IS RALEIGH INVESTING IN GSI' in links)
        self.assertTrue('HOW IS THE GSI COST TOOL SETUP' in links)
        self.assertFalse('REFERENCES' in links)
        self.assertFalse('AUDIT' in links)
        self.assertFalse('PROJECTS' in links)
        self.assertTrue('Log in' in links)
        self.assertTrue('Create New Account' in links)

        # now login as administrator

        selenium.get('http://127.0.0.1:94/login')

        selenium.find_element(By.ID, 'id_username').send_keys('admin@tetratech.com')
        selenium.find_element(By.ID, 'id_password').send_keys('cost2018')
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

        selenium.find_element(By.ID, 'id_username').send_keys('staff@tetratech.com')
        selenium.find_element(By.ID, 'id_password').send_keys('cost2018')
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

        selenium.find_element(By.ID, 'id_username').send_keys('user4@tetratech.com')
        selenium.find_element(By.ID, 'id_password').send_keys('user4022')
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
