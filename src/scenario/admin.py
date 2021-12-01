from django.contrib import admin
from django import forms
from .models import Project, Scenario, Structures, \
    CostItem, CostItemDefaultFactors, CostItemDefaultCosts, CostItemDefaultEquations, \
    CostItemUserCosts, CostItemUserAssumptions


class ObjectAdmin(admin.ModelAdmin):
    ordering = ['-order']


def custom_titled_filter(title):
    """
    this allows overriding the name shown in the right-side FILTER panel

    :param title:
    :return:
    """
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper


def project_title(obj):
    return "%s" % obj.project.project_title


project_title.short_description = 'Project'


def user_fullname(obj):
    return "%s" % obj.project.user.get_full_name()


user_fullname.short_description = 'User'


def user_affilitation(obj):
    return "%s" % obj.project.user.organization_tx


user_affilitation.short_description = 'Affiliation'


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('user_fullname', 'user_affilitation', 'user_type', 'project_title')
    list_display_links = ('project_title',)
    list_filter = (('user__profile__user_type', custom_titled_filter("User Type")),)

    readonly_fields = ['create_date', 'modified_date']

    @admin.display(description='User Name')
    def user_fullname(self, obj):
        return "%s" % obj.user.get_full_name()

    def user_type(self, obj):
        return "%s" % obj.user.profile.user_type

    @admin.display(description='Affiliation')
    def user_affilitation(self, obj):
        return "%s" % obj.user.organization_tx

    @admin.display(description='Project', ordering='project_title')
    def project_title(self, obj):
        return "%s" % obj.project_title


admin.site.register(Project, ProjectAdmin)


class ScenarioAdmin(admin.ModelAdmin):
    list_display = (user_fullname, user_affilitation, 'user_type', project_title, 'scenario_title')
    list_display_links = ('scenario_title',)
    list_filter = (('project__user__profile__user_type', custom_titled_filter("User Type")),)

    exclude = ('areal_features', 'conventional_structures', 'nonconventional_structures', 'counter', 'scenario_date')

    readonly_fields = ['create_date', 'modified_date']

    def user_type(self, obj):
        return "%s" % obj.project.user.profile.user_type


    @admin.display(ordering='scenario_title')
    def scenario_title(self, obj):
        return "%s" % obj.scenario_title


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
    list_display = ('sort_nu', 'name', 'units', 'help_text')
    list_display_links = ('name',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(CostItemAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'help_text':
            field.widget = forms.Textarea(attrs={'cols': 80, 'rows': 4})
        return field


def costitem_sort_nu(obj):
    return obj.costitem.sort_nu


costitem_sort_nu.short_description = 'CostItem Sort No'


def costitem_name(obj):
    return "%s" % obj.costitem.name


costitem_name.short_description = 'CostItem Name'


class CostItemDefaultCostsAdmin(StructuresAdmin):
    list_display = (costitem_sort_nu, costitem_name, 'costitem_units', 'rsmeans_va',
                    'db_25pct_va','db_50pct_va', 'db_75pct_va',
                    'replacement_life', 'o_and_m_pct', 'equation')
    list_display_links = (costitem_name,)

    def costitem_units(self, obj):
        return "%s" % obj.costitem.units


class CostItemDefaultEquationsAdmin(StructuresAdmin):
    list_display = (costitem_sort_nu, costitem_name, 'equation_tx', 'a_area', 'z_depth', 'd_density', 'n_number')
    list_display_links = (costitem_name,)
    pass




class CostItemDefaultFactorsAdmin(StructuresAdmin):
    list_display = ('structure_name', 'costitem_name', 'a_area', 'z_depth', 'd_density', 'n_number')
    list_display_links = ('structure_name', 'costitem_name',)
    list_filter = (('structure__name', custom_titled_filter("Structure Name")),
                   ('costitem__name', custom_titled_filter('Cost Item Name')))

    @admin.display(empty_value='unknown', ordering='structure__name')
    def structure_name(self, obj):
        return "%s" % obj.structure.name

    @admin.display(empty_value='unknown', ordering='costitem__name')
    def costitem_name(self, obj):
        return "%s" % obj.costitem.name

    @admin.display(description = 'Area (a)')
    def a_area(self, obj):
        return "%s" % obj.a_area


    @admin.display(description='Depth (z)')
    def z_depth(obj):
        return obj.z_depth


    @admin.display(description='Density (d)')
    def d_density(obj):
        return obj.d_density


    @admin.display(description='Count (n)')
    def n_number(obj):
        return obj.z_depth




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

def structure_name(obj):
    return "%s" % obj.structure.name


structure_name.short_description = 'Structure Name'

class CostItemUserAssumptionsAdmin(admin.ModelAdmin):
    list_display = (user_name, user_type, scenario_project_title, scenario_title,
                    structure_name, costitem_name,
                    # cost_source, user_input_cost, 'base_year',
                    # replacement_life, o_and_m_pct, first_year_maintenance
                    )
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
admin.site.register(CostItemDefaultFactors, CostItemDefaultFactorsAdmin)
admin.site.register(CostItemDefaultCosts, CostItemDefaultCostsAdmin)
admin.site.register(CostItemDefaultEquations, CostItemDefaultEquationsAdmin)

admin.site.register(CostItemUserCosts, CostItemUserCostsAdmin)
admin.site.register(CostItemUserAssumptions, CostItemUserAssumptionsAdmin)
