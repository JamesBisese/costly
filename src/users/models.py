from django.db import models

from django.contrib.auth.models import AbstractUser, BaseUserManager

from django.utils.translation import ugettext_lazy as _

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    # note 2022-01-27 trying to reduce hits on db
    # https://stackoverflow.com/questions/46854395/prefetch-related-for-authenticated-user/62080682
    def get(self, *args, **kwargs):
        return super().select_related('profile').get(*args, **kwargs)

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    """User model."""

    # username = None
    first_name = None
    last_name = None
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField('Full Name', max_length=100, default=None, blank=True, null=True)
    agency = models.CharField('Organization/Company', max_length=100, default=None, blank=True, null=True)
    phone_tx = models.CharField('Phone', max_length=15, default=None, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()  ## This is the new line in the User model. ##
