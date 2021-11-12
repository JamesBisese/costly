//used in scenario_index.js

var SETTINGS = {};

SETTINGS.URLS = {
    'IIS_PREFIX': '',


    'project_list':   '/api/projects/?format=datatables',
    'project_update': '/project/<int:pk>/update/',
    'project_delete': '/project/<int:pk>/delete/',

    'scenario_list':  '/api/scenarios/?format=datatables',

    'new_scenario_list': '/api/scenario_list/?project=<int:pk>&format=datatables',

    'project_scenario_list': '/project/<int:pk>/scenarios/',
    'project_scenario_list_api': '/api/projects/<int:pk>/scenarios/',

    'scenario_root':   '/scenario/',
    'scenario_duplicate': '/scenario/<int:pk>/duplicate/',
    'scenario_update': '/scenario/<int:pk>/update/',
    'scenario_delete': '/scenario/<int:pk>/delete/',
    'scenario_result': '/scenario/<int:pk>/results/',

    'scenario_structure_cost': '/scenario/<int:pk>/structure_costs/<str:structure_code>/?format=html',

    'scenario_save':     '/scenario/save/',
    'scenario_template': '/scenario/template/',
    'scenario_default':  '/scenario/default/',
    'scenario_api':      '/api/scenarios/<int:pk>/',

    'scenario_results':  '/scenario/results/?id=',
    'scenario_export_results':  '/scenario/export/results/?id=',

    'scenario_export_extended_excel_report':  '/scenario/export/extended_excel_report/?id=',

    'scenario_compare_column': '/scenario/results/column/?id=',


    'costitem_help': '/scenario/costitem/help',
    'scenario_structure_help': '/scenario/structure_costs/help',

    // JSON data for pages in REFERENCES tab
    'audit_structure_data': '/api/structures/',
    'audit_cost_item_data':  '/api/cost_item/',
    'audit_cost_item_default_cost_data': '/api/cost_item_default_costs/',
    'audit_cost_item_default_equations_and_factors_data': '/api/cost_item_default_equations_and_factors/',
    'audit_structure_cost_item_default_factors_data': '/api/structure_cost_item_default_factors/',

    // JSON data for pages in AUDIT tab
    'audit_user_data': '/api/users/',
    'audit_project_data':   '/api/projects/',
    'audit_scenario_data': '/api/scenario_audit/',
    'audit_cost_item_user_costs_data': '/api/cost_item_user_costs',
    'audit_cost_item_user_factors_data': '/api/cost_item_user_factors/',
}


