from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):

    # note 2022-01-27 trying to reduce hits on db
    # https://stackoverflow.com/questions/46854395/prefetch-related-for-authenticated-user/62080682
    def get(self, *args, **kwargs):
        return super().select_related('profile').get(*args, **kwargs)


    def create_user(self, email, password=None, **kwargs):
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, **kwargs):
        user = self.create_user(**kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class AbstractEmailUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), max_length=255, unique=True)

    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user is City staff and can see all Projects and Scenarios for all other users.'))
    is_active = models.BooleanField(_('active'), default=False,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        abstract = True
        ordering = ['email']

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Sends an email to this User."""

        send_mail(subject, message, from_email, [self.email], **kwargs)

AbstractEmailUser._meta.get_field('is_superuser').help_text = 'Designates whether the user is City staff who can access the Admin functions.'
class AbstractNamedUser(AbstractEmailUser):
    name = models.CharField(_('name'), max_length=255)

    #JAB these are added to authtools.
    organization_tx = models.CharField('Affiliation', max_length=100, default=None, blank=True, null=True)
    job_title = models.CharField('Job Title', max_length=100, default=None, blank=True, null=True)
    phone_tx = models.CharField('Phone', max_length=15, default=None, blank=True, null=True)

    REQUIRED_FIELDS = ['name']

    class Meta:
        abstract = True
        ordering = ['name', 'email']

    def __str__(self):
        return '{name} <{email}>'.format(
            name=self.name,
            email=self.email,
        )

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name


class User(AbstractNamedUser):
    class Meta(AbstractNamedUser.Meta):
        swappable = 'AUTH_USER_MODEL'
        verbose_name = _('user')
        verbose_name_plural = _('users')
