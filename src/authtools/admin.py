
import copy

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from .models import User
from .forms import UserCreationForm, AdminUserChangeForm


def custom_titled_filter(title):
    """
    this allows overriding the name shown in the right-side FILTER panel

    :param title:
    :return:
    """
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper


USERNAME_FIELD = get_user_model().USERNAME_FIELD

REQUIRED_FIELDS = (USERNAME_FIELD,) + tuple(get_user_model().REQUIRED_FIELDS)

BASE_FIELDS = (None, {
    'fields': REQUIRED_FIELDS + ('password', 'organization_tx', 'phone_tx', 'job_title',),
})

SIMPLE_PERMISSION_FIELDS = (_('Permissions'), {
    'fields': ('is_active', 'is_staff', 'is_superuser',),
})

ADVANCED_PERMISSION_FIELDS = copy.deepcopy(SIMPLE_PERMISSION_FIELDS)
ADVANCED_PERMISSION_FIELDS[1]['fields'] += ('user_permissions',)

DATE_FIELDS = (_('Important dates'), {
    'fields': ('last_login', 'date_joined',),
})


class StrippedUserAdmin(DjangoUserAdmin):
    # The forms to add and change user instances
    add_form_template = None
    add_form = UserCreationForm
    form = AdminUserChangeForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('is_active', USERNAME_FIELD, 'is_superuser', 'is_staff',)
    list_display_links = (USERNAME_FIELD,)
    list_filter = (
        'profile__user_type',
        ('is_active', custom_titled_filter('Active/Not Active')),
        ('is_superuser', custom_titled_filter('Is SuperUser (Yes/No)')),
        ('is_staff', custom_titled_filter('Is Staff (Yes/No)')),
    )
    fieldsets = (
        BASE_FIELDS,
        SIMPLE_PERMISSION_FIELDS,
    )
    add_fieldsets = (
        (None, {
            'fields': REQUIRED_FIELDS + (
                'password1',
                'password2',
            ),
        }),
    )
    search_fields = (USERNAME_FIELD,)
    ordering = None
    filter_horizontal = tuple()
    readonly_fields = ('last_login', 'date_joined')


class StrippedNamedUserAdmin(StrippedUserAdmin):
    """
    this class gets overridden in the profiles/admin.py file

    """
    pass


class UserAdmin(StrippedUserAdmin):
    fieldsets = (
        BASE_FIELDS,
        ADVANCED_PERMISSION_FIELDS,
        DATE_FIELDS,
    )
    filter_horizontal = ('groups', 'user_permissions',)


class NamedUserAdmin(UserAdmin, StrippedNamedUserAdmin):
    pass


# If the model has been swapped, this is basically a noop.
admin.site.register(User, NamedUserAdmin)
