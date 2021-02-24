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

    'scenario_compare_column': '/scenario/results/column/?id=',

    'structures_list': '/api/structures/?format=datatables',
    'costitems_list':  '/api/costitems/?format=datatables',
    'costitems_default_costs_list': '/api/costitemdefaultcosts/?format=datatables',

    // 'costitems_user_costs_list': '/api/costitemusercosts/?format=datatables',

    'costitems_default_equations_list': '/api/costitemdefaultequations/?format=datatables',
    'costitems_default_factors_list': '/api/costitemdefaultfactors/?format=datatables',

    'costitem_help': '/scenario/costitem/help',
    'scenario_structure_help': '/scenario/structure_costs/help',
}


