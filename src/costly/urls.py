from django.contrib import admin
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers

import profiles.urls
import accounts.urls
import scenario.urls
import testapp.urls

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
admin.site.site_url = r'/' + settings.IIS_APP_ALIAS

urlpatterns = [


    path(settings.IIS_APP_ALIAS + 'api/', include(router.urls)),

    path(settings.IIS_APP_ALIAS + 'about/', views.AboutPage.as_view(), name='about'),
    path(settings.IIS_APP_ALIAS + 'scope/', views.ScopePage.as_view(), name='scope'),

    path(settings.IIS_APP_ALIAS + 'why/', views.WhyPage.as_view(), name='why'),
    path(settings.IIS_APP_ALIAS + 'setup/', views.SetupPage.as_view(), name='setup'),

    path(settings.IIS_APP_ALIAS + 'help/', views.HelpPage.as_view(),   name='help'),
    path(settings.IIS_APP_ALIAS + 'instructions/', views.InstructionsPage.as_view(), name='instructions'),

    path(settings.IIS_APP_ALIAS + 'reference/', views.ReferencePage.as_view(),   name='reference'),

    path(settings.IIS_APP_ALIAS + 'users/', include(profiles.urls)),
    path(settings.IIS_APP_ALIAS + 'admin/', admin.site.urls),
    path(settings.IIS_APP_ALIAS + 'testapp/', include(testapp.urls)),
    path(settings.IIS_APP_ALIAS + '', include(scenario.urls)),
    path(settings.IIS_APP_ALIAS + '', include(accounts.urls)),

    path(settings.IIS_APP_ALIAS + '', views.HomePage.as_view(), name='home'),

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
