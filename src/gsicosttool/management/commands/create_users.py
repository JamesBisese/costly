import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission


class Command(BaseCommand):
    help = 'Create demonstration application users'

    def handle(self, *args, **kwargs):

        user_model = get_user_model()

        user_list = None
        if len(settings.USER_LIST) > 0:
            user_list = json.loads(settings.USER_LIST)

        is_staff_permissions = [
            'Can add scenario',
            'Can change scenario',
            'Can delete scenario',
            'Can add project',
            'Can change project',
            'Can delete project',
        ]

        is_user_permissions = [
            'Can add scenario',
            'Can change scenario',
            'Can delete scenario',
            'Can add project',
            'Can change project',
            'Can delete project',
        ]

        for user in user_list:
            user_atts = user_list[user]

            if not user_model.objects.filter(email=user_atts['email']).exists():
                u = user_model.objects.create_user(
                        email=user_atts['email'],
                        password=user_atts['password'],
                        name=user_atts['email'][0:user_atts['email'].index('@')],
                        is_active=True,
                        is_staff=user_atts['is_staff'] if 'is_staff' in user_atts else False,
                        is_superuser=user_atts['is_superuser'] if 'is_superuser' in user_atts else False,
                       )

                if 'is_staff' in user_atts and user_atts['is_staff'] is True:
                    for perm in is_staff_permissions:
                        permission = Permission.objects.get(name=perm)
                        u.user_permissions.add(permission)
                elif not ('is_staff' in user_atts or 'is_superuser' in user_atts):
                    for perm in is_user_permissions:
                        permission = Permission.objects.get(name=perm)
                        u.user_permissions.add(permission)

                print('User "{}" created'.format(user_atts['email']))
            else:
                print('User "{}" exists already, not created'.format(user_atts['email']))
