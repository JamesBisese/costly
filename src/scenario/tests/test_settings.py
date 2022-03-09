import logging
import json
from django.conf import settings
from django.test import TestCase, Client

from authtools.models import User

logger = logging.getLogger('developer')
logger.setLevel(logging.DEBUG)


class SettingsTests(TestCase):
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

        self.admin_user.save()
        self.staff_user.save()
        self.non_staff_user.save()

    def test_settings(self):
        """
        Ensure that the production settings example has everything necessary for using with settings.production
        """
        self.client = Client()

        logged_in = self.client.login(email=self.admin_user.email, password=self.admin_user_password_tx)
        self.assertTrue(logged_in)

        # logger.debug('DEBUG=={}'.format(settings.DEBUG))  # this is set by test, so you can't see the value here.
        logger.debug('ENV_FILE=={}'.format(settings.ENV_FILE))
        logger.debug('VERSION_INFORMATION=={}'.format(settings.VERSION_INFORMATION))
        logger.debug('DATABASES==\n{}'.format(json.dumps(settings.DATABASES, indent=2)))
