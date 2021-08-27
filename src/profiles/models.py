from __future__ import unicode_literals
# from django.utils.encoding import python_2_unicode_compatible
import uuid
from django.db import models
from django.conf import settings


class BaseProfile(models.Model):

    USER_TYPE_VALUES = ('standard', 'professional')
    USER_TYPE_TEXTS = ('Standard user – educational purposes only',
                       'Professional user – for use with City of Raleigh design review (requires City approval)')
    USER_TYPE_CHOICES = zip(USER_TYPE_VALUES, USER_TYPE_TEXTS)


    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                primary_key=True)
    slug = models.UUIDField(default=uuid.uuid4, blank=True, editable=False)
    # Add more user profile fields here. Make sure they are nullable
    # or with default values
    user_type = models.CharField('User Type', choices=USER_TYPE_CHOICES, max_length=20, null=True, blank=True)
    favoriteDate = models.DateField('Favorite Date', null=True, blank=True)
    picture = models.ImageField('Profile picture',
                                upload_to='profile_pics/%Y-%m-%d/',
                                null=True,
                                blank=True)
    bio = models.CharField("Short Bio", max_length=200, blank=True, null=True)
    email_verified = models.BooleanField("Email verified", default=False)

    class Meta:
        abstract = True


# @python_2_unicode_compatible
class Profile(BaseProfile):
    def __str__(self):
        return "{}'s profile". format(self.user)
