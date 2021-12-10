from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

"""
    NOTE: This is not used. The edit form for GSI Cost Tool Administration is in 
    C:\inetpub\wwwdjango\gsicosttool\src\authtools\admin.py
    
"""

# CustomUser = get_user_model()
#
# class CustomUserAdminFOOBAR(UserAdmin):
#     """Define admin model for custom User model with no email field."""
#
#     fieldsets = (
#         (None, {'fields': ('email', 'password')}),
#         (_('Personal info'), {'fields': ('agency', 'phone_tx', 'username')}),
#         (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
#                                        'groups', 'user_permissions')}),
#         (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
#     )
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'password1', 'password2'),
#         }),
#     )
#     list_display = ('email', 'username', 'is_staff')
#     search_fields = ('email', 'username')
#     ordering = ('email',)

# admin.site.register(CustomUser, CustomUserAdminFOOBAR)
