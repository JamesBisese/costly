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


@admin.display(description="Affiliation", ordering='project__user__organization_tx')
def user_affiliation(obj):
    return "%s" % obj.project.user.organization_tx


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('user_fullname', 'user_affiliation', 'user_type', 'project_title', 'create_date', 'modified_date')
    list_display_links = ('project_title',)
    list_filter = (('user__profile__user_type', custom_titled_filter("User Type")),)

    readonly_fields = ['create_date', 'modified_date']

    @admin.display(description='User Name', ordering='user__name')
    def user_fullname(self, obj):
        return "%s" % obj.user.get_full_name()

    @admin.display(description='Affiliation', ordering='user__organization_tx')
    def user_affiliation(self, obj):
        return "%s" % obj.user.organization_tx

    @admin.display(ordering='user__profile__user_type')
    def user_type(self, obj):
        return "%s" % obj.user.profile.user_type

    @admin.display(description='Project', ordering='project_title')
    def project_title(self, obj):
        return "%s" % obj.project_title

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


admin.site.register(Project, ProjectAdmin)


class ScenarioAdmin(admin.ModelAdmin):
    list_display = ('user_fullname', user_affiliation, 'user_type',
                    'project_title', 'scenario_title', 'create_date', 'modified_date')
    list_display_links = ('scenario_title',)
    list_filter = (('project__user__profile__user_type', custom_titled_filter("User Type")),)

    exclude = ('areal_features', 'conventional_structures', 'nonconventional_structures', 'counter', 'scenario_date')

    readonly_fields = ['create_date', 'modified_date']

    @admin.display(description='User Name', ordering='project__user__name')
    def user_fullname(self, obj):
        return "%s" % obj.project.user.get_full_name()

    @admin.display(ordering='project__user__profile__user_type')
    def user_type(self, obj):
        return "%s" % obj.project.user.profile.user_type

    @admin.display(description='Project', ordering='project__project_title')
    def project_title(self, obj):
        return "%s" % obj.project.project_title

    @admin.display(ordering='scenario_title')
    def scenario_title(self, obj):
        return "%s" % obj.scenario_title

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


admin.site.register(Scenario, ScenarioAdmin)


class StructuresAdmin(admin.ModelAdmin):
    list_display = ('sort_nu', 'classification', 'name')
    list_display_links = ('name',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(StructuresAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'help_text':
            field.widget = forms.Textarea(attrs={'cols': 80, 'rows': 4})
        return field

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


@admin.display(description='CostItem Sort No', ordering='costitem__sort_nu')
def costitem_sort_nu(obj):
    return obj.costitem.sort_nu


@admin.display(description='CostItem Name', empty_value='unknown', ordering='costitem__name')
def costitem_name(obj):
    return "%s" % obj.costitem.name


class CostItemDefaultCostsAdmin(StructuresAdmin):
    list_display = (costitem_sort_nu, 'costitem_name', 'costitem_units', 'rsmeans_va',
                    'db_25pct_va', 'db_50pct_va', 'db_75pct_va',
                    'replacement_life', 'o_and_m_pct', 'equation')
    list_display_links = ('costitem_name',)

    @admin.display(empty_value='unknown', ordering='costitem__units')
    def costitem_units(self, obj):
        return "%s" % obj.costitem.units

    @admin.display(empty_value='unknown', ordering='costitem__name')
    def costitem_name(self, obj):
        return "%s" % obj.costitem.name


class CostItemDefaultEquationsAdmin(StructuresAdmin):
    list_display = (costitem_sort_nu, costitem_name, 'equation_tx', 'a_area', 'z_depth', 'd_density', 'n_number')
    list_display_links = (costitem_name,)
    pass


class StructureCostItemDefaultFactorsAdmin(StructuresAdmin):
    """
    this is tied to both Structure (parent) and Cost Item (child)
    """
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

    @admin.display(description='Area (a)')
    def a_area(self, obj):
        return "%s" % obj.a_area

    @admin.display(description='Depth (z)')
    def z_depth(self, obj):
        return obj.z_depth

    @admin.display(description='Density (d)')
    def d_density(self, obj):
        return obj.d_density

    @admin.display(description='Count (n)')
    def n_number(self, obj):
        return obj.z_depth


@admin.display(description='User', ordering='scenario__project__user__name')
def user_name(obj):
    return "%s" % obj.scenario.project.user.name


@admin.display(description='Type', ordering='scenario__project__user__profile__user_type')
def user_type(obj):
    return "%s" % obj.scenario.project.user.profile.user_type


@admin.display(description='Project', ordering='scenario__project__project_title')
def scenario_project_title(obj):
    return "%s" % obj.scenario.project.project_title


@admin.display(description='Scenario', ordering='scenario__scenario_title')
def scenario_title(obj):
    return "%s" % obj.scenario.scenario_title


@admin.display(description='Cost Source', ordering='cost_source')
def cost_source(obj):
    source = obj.cost_source
    if source == 'rsmeans':
        source = 'Default'
    elif source == 'user':
        source = 'User'
    return "%s" % source


@admin.display(description='User Cost', ordering='user_input_cost')
def user_input_cost(obj):
    input_cost = obj.user_input_cost
    if not input_cost:
        input_cost = 'N/A'
    return "%s" % input_cost


@admin.display(description='Replacement Life (Years)', ordering='replacement_life')
def replacement_life(obj):
    return "%s" % obj.replacement_life


@admin.display(description='Annual O&M (%)', ordering='o_and_m_pct')
def o_and_m_pct(obj):
    return "%s" % obj.o_and_m_pct


@admin.display(description='First Year Maintenance', ordering='first_year_maintenance')
def first_year_maintenance(obj):
    return "%s" % obj.first_year_maintenance


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


@admin.display(description='Structure Name', empty_value='unknown', ordering='structure__name')
def structure_name(obj):
    return "%s" % obj.structure.name


class CostItemUserAssumptionsAdmin(admin.ModelAdmin):
    list_display = (user_name, user_type, scenario_project_title, scenario_title,
                    structure_name, costitem_name,
                    # cost_source, user_input_cost, 'base_year',
                    # replacement_life, o_and_m_pct, first_year_maintenance
                    )
    list_display_links = (costitem_name,)
    list_filter = (('scenario__project__project_title', custom_titled_filter("Project")),)
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
admin.site.register(CostItemDefaultCosts, CostItemDefaultCostsAdmin)
admin.site.register(CostItemDefaultEquations, CostItemDefaultEquationsAdmin)
admin.site.register(CostItemDefaultFactors, StructureCostItemDefaultFactorsAdmin)



admin.site.register(CostItemUserCosts, CostItemUserCostsAdmin)
admin.site.register(CostItemUserAssumptions, CostItemUserAssumptionsAdmin)
