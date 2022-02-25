from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# region -- Audit Pages --


@staff_member_required
def audit_users(request):
    """
        Audit Users - function based view using ajax to load data into DataTable

        http://127.0.0.1:92/audit/users/
    """
    context_data = {
        'title': 'Audit Users',
        'header': 'Audit Users',
        'IIS_APP_ALIAS': settings.IIS_APP_ALIAS
    }
    return render(request, 'audit/user.html', context_data)


@staff_member_required
def audit_project(request):
    """
        Audit Project

        http://127.0.0.1:92/audit/projects/
    """
    context_data = {
        'title': 'Audit Projects',
        'header': 'Audit Projects',
        'IIS_APP_ALIAS': settings.IIS_APP_ALIAS
    }
    return render(request, 'audit/project.html', context_data)


@staff_member_required
def audit_scenario(request):
    """
        Audit Scenario

        http://127.0.0.1:92/audit/scenarios/
    """
    context_data = {
        'title': 'Audit Scenarios',
        'header': 'Audit Scenarios',
        'IIS_APP_ALIAS': settings.IIS_APP_ALIAS
    }
    return render(request, 'audit/scenario.html', context_data)


@staff_member_required
def audit_costitem_user_cost(request):
    """
        Audit Cost Item User Costs

        http://127.0.0.1:92/audit/cost_item/user_costs/
    """
    context_data = {'title': 'Cost ItemUserCosts', 'header': 'Audit Cost Item User Costs',
                    'IIS_APP_ALIAS': settings.IIS_APP_ALIAS}
    return render(request, 'audit/cost_item_user_cost.html', context_data)


@login_required
def audit_structure(request):
    """
        Audit Structures URI/audit/structures/
        Data is loaded client-side using URI/api/structures/
    """
    context_data = {
        'title': 'Structures',
        'header': 'Structures',
        'IIS_APP_ALIAS': settings.IIS_APP_ALIAS
    }
    return render(request, 'audit/structures.html', context_data)


@login_required
def audit_areal_feature(request):
    """
        Audit Cost Items

        URI/audit/areal_feature/
    """
    context_data = {'title': 'Areal Features', 'header': 'Areal Features', 'IIS_APP_ALIAS': settings.IIS_APP_ALIAS}
    return render(request, 'audit/areal_feature.html', context_data)

@login_required
def audit_cost_items(request):
    """
        Audit Cost Items

        URI/audit/cost_items/
    """
    context_data = {'title': 'Cost Items', 'header': 'Cost Items', 'IIS_APP_ALIAS': settings.IIS_APP_ALIAS}
    return render(request, 'audit/cost_item.html', context_data)


@login_required
def audit_cost_item_default_cost(request):
    """
        Audit Cost Item Default Costs

        URI/audit/cost_items_default_cost/
    """
    context_data = {'title': 'Cost Items Default Costs', 'header': 'Cost Items Default Costs',
                    'IIS_APP_ALIAS': settings.IIS_APP_ALIAS}
    return render(request, 'audit/cost_item_default_cost.html', context_data)


@login_required
def audit_cost_item_default_equations_and_factors(request):
    """
        Audit Cost Item Default Equations and Factors

        URI/audit/cost_items_default_equations_and_factors/
    """
    context_data = {
        'title': 'Cost Items Default Equations and Factors',
        'header': 'Cost Items Default Equations and Factors',
        'IIS_APP_ALIAS': settings.IIS_APP_ALIAS
    }
    return render(request, 'audit/cost_item_default_equations_and_factors.html', context_data)


@login_required
def audit_structure_default_cost_item_factors(request):
    """
        Audit Structure Default Cost Item Factors

        URI/audit/structure_default_cost_item_factors/
    """
    context_data = {
        'title': 'Cost Items Default Factors',
        'header': 'Structure/Cost Item Default Factors',
        'IIS_APP_ALIAS': settings.IIS_APP_ALIAS
    }
    return render(request, 'audit/structure_cost_item_default_factors.html', context_data)


@staff_member_required
def audit_structure_user_cost_item_factors(request):
    """
        Audit Structure User Cost Item Factors

        URI/audit/structure_user_cost_item_factors/
        and data is loaded via URI/api/structure_user_cost_item_factors/
    """
    context_data = {
        'title': 'Cost Items User Factors',
        'header': 'Structure/Cost Item User Factors',
        'IIS_APP_ALIAS': settings.IIS_APP_ALIAS
    }
    return render(request, 'audit/structure_cost_item_user_factors.html', context_data)


# endregion -- audit pages --
