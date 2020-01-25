from django.test import TestCase
from django.test.client import Client

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()

# store the password to login later
email = 'myemail@test.com'
admin_email = 'myadminemail@test.com'
password = 'mypassword'

class CreateUserTestCase(TestCase):
    def test_create_user(self):
        """Something should happen"""
        ...
        my_user= User.objects.create_user(email=email, password=password)

        my_admin= User.objects.create_superuser(email=admin_email, password=password)

        self.assertIsNotNone(my_user.profile)

        c = Client()

        # You'll need to log him in before you can send requests through the client
        c.login(email=email, password=password)

        # tests go here

        # User.objects.filter(email='myemail@test.com').delete()
        # User.objects.filter(id=my_user.id).delete()
        # User.objects.filter(id=my_admin.id).delete()