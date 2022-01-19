from django.contrib import admin
from django.contrib.admin.models import LogEntry, DELETION
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.urls import reverse

ADMIN_ORDERING = [

	('scenario', [
        'ArealFeatureLookup',
		'Structures',
		'CostItem',
		'CostItemDefaultCosts',
		'CostItemDefaultEquations',
		'StructureCostItemDefaultFactors',
		'Project',
		'Scenario',
		'ScenarioCostItemUserCosts',
		'StructureCostItemUserFactors',
	]),

	('authtools', [
		'User'
	]),
	('admin', [
		'LogEntry'
	 ]),
]


# Creating a sort function
def get_app_list(self, request):
	app_dict = self._build_app_dict(request)
	for app_name, object_list in ADMIN_ORDERING:
		app = app_dict[app_name]
		app['models'].sort(key=lambda x: object_list.index(x['object_name']))
		yield app

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = 'action_time'
    readonly_fields = ('action_time',)
    list_filter = ['user', 'content_type']
    search_fields = ['object_repr', 'change_message']
    list_display = ['__str__', 'content_type', 'action_time', 'user', 'object_link']

    # keep only view permission
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def object_link(self, obj):
        if obj.action_flag == DELETION:
            link = obj.object_repr
        else:
            ct = obj.content_type
            try:
                link = mark_safe('<a href="%s">%s</a>' % (
                                 reverse('admin:%s_%s_change' % (ct.app_label, ct.model),
                                         args=[obj.object_id]),
                                 escape(obj.object_repr),
                ))
            except NoReverseMatch:
                link = obj.object_repr
        return link
    object_link.admin_order_field = 'object_repr'
    object_link.short_description = 'object'

    def queryset(self, request):
        return super(LogEntryAdmin, self).queryset(request) \
            .prefetch_related('content_type')

admin.AdminSite.get_app_list = get_app_list
