from django.urls import path, include, re_path
from django.conf.urls import url

import sys

from . import views

"""
    this tag makes all the urls reverse into 'scenario:{name}'
"""
app_name = 'scenario'

urlpatterns = [

    # Project CRUD
    path(r'project/add/', views.project_create, name='project_create'),
    path(r'projects/', views.project_list, name='project_index'), # plural version
    path(r'project/', views.project_list, name='index'),
    path(r'project/<int:pk>/update/', views.project_update, name='project_update'),
    path(r'project/<int:pk>/delete/', views.project_delete, name='project_delete'),

    path(r'project/<int:pk>/scenarios/', views.scenario_list, name='project_scenario_index'),
    # path(r'project/<int:pk>/scenarios/', views.ProjectScenarioViewSet.as_view(), name='2project_scenario_index'),


    # Scenario CRUD - with extra 'duplicate' and 'save'
    path(r'scenario/add/', views.scenario_create, name='scenario_create'),

    url(r'project/(?P<project_id>\d+)/scenario/add/', views.scenario_create, name='project_scenario_create'),

    path(r'scenario/<int:pk>/duplicate/', views.scenario_duplicate, name='scenario_duplicate'),
    path(r'scenarios/', views.scenario_list, name='scenario_index'), # plural version
    path(r'scenario/', views.scenario_list),
    path(r'scenario/<int:pk>/update/', views.scenario_update, name='scenario_update'),
    path(r'scenario/save/', views.scenario_save, name='scenario_save'),
    path(r'scenario/<int:pk>/delete/', views.scenario_delete, name='scenario_delete'),

    # Scenario - StructureCosts Read - returns partial HTML
    path(r'scenario/<int:pk>/structure_costs/<slug:structure_code>/', views.StructureCosts.as_view(), name='structure_costs'),
    # path(r'scenario/<int:pk>/structure_costsNEW/', views.StructureCostsNEW.as_view(), name='structure_costs_all'),

    # Scenario - CostItem Update
    path(r'scenario/costitem/<int:pk>/update/', views.costitem_defaultcosts_update, name='costitem_defaultcosts_update'),

    # Scenario - Results Read
    path(r'scenario/<int:pk>/results/', views.ScenarioResults.as_view(), name='scenario_results_with_class'),
    path(r'scenario/results/', views.MultipleScenarioResults.as_view(), name='scenario_results_multiple_with_class'),
    path(r'scenario/<string>1-8/results/', views.ScenarioResults.as_view(), name='scenario_results_multiple2_with_class'),



    path(r'scenario/default/', views.DefaultScenario.as_view(), name='scenario_json_default'),
    path(r'scenario/template/', views.TemplateScenario.as_view(), name='scenario_json_template'),

    # StructureHelp - Read - not used. using slug 'all' returns a list of all values
    path(r'scenario/structure/help/<slug:structure_code>/', views.StructureHelp.as_view(), name='structure_help'),
    # StructureCostHelp - Read. using slug 'all' returns a list of all values, unrecognized code also returns list
    path(r'scenario/costitem/help/<slug:costitem_code>/', views.CostItemHelp.as_view(), name='costitem_help'),

    # path(r'scenario/<int:pk>/increment/', views.scenario_increment, name='scenario_increment'),
    # path(r'scenario/<int:pk>/decrement/', views.scenario_decrement, name='scenario_decrement'),

    # a list of all the Cost Item Default Costs in the database
    path(r'structures/', views.StructuresList.as_view(), name='structures'),

    path(r'costitems/', views.CostItemsList.as_view(), name='costitems'),

    # a list of all the Cost Item Default Costs in the database
    path(r'cost_item/default_costs/', views.CostItemDefaultCostsList.as_view(), name='costitems_default_costs'),

    # a list of all the Structure - Cost Item Default Assumptions in the database
    path(r'cost_item/default_equations/', views.CostItemDefaultEquationsList.as_view(), name='costitems_default_equations'),
    path(r'cost_item/default_factors/', views.CostItemDefaultFactorsList.as_view(), name='costitems_default_factors'),

]

urlpatterns += [
	url(r'^select2/', include('django_select2.urls')),
	# path(r'', views.ScenarioList.as_view(), name='scenario-index'),


]

# path(r'scenario/addwithclass/', views.ScenarioCreate.as_view(), name='scenario_create_with_class'),

# path(r'json/', views.json_index, name='json_index'),
# path(r'json_load/', views.json_load, name='json_load'),
# path(r'part/', views.test_partial, name='test_partial'),
# path(r's3/', views.CostItemDefaultCostsList.as_view(), name='costitems_create_with_class'),
# path(r'scenario/<int:pk>/structure_costs/<slug:structure_code>/', views.StructureCosts.as_view(),
#      name='structure_costs'),
#
# path(r'scenario/structure_costs/help/<slug:costitem_code>/', views.StructureCostsHelp.as_view(),
#      name='structure_costs_help'),
#
# # this isn't implemented correctly - it should be returned as part of the API with format=html
# path(r'scenario/<int:pk>/results/', views.ScenarioResults.as_view(), name='scenario_results_with_class'),
# path(r'scenario/results/', views.MultipleScenarioResults.as_view(), name='scenario_results_multiple_with_class'),
# path(r'scenario/<string>1-8/results/', views.ScenarioResults.as_view(), name='scenario_results_multiple2_with_class'),
# path(r'scenario/costitem/<int:pk>/update/', views.costitem_defaultcosts_update, name='costitem_defaultcosts_update'),
#
# path(r'scenario/default/', views.DefaultScenario.as_view(), name='scenario_json_default'),
# path(r'scenario/template/', views.TemplateScenario.as_view(), name='scenario_json_template'),
#
# path(r'scenario/add/', views.scenario_create, name='scenario_create'),
#
# path(r'scenario/addwithclass/', views.ScenarioCreate.as_view(), name='scenario_create_with_class'),
#
# path(r'scenario/<int:pk>/update/', views.scenario_update, name='scenario_update'),
# path(r'scenario/<int:pk>/duplicate/', views.scenario_duplicate, name='scenario_duplicate'),
# path(r'scenario/<int:pk>/increment/', views.scenario_increment, name='scenario_increment'),
# path(r'scenario/<int:pk>/decrement/', views.scenario_decrement, name='scenario_decrement'),
# path(r'scenario/<int:pk>/delete/', views.scenario_delete, name='scenario_delete'),

# path(r'', views.project_list, name='index'),

# urlpatterns = [
# 	path(r'scenario/', views.index, name='index'),
# ]

# Add URLConf to create, update, and delete person
# urlpatterns = [
# 	path(r'persons/', views.PersonList.as_view(), name='person_list'),
# 	path(r'person/<int:pk>/view/', views.PersonView.as_view(), name='person_view'),
# 	path(r'person/add/', views.PersonCreate.as_view(), name='person_create'),
# 	path(r'person/<int:pk>/update/', views.PersonUpdate.as_view(), name='person_update'),
# 	path(r'person/<int:pk>/delete/', views.PersonDelete.as_view(), name='person_delete'),
# ]

# urlpatterns += [
# 	path(r'scenario/', views.ScenarioList.as_view(), name='scenario_list'),
# 	path(r'scenario/add/', views.ScenarioCreate.as_view(), name='scenario_create'),
# 	path(r'scenario/<int:pk>/update/', views.ScenarioUpdate.as_view(), name='scenario_update'),
# 	path(r'scenario/<int:pk>/delete/', views.ScenarioDelete.as_view(), name='scenario_delete'),
# ]

    # path(r'model/', views.ModelPage.as_view(), name='model'),
    # path(r'costtool/', views.CostToolModelPage.as_view(), name='cost_tool_model'),

    # path(r'projects/', views.project_list, name='project_list'),
    # path(r'projects/add/', views.project_create, name='project_create'),
    # path(r'projects/<int:pk>/update/', views.project_update, name='project_update'),
    # path(r'projects/<int:pk>/delete/', views.project_delete, name='project_delete'),

	# path(r'location/', views.LocationList.as_view(), name='location_list'),
	# path(r'location/add/', views.LocationCreate.as_view(), name='location_create'),
	# path(r'location/<int:pk>/update/', views.LocationUpdate.as_view(), name='location_update'),
	# path(r'location/<int:pk>/delete/', views.LocationDelete.as_view(), name='location_delete'),