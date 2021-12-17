from django.contrib import admin

ADMIN_ORDERING = [

	('scenario', [
		'Structures',
		'CostItem',
		'CostItemDefaultCosts',
		'CostItemDefaultEquations',
		'CostItemDefaultFactors',
		'Project',
		'Scenario',
		'CostItemUserCosts',
		'CostItemUserAssumptions',
	]),

	('authtools', [
		'User'
	])
]


# Creating a sort function
def get_app_list(self, request):
	app_dict = self._build_app_dict(request)
	for app_name, object_list in ADMIN_ORDERING:
		app = app_dict[app_name]
		app['models'].sort(key=lambda x: object_list.index(x['object_name']))
		yield app


admin.AdminSite.get_app_list = get_app_list
