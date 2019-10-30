from django.contrib import admin
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers

import profiles.urls
import accounts.urls
import scenario.urls
# import testapp.urls

#
# TODO: move this into scenario/urls.py where it belongs
# need to figure out how to still use /api/ as the root though
#
from . import views
import scenario.views
from scenario.views import UserViewSet, ProjectViewSet, \
    ScenarioViewSet, ScenarioListViewSet, \
    StructureViewSet, \
    CostItemViewSet, \
    CostItemDefaultCostViewSet, CostItemDefaultEquationsViewSet, CostItemDefaultFactorsViewSet, \
    CostItemUserCostViewSet, CostItemUserAssumptionsViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'scenarios', ScenarioViewSet)
router.register(r'scenario_list', ScenarioListViewSet)
router.register(r'structures', StructureViewSet)
router.register(r'costitems', CostItemViewSet)

router.register(r'costitemdefaultcosts', CostItemDefaultCostViewSet)
router.register(r'costitemusercosts', CostItemUserCostViewSet)

router.register(r'costitemdefaultequations', CostItemDefaultEquationsViewSet)
router.register(r'costitemdefaultfactors', CostItemDefaultFactorsViewSet)
router.register(r'costitemuserassumptions', CostItemUserAssumptionsViewSet)

# Personalized admin site settings like title and header
admin.site.site_title = 'Costly Site Admin'
admin.site.site_header = 'Costly Administration'

iis_app_alias = ''
if len(settings.IIS_APP_ALIAS) > 0:
    iis_app_alias = settings.IIS_APP_ALIAS + '/'

admin.site.site_url = r'/' + iis_app_alias

urlpatterns = [


    path(iis_app_alias + 'api/', include(router.urls)),

    path(iis_app_alias + 'about/', views.AboutPage.as_view(), name='about'),
    path(iis_app_alias + 'scope/', views.ScopePage.as_view(), name='scope'),

    path(iis_app_alias + 'why/', views.WhyPage.as_view(), name='why'),
    path(iis_app_alias + 'setup/', views.SetupPage.as_view(), name='setup'),

    path(iis_app_alias + 'help/', views.HelpPage.as_view(),   name='help'),
    path(iis_app_alias + 'instructions/', views.InstructionsPage.as_view(), name='instructions'),

    path(iis_app_alias + 'reference/', views.ReferencePage.as_view(),   name='reference'),

    path(iis_app_alias + 'users/', include(profiles.urls)),
    path(iis_app_alias + 'admin/', admin.site.urls),
    # path(iis_app_alias + 'testapp/', include(testapp.urls)),
    path(iis_app_alias + '', include(scenario.urls)),
    path(iis_app_alias + '', include(accounts.urls)),

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
