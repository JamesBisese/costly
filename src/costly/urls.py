from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

import authtools.urls
import profiles.urls
import scenario.urls
import accounts.urls
import users.urls

#
# TODO: move this into scenario/urls.py where it belongs
# need to figure out how to still use /api/ as the root though
#
from . import views

# Personalized admin site settings like title and header
admin.site.site_title = 'GSI Cost Tool'
admin.site.site_header = 'GSI Cost Tool Administration'

iis_app_alias = ''
if len(settings.IIS_APP_ALIAS) > 0:
    iis_app_alias = settings.IIS_APP_ALIAS + '/'

admin.site.site_url = r'/' + iis_app_alias

urlpatterns = [

    path(iis_app_alias + 'about/', views.AboutPage.as_view(), name='about'),
    path(iis_app_alias + 'scope/', views.ScopePage.as_view(), name='scope'),

    path(iis_app_alias + 'why/', views.WhyPage.as_view(), name='why'),
    path(iis_app_alias + 'setup/', views.SetupPage.as_view(), name='setup'),

    path(iis_app_alias + 'help/', views.HelpPage.as_view(),   name='help'),
    path(iis_app_alias + 'instructions/', views.InstructionsPage.as_view(), name='instructions'),

    path(iis_app_alias + 'reference/', views.ReferencePage.as_view(),   name='reference'),
    path(iis_app_alias + 'audit/', views.AuditPage.as_view(),   name='audit'),

    path(iis_app_alias + 'users/', include(profiles.urls)),
    path(iis_app_alias + 'admin/', admin.site.urls),

    path(iis_app_alias + 'accounts/', include(authtools.urls)),

    path(iis_app_alias + '', include(scenario.urls)),
    path(iis_app_alias + '', include(accounts.urls)),
    path(iis_app_alias + '', include(users.urls)),

    path(iis_app_alias + '', views.HomePage.as_view(), name='home'),
]

# User-uploaded files like profile pics need to be served in development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Include django debug toolbar if DEBUG is on
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
