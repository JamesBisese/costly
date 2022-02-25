from django.urls import path, include
from django.urls import re_path
from django.conf import settings
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'projects', views.ProjectViewSet, 'projects')
router.register(r'scenarios', views.ScenarioViewSet)
router.register(r'scenario_list', views.ScenarioListViewSet, 'scenariolist')
router.register(r'scenario_audit', views.ScenarioAuditViewSet, 'scenarioaudit')
router.register(r'structures', views.StructureViewSet)
router.register(r'cost_item', views.CostItemViewSet)

router.register(r'cost_item_default_costs', views.CostItemDefaultCostViewSet)
router.register(r'cost_item_user_costs', views.CostItemUserCostViewSet)

router.register(r'cost_item_default_equations_and_factors', views.CostItemDefaultEquationsAndFactors)
router.register(r'structure_cost_item_default_factors', views.StructureCostItemDefaultFactorsViewSet)
router.register(r'structure_user_cost_item_factors', views.StructureCostItemUserFactorsViewSet)

iis_app_alias = ''
if len(settings.IIS_APP_ALIAS) > 0:
    iis_app_alias = settings.IIS_APP_ALIAS + '/'

"""
    this tag makes all the urls reverse into 'scenario:{name}'
"""
app_name = 'scenario'

urlpatterns = [
    path(iis_app_alias + 'api/', include(router.urls)),

    # Project CRUD
    path(r'project/add/', views.project_create, name='project_create'),
    path(r'projects/', views.project_list, name='project_index'),  # plural version
    path(r'project/', views.project_list, name='index'),
    path(r'project/<int:pk>/update/', views.project_update, name='project_update'),
    path(r'project/<int:pk>/delete/', views.project_delete, name='project_delete'),

    path(r'project/<int:pk>/scenarios/', views.scenario_list, name='project_scenario_index'),
    # path(r'project/<int:pk>/scenarios/', views.ProjectScenarioViewSet.as_view(), name='2project_scenario_index'),


    # Scenario CRUD - with extra 'duplicate' and 'save'
    # path(r'scenario/add/', views.scenario_create, name='scenario_create'),

    re_path(r'project/(?P<project_id>\d+)/scenario/add/', views.scenario_create, name='project_scenario_create'),

    path(r'scenario/<int:pk>/duplicate/', views.scenario_duplicate, name='scenario_duplicate'),
    path(r'scenarios/', views.scenario_list, name='scenario_index'),  # plural version
    path(r'scenario/', views.scenario_list),
    path(r'scenario/<int:pk>/update/', views.scenario_update, name='scenario_update'),
    path(r'scenario/save/', views.scenario_save, name='scenario_save'),
    path(r'scenario/<int:pk>/delete/', views.scenario_delete, name='scenario_delete'),

    # Scenario - StructureCosts Read - returns partial HTML
    path(r'scenario/<int:pk>/structure_costs/<slug:structure_code>/', views.StructureCosts.as_view(), name='structure_costs'),
    path(r'scenario/<int:pk>/structure_costs/<slug:structure_code>/<slug:costitem_code>/', views.StructureCosts.as_view()),

    # Scenario - CostItem Update
    # path(r'scenario/costitem/<int:pk>/update/', views.costitem_defaultcosts_update, name='costitem_defaultcosts_update'),

    # Scenario - Results Read
    path(r'scenario/<int:pk>/results/', views.ScenarioResults.as_view(), name='scenario_results_with_class'),
    path(r'scenario/results/', views.CompareScenarioResults.as_view(), name='scenario_compare_results'),
    path(r'scenario/results/column/', views.CompareScenarioColumn.as_view(), name='scenario_compare_column'),
    # path(r'scenario/<string>1-8/results/', views.ScenarioResults.as_view(), name='scenario_results_multiple2_with_class'),

    # Scenario - Results in Excel Format
    path(r'scenario/<int:pk>/excel/', views.ScenarioExcelResults.as_view(), name='scenario_results_excel'),
    path(r'scenario/export/results/', views.CompareScenarioExcelResults.as_view(), name='scenario_export_results'),
    # new wide version of export
    path(r'scenario/export/extended_excel_report/', views.ScenarioExtendedExcelReport.as_view(), name='scenario_export_extended_excel_report'),

    path(r'scenario/template/', views.TemplateScenario.as_view(), name='scenario_json_template'),

    # StructureHelp - Read - not used. using slug 'all' returns a list of all values
    path(r'scenario/structure/help/<slug:structure_code>/', views.StructureHelp.as_view(), name='structure_help'),
    # StructureCostHelp - Read. using slug 'all' returns a list of all values, unrecognized code also returns list
    path(r'scenario/costitem/help/<slug:costitem_code>/', views.CostItemHelp.as_view(), name='costitem_help'),

    # audit HTML pages for the (relatively) immutable look-up lists and reference lists
    path(r'audit/structures/', views.audit_structure, name='structures'),
    path(r'audit/cost_item/', views.audit_cost_items, name='costitems'),
    path(r'audit/cost_item/default_costs/', views.audit_cost_item_default_cost,
         name='costitems_default_costs'),
    path(r'audit/cost_item/default_equations/', views.audit_cost_item_default_equations_and_factors,
         name='costitems_default_equations'),
    path(r'audit/structure_default_cost_item_factors/', views.audit_structure_default_cost_item_factors,
         name='costitems_default_factors'),

    # audit HTML pages for user input project, scenario, and cost_items
    path(r'audit/users/', views.audit_users, name='audit_users'),
    path(r'audit/projects/', views.audit_project, name='audit_projects'),
    path(r'audit/scenarios/', views.audit_scenario, name='audit_scenarios'),
    path(r'audit/cost_item/user_costs/', views.audit_costitem_user_cost, name='audit_costitems_user_costs'),
    path(r'audit/structure_user_cost_item_factors/', views.audit_structure_user_cost_item_factors,
         name='audit_structure_user_cost_item_factors'),
]

urlpatterns += [
    re_path(r'^select2/', include('django_select2.urls')),
]
