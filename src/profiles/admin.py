from __future__ import unicode_literals
from django.contrib import admin
from authtools.admin import NamedUserAdmin
from .models import Profile
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.html import format_html

User = get_user_model()


class UserProfileInline(admin.StackedInline):
    model = Profile
    exclude = ('favoriteDate', 'picture',)

class NewUserAdmin(NamedUserAdmin):
    """
      this defines the page /admin/authtools/user/

    """
    inlines = [UserProfileInline]

    def user_type(self, obj):
        return "%s" % obj.profile.user_type or 'N/A'
    user_type.short_description = 'User Type'

    list_display = ('name', 'organization_tx', 'job_title', 'user_type', 'email', 'permalink',
                    'is_active', 'is_superuser', 'is_staff', 'last_login', 'date_joined')
    list_display_links = ('name',)
    # hint: search related fields using double-underscore '__'
    search_fields = ('email', 'name', 'organization_tx','job_title', 'profile__user_type')

    # 'View on site' didn't work since the original User model needs to
    # have get_absolute_url defined. So showing on the list display
    # was a workaround.
    def permalink(self, obj):
        url = reverse("profiles:show",
                      kwargs={"slug": obj.profile.slug})
        # Unicode hex b6 is the Pilcrow sign
        return format_html('<a href="{}">{}</a>'.format(url, '\xb6'))


admin.site.unregister(User)
admin.site.register(User, NewUserAdmin)
