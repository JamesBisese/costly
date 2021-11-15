from django.contrib import admin

from .models import Scenario, Structures, \
    CostItem, CostItemDefaultFactors, CostItemDefaultCosts, CostItemDefaultEquations, \
    CostItemUserCosts


def project_title(obj):
    return "%s" % obj.project.project_title


project_title.short_description = 'Project'


def scenario_title1(obj):
    return "%s" % obj.scenario_title


scenario_title1.short_description = 'Scenario'


def user_fullname(obj):
    return "%s" % obj.project.user.get_full_name()


user_fullname.short_description = 'User'


def user_type(obj):
    return "%s" % obj.project.user.organization_tx


user_type.short_description = 'User Type'


class ScenarioAdmin(admin.ModelAdmin):
    list_display = (user_fullname, user_type, project_title, scenario_title1)
    # list_display_links = (costitem_name,)
    pass


admin.site.register(Scenario, ScenarioAdmin)


class StructuresAdmin(admin.ModelAdmin):
    list_display = ('sort_nu', 'classification', 'name')
    list_display_links = ('name',)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False


class CostItemAdmin(StructuresAdmin):
    list_display = ('sort_nu', 'name')
    list_display_links = ('name',)
    pass


def costitem_sort_nu(obj):
    return obj.costitem.sort_nu


costitem_sort_nu.short_description = 'CostItem Sort No'


def costitem_name(obj):
    return "%s" % obj.costitem.name


costitem_name.short_description = 'CostItem Name'


class CostItemDefaultCostsAdmin(StructuresAdmin):
    list_display = (costitem_sort_nu, costitem_name)
    list_display_links = (costitem_name,)
    pass


class CostItemDefaultEquationsAdmin(StructuresAdmin):
    list_display = (costitem_sort_nu, costitem_name)
    list_display_links = (costitem_name,)
    pass


def user_name(obj):
    return "%s" % obj.scenario.project.user.name


user_name.short_description = 'User'


def user_type(obj):
    return "%s" % obj.scenario.project.user.profile.user_type


user_type.short_description = 'Type'


def scenario_project_title(obj):
    return "%s" % obj.scenario.project.project_title


scenario_project_title.short_description = 'Project'


def scenario_title(obj):
    return "%s" % obj.scenario.scenario_title


scenario_title.short_description = 'Scenario'


def cost_source(obj):
    source = obj.cost_source
    if source == 'rsmeans':
        source = 'Default'
    elif source == 'user':
        source = 'User'
    return "%s" % source


cost_source.short_description = 'Cost Source'


def user_input_cost(obj):
    input_cost = obj.user_input_cost
    if not input_cost:
        input_cost = 'N/A'
    return "%s" % input_cost


user_input_cost.short_description = 'User Cost'


def replacement_life(obj):
    return "%s" % obj.replacement_life


replacement_life.short_description = 'Replacement Life (Years)'


def o_and_m_pct(obj):
    return "%s" % obj.o_and_m_pct


o_and_m_pct.short_description = 'Annual O&M (%)'


def first_year_maintenance(obj):
    return "%s" % obj.first_year_maintenance


first_year_maintenance.short_description = 'First Year Maintenance'


class CostItemUserCostsAdmin(admin.ModelAdmin):
    list_display = (user_name, user_type, scenario_project_title, scenario_title, costitem_name,
                    cost_source, user_input_cost, 'base_year',
                    replacement_life, o_and_m_pct, first_year_maintenance)
    list_display_links = (costitem_name,)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Structures, StructuresAdmin)
admin.site.register(CostItem, CostItemAdmin)
admin.site.register(CostItemDefaultFactors)
admin.site.register(CostItemDefaultCosts, CostItemDefaultCostsAdmin)
admin.site.register(CostItemDefaultEquations, CostItemDefaultEquationsAdmin)

admin.site.register(CostItemUserCosts, CostItemUserCostsAdmin)
