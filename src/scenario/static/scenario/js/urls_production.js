//used in scenario_index.js

var SETTINGS = {};
var iis_prefix = '/gsicosttool';

SETTINGS.URLS = {
    'IIS_PREFIX': iis_prefix,
    'project_list':   iis_prefix + '/api/projects/?format=datatables',
    'project_update': iis_prefix + '/project/<int:pk>/update/',
    'project_delete': iis_prefix + '/project/<int:pk>/delete/',

    'scenario_list':  iis_prefix + '/api/scenarios/?format=datatables',

    'new_scenario_list': iis_prefix + '/api/scenario_list/?project=<int:pk>&format=datatables',

    'project_scenario_list': iis_prefix + '/project/<int:pk>/scenarios/',
    'project_scenario_list_api': iis_prefix + '/api/projects/<int:pk>/scenarios/',

    'scenario_root':   iis_prefix + '/scenario/',
    'scenario_duplicate': iis_prefix + '/scenario/<int:pk>/duplicate/',
    'scenario_update': iis_prefix + '/scenario/<int:pk>/update/',
    'scenario_delete': iis_prefix + '/scenario/<int:pk>/delete/',

    'scenario_structure_cost': iis_prefix + '/scenario/<int:pk>/structure_costs/<str:structure_code>/?format=html',

    'scenario_save':     iis_prefix + '/scenario/save/',
    'scenario_template': iis_prefix + '/scenario/template/',
    'scenario_default':  iis_prefix + '/scenario/default/',
    'scenario_api':      iis_prefix + '/api/scenarios/<int:pk>/',

    'scenario_results':  iis_prefix + '/scenario/results/?id=',

    'structures_list': iis_prefix + '/api/structures/?format=datatables',
    'costitems_list':  iis_prefix + '/api/costitems/?format=datatables',
    'costitems_default_costs_list': iis_prefix + '/api/costitemdefaultcosts/?format=datatables',
    'costitems_default_equations_list': iis_prefix + '/api/costitemdefaultequations/?format=datatables',
    'costitems_default_factors_list': iis_prefix + '/api/costitemdefaultfactors/?format=datatables',

    'costitem_help': iis_prefix + '/scenario/costitem/help',
    'scenario_structure_help': iis_prefix + '/scenario/structure_costs/help',
}
