import io
import json

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import HttpResponseRedirect, render, get_object_or_404
from django_tables2 import SingleTableView
from django_tables2.export.views import ExportMixin
from django.template.loader import render_to_string
from django.views import generic
from django.urls import reverse, reverse_lazy

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin

from djmoney.money import Money

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

import xlsxwriter

from .models import Project, Scenario, ArealFeatures, Structures, \
    ConventionalStructures, NonConventionalStructures, \
    CostItem, CostItemDefaultEquations, \
    CostItemDefaultCosts, CostItemUserCosts, \
    CostItemDefaultFactors, CostItemUserAssumptions

from .forms import ProjectForm, ScenarioEditForm
from . import tables

from authtools.models import User

from .serializers import UserSerializer, ProjectSerializer, EmbeddedProjectSerializer, \
    ScenarioSerializer, ScenarioListSerializer, ScenarioAuditSerializer, \
    StructureSerializer, \
    CostItemDefaultCostSerializer, CostItemUserCostSerializer, \
    CostItemDefaultEquationsSerializer, CostItemDefaultFactorsSerializer, \
    CostItemSerializer, CostItemUserAssumptionsSerializer

# region -- Audit Pages --

"""
    Audit Users - function based view using ajax to load data into DataTable

    http://127.0.0.1:92/audit/users/
"""


@login_required
def audit_users(request):
    context_data = {'title': 'Audit Users', 'header': 'Audit Users', 'IIS_APP_ALIAS': settings.IIS_APP_ALIAS}
    return render(request, 'audit/user.html', context_data)


"""
    Audit Project

    http://127.0.0.1:92/audit/projects/
"""


@login_required
def audit_project(request):
    context_data = {'title': 'Audit Projects', 'header': 'Audit Projects', 'IIS_APP_ALIAS': settings.IIS_APP_ALIAS}
    return render(request, 'audit/project.html', context_data)


"""
    Audit Scenario
    
    http://127.0.0.1:92/audit/scenarios/
"""


@login_required
def audit_scenario(request):
    context_data = {'title': 'Audit Scenarios', 'header': 'Audit Scenarios', 'IIS_APP_ALIAS': settings.IIS_APP_ALIAS}
    return render(request, 'audit/scenario.html', context_data)


"""
    Audit Cost Item User Costs

    http://127.0.0.1:92/audit/cost_item/user_costs/
"""


@login_required
def audit_costitem_user_cost(request):
    context_data = {'title': 'Cost ItemUserCosts', 'header': 'Audit Cost Item User Costs',
                    'IIS_APP_ALIAS': settings.IIS_APP_ALIAS}
    return render(request, 'audit/cost_item_user_cost.html', context_data)


"""
    Audit Structures

    URI/audit/structures/
"""


@login_required
def audit_structure(request):
    context_data = {'title': 'Structures', 'header': 'Structures', 'IIS_APP_ALIAS': settings.IIS_APP_ALIAS}
    return render(request, 'audit/structures.html', context_data)


"""
    Audit Cost Items

    URI/audit/cost_items/
"""


@login_required
def audit_cost_items(request):
    context_data = {'title': 'Cost Items', 'header': 'Cost Items', 'IIS_APP_ALIAS': settings.IIS_APP_ALIAS}
    return render(request, 'audit/cost_item.html', context_data)


"""
    Audit Cost Item Default Costs

    URI/audit/cost_items_default_cost/
"""


@login_required
def audit_cost_item_default_cost(request):
    context_data = {'title': 'Cost Items Default Costs', 'header': 'Cost Items Default Costs',
                    'IIS_APP_ALIAS': settings.IIS_APP_ALIAS}
    return render(request, 'audit/cost_item_default_cost.html', context_data)


"""
    Audit Cost Item Default Equations and Factors

    URI/audit/cost_items_default_equations_and_factors/
"""


@login_required
def audit_cost_item_default_equations_and_factors(request):
    context_data = {'title': 'Cost Items Default Equations and Factors',
                    'header': 'Cost Items Default Equations and Factors', 'IIS_APP_ALIAS': settings.IIS_APP_ALIAS}
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


@login_required
def audit_structure_user_cost_item_factors(request):
    """
        Audit Structure User Cost Item Factors

        URI/audit/structure_user_cost_item_factors/
    """
    context_data = {
        'title': 'Cost Items User Factors',
        'header': 'Structure/Cost Item User Factors',
        'IIS_APP_ALIAS': settings.IIS_APP_ALIAS
    }
    return render(request, 'audit/structure_cost_item_user_factors.html', context_data)


# endregion -- audit pages --

"""
    Project functionality
"""


@login_required
def project_list(request):
    """
        project list as function based views using ajax to feed in data

        http://127.0.0.1:92/projects/
    """
    projects = Project.objects.all()
    context_data = {'projects': projects,
                    'header': 'Projects'}
    if request.user.has_perm('scenario.add_project'):
        context_data['can_add'] = True

    # jab - added for beta-user-testing.  allow all users to add
    context_data['can_add'] = True
    context_data['IIS_APP_ALIAS'] = settings.IIS_APP_ALIAS

    return render(request, 'project/project_index.html', context_data)


def save_project_form(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            # I don't know how this is supposed to work.  I needed
            # to add the 'instance' thing, but it doesn't seem right
            if form.cleaned_data['project_area'] is not None:
                form.cleaned_data['project_area'] = form.cleaned_data['project_area'].replace(",", "")
                form.instance.project_area = form.cleaned_data['project_area'].replace(",", "")
                # this is to take off any decimal part.  assuming no one really owns land to the part of a square foot.
                form.instance.project_area = str(int(float(form.instance.project_area)))
                form.cleaned_data['project_area'] = form.instance.project_area
            form.save()
            data['form_is_valid'] = True
            projects = Project.objects.all()
            data['html_list'] = render_to_string('project/includes/partial_project_list.html', {
                'projects': projects
            })
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
    else:
        form = ProjectForm(user_id=request.user.id)
    return save_project_form(request, form, 'project/includes/partial_project_create.html')


def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
    else:
        form = ProjectForm(instance=project)
    return save_project_form(request, form, 'project/includes/partial_project_update.html')


def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    data = dict()
    if request.method == 'POST':
        project.delete()
        data['form_is_valid'] = True
        projects = Project.objects.all()
        data['html_list'] = render_to_string('project/includes/partial_project_list.html', {
            'projects': projects
        })
    else:
        context = {'project': project}
        data['html_form'] = render_to_string('project/includes/partial_project_delete.html', context, request=request)
    return JsonResponse(data)


'''
    TBD provided via /api/structures and /api/structures/?code=TBD
'''


class ProjectScenarioViewSet(viewsets.ModelViewSet):
    pk = 1
    queryset = Scenario.objects.filter(project__id=pk)
    serializer_class = ScenarioSerializer

    def get_queryset(self):
        qs = super(ProjectScenarioViewSet, self).get_queryset()
        return qs


'''
this is what populates the Scenario table

    provided via /api/projects

but it does something strange and the search doesn't work
'''


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_queryset(self):
        qs = super(ProjectViewSet, self).get_queryset()

        if not (self.request.user.is_superuser or self.request.user.is_staff):
            qs = qs.filter(user=self.request.user)
        return qs

    @action(methods=['get'], detail=True)
    def scenarios(self, request, pk):
        scenarios = Scenario.objects.filter(project__id=pk)
        serializer_class = ScenarioListSerializer

        # serializer = self.serializer_class(self.queryset, many=True)

        serializer = serializer_class(scenarios, many=True)
        return Response(serializer.data)


# also never removed

class ProjectList(ExportMixin, SingleTableView):  # TODO , FilterView
    model = Project
    table_class = tables.ProjectTable
    template_name = 'scenario/generic_list.html'
    exclude_columns = ('edit_column', 'delete_column',)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('accounts:login'))
        return super(ProjectList, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(ProjectList, self).get_queryset()

        if not (self.request.user.is_superuser or self.request.user.is_staff):
            qs = qs.filter(user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context_data = super(ProjectList, self).get_context_data(**kwargs)

        context_data['title'] = 'Projects'
        context_data['header_2'] = 'Projects'
        context_data['active_link'] = 'project'
        context_data['can_add'] = True
        context_data['new_url'] = ''
        return context_data


"""
###############################################################################

    end Project functionality

"""


def test_partial(request):
    cost_item_default_costs = CostItemDefaultCosts.objects.all()

    context = {'something': 'here'}

    if request.is_ajax():
        template = 'test_partial/partial-results.html'
    else:
        template = 'test_partial/result-page.html'
    return render(request, template, {'cost_item_default_costs': cost_item_default_costs}, context)


"""
    TBD
"""


def costitem_defaultcosts_update(request, pk):
    costitem_defaultcosts = get_object_or_404(CostItemDefaultCosts, pk=pk)

    # get a serialized copy of the scenario and in the users browser it will be loaded into the UI
    serializer_class = CostItemDefaultCostSerializer
    serializer = serializer_class(costitem_defaultcosts)

    context_data = {'costitem_defaultcosts': serializer.data, 'IIS_APP_ALIAS': settings.IIS_APP_ALIAS}
    return render(request, 'scenario/costtool/index.html', context_data)


"""

    this gets called by 'SaveDB' AND BY EACH AND EVERY EDIT ON THE UI!!!!
    this is URL scenario_save_url

"""


def scenario_save(request):
    if request.method != 'POST':
        return JsonResponse({'Error': 'Only POST is accepted by scenario_save()'})

    posted_data = json.loads(request.body.decode('utf-8'))

    form_data = json.loads(posted_data)

    # CREATE
    # TODO: remove this - we will do adds using the db, not this UI
    if ('scenario_id' in form_data
            and (form_data['scenario_id'] == 'undefined'
                 or form_data['scenario_id'] == '')):

        try:
            scenario = Scenario.objects.create(
                project_id=form_data['project_id'],
                scenario_title=form_data['siteData']['embedded_scenario']['scenario_title'],
            )

            if not scenario is None:
                form_data['scenario_id'] = scenario.id

            # send it off to be processed
            scenario.process_related_data(form_data['siteData'])

            scenario.save()
        except Exception as error:
            form_data['Error'] = {'Type': type(error).__name__,
                                  'message': "Unexpected error:" + error.args[0],
                                  }

            # DB_SPECIFIC
            if (error.args[
                0] == "UNIQUE constraint failed: scenario_scenario.user_id, scenario_scenario.project_title, scenario_scenario.scenario_title"):
                form_data['Error']['message'] = "Duplicate Project and Scenario Title.  You can only have one " \
                                                + "scenario with the the same Project Title and Scenario Title"
                form_data['Error']['error_dom_id'] = 'scenario_title_validation_error'

                return JsonResponse(form_data)

        form_data['scenario_id'] = scenario.id

        form_data['uiMessage'] = {'redirect_required':
                                      {'reason': 'added',
                                       'scenario_id': scenario.id,
                                       'redirect_to': reverse('scenario:scenario_update', kwargs={'pk': scenario.id})
                                       }
                                  }

    else:  # UPDATE
        # TODO: check that it found the object
        scenario = get_object_or_404(Scenario, pk=form_data['scenario_id'])

        try:
            # send it off to be processed
            scenario.process_related_data(form_data['siteData'])

            scenario.save()

        except Exception as error:
            # don't dump all the form_data content if there is a failure
            # form_data = {}
            form_data['Error'] = {'Type': type(error).__name__,
                                  'message': "1.232 Unexpected error:" + str(error.args[0]),
                                  }
            # DB_SPECIFIC
            if (error.args[
                0] == "UNIQUE constraint failed: scenario_scenario.user_id, scenario_scenario.project_title, scenario_scenario.scenario_title"):
                form_data['Error']['message'] = "Duplicate Project and Scenario Title.  You can only have one " \
                                                + "scenario with the the same Project Title and Scenario Title"
                form_data['Error']['error_dom_id'] = 'scenario_title_validation_error'

            if ('duplicate key value violates unique constraint' in error.args[0]):
                form_data['Error']['message'] = "Duplicate Project and Scenario Title.  You can only have one " \
                                                + "scenario with the the same Project Title and Scenario Title"
                form_data['Error']['error_dom_id'] = 'scenario_title_validation_error'

        # TADA

        serializer_class = EmbeddedProjectSerializer

        project_serializer = serializer_class(scenario.project, many=False)

        form_data['siteData']['project'] = project_serializer.data

        form_data['processing_message'] = 'Successfully Saved'

        cost_item_user_costs = CostItemUserCosts.objects.filter(scenario__id=scenario.id)

        # form_data['user_costs'] = cost_item_user_costs

        serializer_class = CostItemUserCostSerializer

        cost_item_serializer = serializer_class(cost_item_user_costs, many=True)

        form_data['user_costs'] = cost_item_serializer.data

        disclaimer_tx = render_to_string('scenario/results_disclaimer.html')
        form_data['html_result'] = disclaimer_tx + scenario_table_html(scenario)
        # testobj = ScenarioResults()

        # render_to_string(template_name, context, request=request)

    return JsonResponse(form_data)


#
# this is the Structure Cost data in a single html partial table or JSON
#
class StructureCosts(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

    def get(self, request, multiple_pks):
        pass

    def get(self, request, pk, structure_code):

        scenario = get_object_or_404(Scenario, id=pk)
        serializer_class = ScenarioSerializer
        serializer = serializer_class(scenario)
        scenario_data = serializer

        structure = Structures.objects.get(code=structure_code)

        cost_item_default_costs = CostItemDefaultCosts.objects.all().order_by("costitem__sort_nu")

        cost_item_default_factors = CostItemDefaultFactors.objects.filter(structure=structure)

        cost_item_user_costs = CostItemUserCosts.objects.filter(scenario=scenario)

        cost_item_user_assumptions = CostItemUserAssumptions.objects.filter(scenario__id=pk, structure=structure)

        if 'format' in request.query_params and request.query_params['format'] == 'json':
            # return the content as JSON
            return JsonResponse(structure_cost_item_json(structure,
                                                         scenario_data,
                                                         cost_item_default_costs,
                                                         cost_item_default_factors,
                                                         cost_item_user_costs,
                                                         cost_item_user_assumptions,
                                                         ))
        else:
            # return the scenario as an HTML table
            return HttpResponse(structure_cost_item_table_html(structure,
                                                               scenario_data,
                                                               cost_item_default_costs,
                                                               cost_item_default_factors,
                                                               # cost_item_user_costs,
                                                               cost_item_user_assumptions
                                                               ))


#
# this is the Structure Cost data in a single html partial table or JSON
#
# class StructureCostsNEW(APIView):
#     renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
#
#     def get(self, request, multiple_pks):
#         pass
#
#     def get(self, request, pk, structure_code):
#
#         scenario = get_object_or_404(Scenario, id=pk)
#         serializer_class = ScenarioSerializer
#         serializer = serializer_class(scenario)
#         scenario_data = serializer
#
#         structure = Structures.objects.get(code=structure_code)
#
#         cost_item_default_costs = CostItemDefaultCosts.objects.all() # .order_by("costitem__sort_nu")
#
#         cost_item_default_assumptions = CostItemDefaultAssumptions.objects.filter(structure=structure)
#
#         cost_item_user_costs = CostItemUserCosts.objects.filter(scenario=scenario)# .order_by("costitem__sort_nu")
#
#         cost_item_user_assumptions = CostItemUserAssumptions.objects.filter(scenario__id=pk, structure=structure)
#
#         if 'format' in request.query_params and request.query_params['format'] == 'json':
#             # return the content as JSON
#             return JsonResponse(structure_cost_item_json(structure,
#                                                           scenario_data,
#                                                           cost_item_default_costs,
#                                                           cost_item_default_assumptions,
#                                                           cost_item_user_costs,
#                                                           cost_item_user_assumptions,
#                                                           ))
#         else:
#             # return the scenario as an HTML table
#             return HttpResponse(structure_cost_item_table_html(structure,
#                                                               scenario_data,
#                                                               cost_item_default_costs,
#                                                               cost_item_default_assumptions,
#                                                               # cost_item_user_costs,
#                                                               cost_item_user_assumptions))
#
#     """
#         this is the "NEW" version used to get all the costs for a scenario
#     """
#     def get(self, request, pk):
#
#         scenario = get_object_or_404(Scenario, id=pk)
#
#         return JsonResponse(scenario.get_costs())


"""
    convert units between Structure Units and Cost Item units
    i.e. ft2 and square yards, ft2 and AC

"""


def get_unit_conversion(structure_units, cost_item_units):
    conversion_factor = '1'
    structure_units = structure_units.upper()
    cost_item_units = cost_item_units.upper()

    if structure_units == cost_item_units:
        conversion_factor = '1'
    elif structure_units == 'SF':
        if cost_item_units == 'AC':
            conversion_factor = '1/43560'
        elif cost_item_units == 'SY':
            conversion_factor = '1/9'
        elif cost_item_units in ['CY', 'TN']:
            conversion_factor = '1/27'
    elif structure_units == 'CF':
        if cost_item_units == 'AC':
            conversion_factor = '1/43560'
        elif cost_item_units == 'SY':
            conversion_factor = '1/9'
        elif cost_item_units == 'CY':
            conversion_factor = '1/27'
        elif cost_item_units == 'TN':
            conversion_factor = '1/27'
    elif structure_units == 'SY':
        if cost_item_units == 'AC':
            conversion_factor = '1/4840'
        elif cost_item_units == 'CY':
            conversion_factor = '1'
    elif structure_units == 'LF':
        if cost_item_units == 'AC':
            conversion_factor = '1/43560'
        elif cost_item_units == 'SY':
            conversion_factor = '1/9'
        elif cost_item_units == 'CY':
            conversion_factor = '1/27'

    return conversion_factor


"""

    this one gets the result costs (as opposed to the other version used to populate the UI

"""


def structure_cost_item_result_json(structure,
                                    scenario_data,
                                    cost_item_default_costs,
                                    cost_item_default_assumptions,  # this knows which items to check 'by default'
                                    cost_item_user_costs,
                                    # cost_item_user_assumptions,  # this knows which items the user checked

                                    ):
    if structure.classification == 'conventional':
        structure.area = scenario_data['conventional_structures'].value[structure.code]['area']
    else:
        structure.area = scenario_data['nonconventional_structures'].value[structure.code]['area']

    scenario_json = scenario_data.data

    # TODO: not this
    # this has all the assumptions, with the 'structure_code' in there.
    #   scenario_json['cost_item_user_assumptions']
    # cost_item_user_assumptions = scenario_json['cost_item_user_assumptions']

    structure_costs = {'structure': {'code': structure.code,
                                     'name': structure.name,
                                     'area': structure.area,
                                     'units': structure.units,
                                     'units_html': structure.units_html,
                                     },
                       'data': {}}

    cost_item_default_equations = CostItemDefaultEquations.objects.all().order_by("costitem__sort_nu")

    for obj in cost_item_default_equations:
        costitem_code = obj.costitem.code
        structure_costs['data'][costitem_code] = {'equation': obj.equation_tx,
                                                  'units': obj.costitem.units,
                                                  'checked': False,
                                                  'a_area': obj.a_area,
                                                  'z_depth': obj.z_depth,
                                                  'd_density': obj.d_density,
                                                  'n_number': obj.n_number,
                                                  'help_text': obj.help_text
                                                  }

    for obj in cost_item_default_assumptions:
        structure_costs['data'][obj.costitem.code] = {'checked': True,
                                                      'a_area': obj.a_area,
                                                      'n_number': obj.n_number,
                                                      'cost_source': 'rsmeans',
                                                      'unit_cost': 'TBD5',
                                                      'units': obj.costitem.units,
                                                      'equation': obj.construction_cost_factor_equation,
                                                      }

    # first add in the cost_item_user_costs
    for cost_item_user_costs_obj in cost_item_user_costs:
        costitem_code = cost_item_user_costs_obj.costitem.code
        unit_cost = None
        cost_source = None
        if cost_item_user_costs_obj.user_input_cost is not None:
            # note: this is a Money field
            unit_cost = cost_item_user_costs_obj.user_input_cost.amount
        cost_source = cost_item_user_costs_obj.cost_source
        if cost_source == 'user':
            if cost_item_user_costs_obj.user_input_cost is not None:
                # note: this is a Money field
                unit_cost = cost_item_user_costs_obj.user_input_cost.amount

        if not costitem_code in structure_costs['data']:
            structure_costs['data'][costitem_code] = {'checked': False,
                                                      'cost_source': cost_source,
                                                      'unit_cost': unit_cost,
                                                      'equation': 'TBD2'
                                                      }
        else:
            if cost_source == 'user':
                structure_costs['data'][costitem_code]['unit_cost'] = unit_cost
            structure_costs['data'][costitem_code]['cost_source'] = cost_source

    # then add in the default costs to update the non 'user' (cost_source) costs
    for cost_item_default_costs_obj in cost_item_default_costs:
        costitem_code = cost_item_default_costs_obj.costitem.code
        if costitem_code in structure_costs['data']:
            if structure_costs['data'][costitem_code]['cost_source'] != 'user':
                cost_source = structure_costs['data'][costitem_code]['cost_source']
                # the user selected or entered data in assumptions tab, but not in cost tab
                if cost_source == 'TBD1':
                    structure_costs['data'][costitem_code]['cost_source'] = 'rsmeans'
                    cost_source = 'rsmeans'

                unit_cost = None
                if cost_source == 'rsmeans':
                    unit_cost = cost_item_default_costs_obj.rsmeans_va.amount
                elif cost_source == 'db_25_pct':
                    unit_cost = cost_item_default_costs_obj.db_25pct_va.amount
                elif cost_source == 'db_50_pct':
                    unit_cost = cost_item_default_costs_obj.db_50pct_va.amount
                elif cost_source == 'db_75_pct':
                    unit_cost = cost_item_default_costs_obj.db_75pct_va.amount

                structure_costs['data'][costitem_code]['unit_cost'] = unit_cost
        else:
            structure_costs['data'][costitem_code] = {'checked': False,
                                                      'cost_source': 'rsmeans',
                                                      'unit_cost': cost_item_default_costs_obj.rsmeans_va.amount,
                                                      'equation': None
                                                      }

    # now add in the equation
    for cost_item_default_assumptions_obj in cost_item_default_assumptions:
        costitem_code = cost_item_default_assumptions_obj.costitem.code
        structure_costs['data'][costitem_code][
            'equation'] = cost_item_default_assumptions_obj.construction_cost_factor_equation

    """
        TADA - this is the calculation (started on this 2019-07-15)

        I think the way to do it is to find all 'data' that where checked == true
        and then replace all the components of the equation as strings and then eval it

    """
    for cost_item in structure_costs['data']:
        cost_item_data = structure_costs['data'][cost_item]

        if cost_item_data['checked'] is True:

            factors = {
                'a_area': None,
                'z_depth': None,
                'd_density': None,
                # 'r_ratio': None,
                'n_number': None,
            }

            for factor in factors:
                val = str(cost_item_data[factor])
                if len(val) == 0 or val == 'None':
                    factors[factor] = '1'

            # # this is commonly used to scale the area
            # sizing_factor_k = str(cost_item_data['sizing_factor_k'])
            # if len(sizing_factor_k) == 0 or sizing_factor_k == 'None':
            #     sizing_factor_k = '1'
            #
            # # this is used to (ignore the area) and just use a number of 'each' items
            # # for example, a feature might have an area of 1000ft2, but contain 60 ft of pipe
            # # so the total pipe used is n = 60 and the equation is =sizing_factor_n*$
            # sizing_factor_n = str(cost_item_data['sizing_factor_n'])
            # if len(sizing_factor_n) == 0 or sizing_factor_n == 'None':
            #     sizing_factor_n = '1'

            structure_units = structure_costs['structure']['units']
            cost_item_units = cost_item_data['units']
            unit_conversion = 1
            if structure_units != cost_item_units:
                unit_conversion = get_unit_conversion(structure_units, cost_item_units)

            # equation = cost_item_data['equation']
            # if equation == 'TBD1':
            #     if cost_item in [ 'pipe', 'outlet_structure']:
            #         equation = '=sizing_factor_n*$'
            #     elif cost_item_units in ['CY/TN']:
            #         equation = '=x*sizing_factor_k*sizing_factor_n*$'
            #     else:
            #         equation = '=x*sizing_factor_k*$'
            #     cost_item_data['equation'] = equation

            # TODO: figure out where to put this
            # equation = equation + '*' + 'unit_conversion'

            equation = equation.replace('=', '')
            # equation = equation.replace('x', str(structure.area))
            equation = equation.replace('x', '(' + str(structure.area) + '*' + str(unit_conversion) + ')')

            # equation = equation.replace('unit_conversion', str(unit_conversion))

            equation = equation.replace('area', factors['a_area'])
            equation = equation.replace('depth', factors['z_depth'])
            equation = equation.replace('density', factors['d_density'])
            # equation = equation.replace('ratio', factors['r_ratio'])
            equation = equation.replace('number', factors['n_number'])

            equation = equation.replace('$', str(cost_item_data['unit_cost']))

            cost_item_data['equation_calc'] = equation

            try:
                cost_amount = eval(equation)
                cost_item_data['equation_value'] = '{:,.2f}'.format(cost_amount)
                # cost_item_data['unit_cost_formatted'] = '${:,.2f}'.format(cost_item_data['unit_cost'])
            except:
                cost_amount = equation
                cost_item_data['equation_value'] = cost_amount

    return structure_costs


"""

    return JSON to cost tool for processing by javascript to populate 
    the 'Structure/Cost Item Costs' tab
    
    ajax call to 
    /scenario/<scenario_id>/structure_costs/<structure_code>/?format=json

"""


def structure_cost_item_json(structure,
                             scenario_data,
                             cost_item_default_costs,
                             cost_item_default_factors,  # this knows which items to check 'by default'
                             cost_item_user_costs,
                             cost_item_user_assumptions,  # this knows which items the user checked

                             ):
    cost_item_default_equations = CostItemDefaultEquations.objects.all().order_by("costitem__sort_nu")

    structure.area = 0
    if structure.classification == 'conventional':
        if scenario_data['conventional_structures'].value is not None:
            structure.area = scenario_data['conventional_structures'].value[structure.code]['area']
    else:
        if scenario_data['nonconventional_structures'].value is not None:
            structure.area = scenario_data['nonconventional_structures'].value[structure.code]['area']

    scenario_json = scenario_data.data

    # TODO: make this legible. I can't figure out what is going on.
    # this has all the assumptions, with the 'structure_code' in there.
    #   scenario_json['cost_item_user_assumptions']
    # cost_item_user_assumptions = scenario_json['cost_item_user_assumptions']

    structure_costs = {'structure': {'code': structure.code,
                                     'name': structure.name,
                                     'area': structure.area,
                                     'units': structure.units,
                                     'units_html': structure.units_html,
                                     },
                       'data': {}}

    """
        there are 3 sources of 'Structure Costs' data 
            1. Cost Item User Assumptions (data entered on Structure Costs page stored in ...
            2. Cost Item Default Assumptions (data loaded from CSV into table/model CostItemDefaultAssumptions)
    """

    '''
        these are cost items that the usr edited on Structure Costs 
        edit can be
        1. checked cost item
        2. set value in Factor Assumptions, Sizing Factor (k) or Sizing Factor (n)
    '''
    # jab new - get equation from CostItemDefaultEquations table
    for obj in cost_item_default_equations:
        costitem_code = obj.costitem.code
        structure_costs['data'][costitem_code] = {'equation': obj.equation_tx,
                                                  'units': obj.costitem.units,
                                                  'checked': False,
                                                  'a_area': obj.a_area,
                                                  'z_depth': obj.z_depth,
                                                  'd_density': obj.d_density,
                                                  'n_number': obj.n_number,
                                                  'help_text': obj.help_text
                                                  }

    seen_costitem_codes = set()
    if len(cost_item_user_assumptions) > 0:
        for obj in cost_item_user_assumptions:
            costitem_code = obj.costitem.code

            seen_costitem_codes.add(costitem_code)

            structure_costs['data'][costitem_code]['checked'] = obj.checked
            structure_costs['data'][costitem_code]['a_area'] = obj.a_area
            structure_costs['data'][costitem_code]['z_depth'] = obj.z_depth
            structure_costs['data'][costitem_code]['d_density'] = obj.d_density
            structure_costs['data'][costitem_code]['n_number'] = obj.n_number
    # else:
    for obj in cost_item_default_factors:
        costitem_code = obj.costitem.code

        if costitem_code not in seen_costitem_codes:
            structure_costs['data'][costitem_code]['checked'] = True
            structure_costs['data'][costitem_code]['a_area'] = obj.a_area
            structure_costs['data'][costitem_code]['z_depth'] = obj.z_depth
            structure_costs['data'][costitem_code]['d_density'] = obj.d_density
            structure_costs['data'][costitem_code]['n_number'] = obj.n_number

    '''
        these are cost items that are set as defaults for this Structure 
        
        TODO: this is not needed anymore - it is replaced with the code earlier
    '''
    # pass
    # for obj in cost_item_default_assumptions:
    #     costitem_code = obj.costitem.code
    # structure_costs['data'][costitem_code]['checked'] = obj.checked
    # structure_costs['data'][costitem_code]['factor_assumption_tx'] = obj.factor_assumption_tx
    # structure_costs['data'][costitem_code]['sizing_factor_k'] = obj.sizing_factor_k
    # structure_costs['data'][costitem_code]['sizing_factor_n'] = obj.sizing_factor_n

    '''
        new change to use defaults from CostItemDefaultEquations table
    '''
    # for obj in cost_item_default_equations:
    #     costitem_code = obj.costitem.code
    #     for field_nm in (
    #                      'a_area',
    #                      'z_depth',
    #                      'd_density',
    #                      'r_ratio',
    #                      'n_number',
    #                      'help_text'):
    #         if getattr(obj, field_nm):
    #             structure_costs['data'][costitem_code][field_nm] = getattr(obj, field_nm)

    # first add in the cost_item_user_costs
    for obj in cost_item_user_costs:
        costitem_code = obj.costitem.code

        cost_source = None
        unit_cost = None
        # unit_cost_formatted = ''

        if obj.user_input_cost is not None:
            # note: this is a Money field
            unit_cost = obj.user_input_cost.amount

        cost_source = obj.cost_source

        """
            the only cost data that is available here is the 'user' input costs - not
            rsmean, db25, db50, etc.
        """
        if cost_source == 'user':
            if obj.user_input_cost is not None:
                # note: this is a Money field and this just uses the decimal part
                unit_cost = obj.user_input_cost.amount
                # unit_cost_formatted = '${:,.2f}'.format(obj.user_input_cost.amount)

        # add the user costs data
        structure_costs['data'][costitem_code]['cost_source'] = cost_source
        structure_costs['data'][costitem_code]['unit_cost'] = unit_cost
        # structure_costs['data'][costitem_code]['unit_cost_formatted'] = unit_cost_formatted
        structure_costs['data'][costitem_code]['o_and_m_pct'] = int(obj.o_and_m_pct)
        structure_costs['data'][costitem_code]['replacement_life'] = int(obj.replacement_life or "0")

    # then add in the default costs to update the non 'user' (cost_source) costs

    for obj in cost_item_default_costs:
        costitem_code = obj.costitem.code

        # make the blank structure
        if not costitem_code in structure_costs['data']:
            structure_costs['data'][costitem_code]['cost_source'] = 'rsmeans'

        if not 'o_and_m_pct' in structure_costs['data'][costitem_code]:
            structure_costs['data'][costitem_code]['o_and_m_pct'] = obj.o_and_m_pct
        if not 'replacement_life' in structure_costs['data'][costitem_code]:
            structure_costs['data'][costitem_code]['replacement_life'] = obj.replacement_life

        cost_source = 'rsmeans'

        if 'cost_source' in structure_costs['data'][costitem_code]:
            cost_source = structure_costs['data'][costitem_code]['cost_source']

        if cost_source != 'user':
            unit_cost = None
            if cost_source == 'rsmeans':
                unit_cost = obj.rsmeans_va.amount
            elif cost_source == 'db_25_pct':
                unit_cost = obj.db_25pct_va.amount
            elif cost_source == 'db_50_pct':
                unit_cost = obj.db_50pct_va.amount
            elif cost_source == 'db_75_pct':
                unit_cost = obj.db_75pct_va.amount

            structure_costs['data'][costitem_code]['unit_cost'] = unit_cost
            # structure_costs['data'][costitem_code]['unit_cost_formatted'] = '${:,.2f}'.format(unit_cost)

    """
        TADA - this is the calculation (started on this 2019-07-15)
        
        I think the way to do it is to find all 'data' that where checked == true
        and then replace all the components of the equation as strings and then eval it

    """
    for cost_item in structure_costs['data']:
        cost_item_data = structure_costs['data'][cost_item]

        if cost_item_data['checked'] is True:

            factors = {
                'a_area': 1,
                'z_depth': 1,
                'd_density': 1,
                # 'r_ratio': 1,
                'n_number': 1,
            }

            for factor in factors:
                val = str(cost_item_data[factor])
                if len(val) == 0 or val == 'None':
                    factors[factor] = '1'
                else:
                    factors[factor] = val

            structure_units = structure_costs['structure']['units']
            cost_item_units = cost_item_data['units']
            unit_conversion = 1
            if structure_units != cost_item_units:
                unit_conversion = get_unit_conversion(structure_units, cost_item_units)

            equation = cost_item_data['equation']

            # TODO: figure out where to put this
            # equation = equation + '*' + 'unit_conversion'

            equation = equation.replace('=', '')
            # equation = equation.replace('x', str(structure.area))
            # equation = equation.replace('unit_conversion', str(unit_conversion))

            equation = equation.replace('x', '(' + str(structure.area) + '*' + str(unit_conversion) + ')')

            equation = equation.replace('area', str(factors['a_area']))
            equation = equation.replace('depth', str(factors['z_depth']))
            equation = equation.replace('density', str(factors['d_density']))
            # equation = equation.replace('ratio', str(factors['r_ratio']))
            equation = equation.replace('number', str(factors['n_number']))

            equation = equation.replace('$', str(cost_item_data['unit_cost']))

            cost_item_data['equation_calc'] = equation

            try:
                cost_amount = eval(equation)
                cost_item_data['equation_value'] = '{:,.2f}'.format(cost_amount)
                cost_item_data['construction_cost'] = round(cost_amount, 2)
                # cost_item_data['unit_cost_formatted'] = '${:,.2f}'.format(cost_item_data['unit_cost'])
            except:
                cost_amount = equation
                cost_item_data['equation_value'] = 'err:' + cost_amount
                cost_item_data['construction_cost'] = 999  # stub used for debugging error

    """
         NOW - this is the calculation from post-construction costs (started on this 2019-11-12)

         I think the way to do it is to find all 'data' that where checked == true
         and then replace all the components of the equation as strings and then eval it

     """

    # these are 'Scenario' level values set on the 'Project-Scenario Description' page
    planning_and_design_factor = int(scenario_data['embedded_scenario'].value['planning_and_design_factor'])
    study_life = int(scenario_data['embedded_scenario'].value['study_life'])
    discount_rate = float(scenario_data['embedded_scenario'].value['discount_rate'])

    """
        these are 'Structure' level values for each 'Cost Item' add the costs for each cost item
    """
    for cost_item in structure_costs['data']:
        cost_item_data = structure_costs['data'][cost_item]
        if cost_item_data['checked'] is True:
            construction_cost = round(float(cost_item_data.pop('construction_cost')), 2)
            planning_and_design_costs = round(construction_cost * planning_and_design_factor * 0.01, 2)

            replacement_life = cost_item_data['replacement_life']
            o_and_m_pct = cost_item_data['o_and_m_pct']

            # =(G$116*(G$115/100))/(1+($D$13/100))^$C120
            # = (construction_cost * (o_and_m_pct/100)) / (1 + (discount_rate/100))^i
            o_and_m_costs = 0
            if o_and_m_pct != 0:
                for i in range(1, study_life + 1, 1):
                    o_and_m_costs += (construction_cost * (o_and_m_pct / 100)) / (1 + (discount_rate / 100)) ** i

            number_of_replacements = 0
            if replacement_life != 0 and study_life > replacement_life:
                number_of_replacements = int(round(study_life / replacement_life, 0))

            value_of_first_replacement = 0
            replacement_years = []
            replacement_costs = 0
            if number_of_replacements == 1:
                replacement_years.append(replacement_life)
                replacement_costs = round((construction_cost / (1 + (discount_rate / 100)) ** replacement_life), 2)
                value_of_first_replacement = replacement_costs
            elif number_of_replacements > 0:
                for i in range(int(study_life / int(number_of_replacements)), study_life + 1,
                               int(study_life / int(number_of_replacements))):
                    replacement_years.append(i)
                    replacement_cost = round(construction_cost / (1 + (discount_rate / 100)) ** i, 2)
                    replacement_costs += replacement_cost
                    # replacements.append(replacement_cost)
                    if value_of_first_replacement == 0:
                        value_of_first_replacement = replacement_costs

            # =IF(U225=0,0,INDEX(U$230:U$329,MATCH(U$223,$C$230:$C$329,)))
            # =IF(number_of_replacements==0,0,INDEX(U$230:U$329,MATCH(replacement_life,$C$230:$C$329,)))
            structure_costs['data'][cost_item]['costs'] = {
                'construction': construction_cost,
                'planning_and_design': planning_and_design_costs,
                'o_and_m': round(o_and_m_costs, 2),
                'first_replacement': value_of_first_replacement,
                'replacement': round(replacement_costs, 2),
                'replacement_years': replacement_years,
            }

    return structure_costs

    # structure_costs['data'][costitem_code] = {'checked': False,
    #                                                           'cost_source': cost_source,
    #                                                           'unit_cost': unit_cost,
    #                                                           'unit_cost_formatted': '${:,.2f}'.format(unit_cost),
    #                                                           'equation': 'TBD2'
    #                                                           }


# else:
#     # if cost_source == 'user':
#     #     structure_costs['data'][costitem_code]['unit_cost'] = unit_cost
#     #     structure_costs['data'][costitem_code]['unit_cost_formatted'] = '${:,.2f}'.format(unit_cost)
#     #     structure_costs['data'][costitem_code]['cost_source'] = cost_source
#     #     structure_costs['data'][costitem_code]['equation'] = 'TBD3'
#     # else:
#     if not costitem_code in structure_costs['data']:
#         for ci in cost_item_default_costs:
#             if ci.costitem.code == costitem_code:
#                 if cost_source == 'rsmeans':
#                     unit_cost = ci.rsmeans_va.amount
#                 elif cost_source == 'db_25_pct':
#                     unit_cost = ci.db_25pct_va.amount
#                 elif cost_source == 'db_50_pct':
#                     unit_cost = ci.db_50pct_va.amount
#                 elif cost_source == 'db_75_pct':
#                     unit_cost = ci.db_75pct_va.amount
#
#                 structure_costs['data'][costitem_code] = {'checked': False,
#                                                           'cost_source': cost_source,
#                                                           'unit_cost': unit_cost,
#                                                           'unit_cost_formatted': '${:,.2f}'.format(unit_cost),
#                                                           'equation': 'TBD4'
#                                                           }
#
#                 break

#
# this is the also scenario data in a single html partial table
#
def structure_cost_item_table_html(structure,
                                   scenario_data,
                                   cost_item_default_costs,

                                   structure_cost_items_data,  # TODO change to whatever this should be
                                   cost_item_user_assumptions
                                   ):
    template_name = "scenario/includes/partial_structure_costs.html"
    if structure.classification == 'conventional':
        structure.area = scenario_data['conventional_structures'].value[structure.code]['area']
    else:
        structure.area = scenario_data['nonconventional_structures'].value[structure.code]['area']

    if cost_item_user_assumptions.count() > 0:
        for cost_item_default_costs_obj in cost_item_default_costs:
            for cost_item_user_assumptions_obj in cost_item_user_assumptions:
                if cost_item_user_assumptions_obj.structure.code == structure.code:
                    if cost_item_default_costs_obj.costitem.code == cost_item_user_assumptions_obj.costitem.code:
                        cost_item_default_costs_obj.checked = cost_item_user_assumptions_obj.checked
                        cost_item_default_costs_obj.conversion_factor = cost_item_user_assumptions_obj.conversion_factor
                        cost_item_default_costs_obj.factor_assumption_tx = cost_item_user_assumptions_obj.factor_assumption_tx
                        cost_item_default_costs_obj.sizing_factor_k = cost_item_user_assumptions_obj.sizing_factor_k
                        cost_item_default_costs_obj.sizing_factor_n = cost_item_user_assumptions_obj.sizing_factor_n
                        cost_item_default_costs_obj.construction_cost_factor_equation = cost_item_user_assumptions_obj.construction_cost_factor_equation
    else:
        # this puts a flag on the item use to check it by default in the template
        for cost_item_default_costs_obj in cost_item_default_costs:
            for structure_cost_items_data_obj in structure_cost_items_data:
                if structure_cost_items_data_obj.structure.code == structure.code:
                    if cost_item_default_costs_obj.costitem.code == structure_cost_items_data_obj.costitem.code:
                        cost_item_default_costs_obj.checked = True

                        # print("for " + structure_code + ' checked ' + structure_cost_items_data_obj.costitem.code)

    context = {
        'structure': structure,
        'scenario': scenario_data,
        'cost_item_default_costs': cost_item_default_costs,
        'structure_cost_items': structure_cost_items_data,
    }

    return render_to_string(template_name, context)


#
# this is the Structure Help returns a single html partial table
#
class StructureHelp(APIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, multiple_pks):
        pass

    def get(self, request, structure_code):

        structure_meta = Structures.objects.filter(code=structure_code)
        if len(structure_meta) == 0:
            structure_meta = Structures.objects.all()
        else:
            structure_meta = structure_meta[0]

        # return the scenario as an HTML table
        return HttpResponse(structure_help_html(structure_meta, structure_code))


#
# TBD
#
def structure_help_html(structure_meta, structure_code):
    template_name = "scenario/includes/partial_structure_help.html"
    context = {
        'structure_code': structure_code,
        'structure_meta': structure_meta,
    }
    return render_to_string(template_name, context)


#
# this is the Structure Cost Help returns a single html partial table
#
class CostItemHelp(APIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, multiple_pks):
        pass

    def get(self, request, costitem_code):
        costitem_meta = CostItem.objects.filter(code=costitem_code)
        if len(costitem_meta) == 0:
            costitem_meta = CostItem.objects.all()
        else:
            costitem_meta = costitem_meta[0]

        # return the scenario as an HTML table
        return HttpResponse(costitem_help_html(costitem_meta, costitem_code))


#
# this is the also scenario data in a single html partial table
#
def costitem_help_html(costitem_meta, costitem_code):
    template_name = "scenario/includes/partial_costitem_help.html"
    context = {
        'costitem_code': costitem_code,
        'costitem_meta': costitem_meta,
    }
    return render_to_string(template_name, context)


class CompareScenarioResults(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "scenario/results_compare.html"

    def get(self, request, multiple_pks):
        pass

    def get(self, request):
        scenarios = {}
        id_tx = request.query_params['id']
        ids = id_tx.split(',')
        for id in ids:
            scenario = get_object_or_404(Scenario, pk=id)
            scenario_table = scenario_table_html(scenario)
            scenarios[id] = {'id': id, 'html': scenario_table, 'data': scenario}

        left_scenario = scenarios[ids[0]]['data']
        right_scenario = scenarios[ids[1]]['data']

        comparison_column_html = comparison_column(ids, left_scenario, right_scenario)

        comparison = {'html': comparison_column_html}

        context = {'scenarios': scenarios,
                   'comparison': comparison,
                   'IIS_APP_ALIAS': settings.IIS_APP_ALIAS}
        #
        #
        return Response(context)


class CompareScenarioColumn(APIView):

    def get(self, request, multiple_pks):
        pass

    def get(self, request):
        id_tx = request.query_params['id']
        ids = id_tx.split(',')

        left_scenario = get_object_or_404(Scenario, pk=ids[0])
        right_scenario = get_object_or_404(Scenario, pk=ids[1])

        comparison_column_html = comparison_column(ids, left_scenario, right_scenario)

        return HttpResponse(comparison_column_html)


#
# this is the scenario data in a single html partial table
#
class ScenarioResults(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "scenario/results.html"

    def get(self, request, multiple_pks):
        pass

    def get(self, request, pk):
        scenario = get_object_or_404(Scenario, pk=pk)

        # return the scenario as an HTML table
        # disclaimer_tx = '<p>Hello World!</p>'
        disclaimer_tx = render_to_string('scenario/results_disclaimer.html')

        return HttpResponse(disclaimer_tx + scenario_table_html(scenario))


#
# generate the Results table and return as an HTML string (make sure this is true)
#
def comparison_column(ids, left_scenario, right_scenario):
    # this is templates/scenario/results
    template_name = "scenario/comparison_column.html"

    left = left_scenario
    right = right_scenario

    left_costs = left.get_costs()
    right_costs = right.get_costs()

    diff = {'design_elements': False}
    if left.nutrient_req_met != right.nutrient_req_met \
            or left.captures_90pct_storm != right.captures_90pct_storm \
            or left.meets_peakflow_req != right.meets_peakflow_req:
        diff['design_elements'] = True

    diff['planning_and_design'] = False
    if left.planning_and_design_factor != right.planning_and_design_factor \
            or left.study_life != right.study_life \
            or left.discount_rate != right.discount_rate:
        diff['planning_and_design'] = True

    diff['pervious_area'] = left.pervious_area or 0 - right.pervious_area or 0
    diff['impervious_area'] = left.impervious_area or 0 - right.impervious_area or 0

    diff['pervious'] = False
    if left.impervious_area != right.impervious_area:
        diff['pervious'] = True

    left_total = left_costs['project_life_cycle_costs']['total']
    right_total = right_costs['project_life_cycle_costs']['total']

    costs = {}
    costs['construction'] = left_total['construction'] - right_total['construction']
    costs['planning_and_design'] = left_total['planning_and_design'] - right_total['planning_and_design']
    costs['o_and_m'] = left_total['o_and_m'] - right_total['o_and_m']
    costs['replacement'] = left_total['replacement'] - right_total['replacement']
    costs['total'] = costs['construction'] + costs['planning_and_design'] + \
                     costs['o_and_m'] + costs['replacement']

    diff['project_life_cycle_costs'] = costs

    left_total = left_costs['project_life_cycle_costs']['conventional']['costs']
    right_total = right_costs['project_life_cycle_costs']['conventional']['costs']

    costs = {}
    costs['construction'] = left_total['construction'] - right_total['construction']
    costs['planning_and_design'] = left_total['planning_and_design'] - right_total['planning_and_design']
    costs['o_and_m'] = left_total['o_and_m'] - right_total['o_and_m']
    costs['replacement'] = left_total['replacement'] - right_total['replacement']
    costs['total'] = costs['construction'] + costs['planning_and_design'] + \
                     costs['o_and_m'] + costs['replacement']

    diff['conventional'] = costs

    left_total = left_costs['project_life_cycle_costs']['nonconventional']['costs']
    right_total = right_costs['project_life_cycle_costs']['nonconventional']['costs']

    costs = {}
    costs['construction'] = left_total['construction'] - right_total['construction']
    costs['planning_and_design'] = left_total['planning_and_design'] - right_total['planning_and_design']
    costs['o_and_m'] = left_total['o_and_m'] - right_total['o_and_m']
    costs['replacement'] = left_total['replacement'] - right_total['replacement']
    costs['total'] = costs['construction'] + costs['planning_and_design'] + \
                     costs['o_and_m'] + costs['replacement']

    diff['nonconventional'] = costs

    areal_features = {
        'total_area': 0,
        'item_list': {}
    }
    serializer_class = ScenarioSerializer
    left_serializer = serializer_class(left_scenario)
    right_serializer = serializer_class(right_scenario)

    diff_area_sum = 0
    for r, left_obj in left_serializer.data['areal_features'].items():
        right_obj = right_serializer.data['areal_features'][r]
        right_area = right_obj['area'] if right_obj['checkbox'] is True else 0
        left_area = left_obj['area'] if left_obj['checkbox'] is True else 0
        diff_area = left_area or 0 - right_area or 0
        diff_area_sum += diff_area
        areal_features['item_list'][r] = {'label': right_obj['label'], 'area': diff_area}
        if r == 'stormwater_management_feature':
            areal_features['item_list'][r]['project_land_unit_cost'] = left_scenario.project.land_unit_cost
            areal_features['item_list'][r]['project_land_cost_diff'] = (
                                                                                   left_area or 0 - right_area or 0) * left_scenario.project.land_unit_cost

    areal_features['total_area'] = diff_area_sum
    diff['areal_features'] = areal_features

    context = {
        'diff': diff,
    }

    return render_to_string(template_name, context)


#
# generate the Results table and return as an HTML string (make sure this is true)
#
def scenario_table_html(scenario):
    # this is templates/scenario/results
    template_name = "scenario/results.html"

    # get a serialized copy of the scenario and in the users browser
    # it will be loaded into the Results tab
    serializer_class = ScenarioSerializer
    serializer = serializer_class(scenario)

    scenarioTemplate = Scenario.templateScenario

    # this holds calculated values used in the tables but not stored in a
    # scenario variable

    sum_values = {}

    areal_features_sum_area = 0
    conventional_structure_sum_area = 0
    nonconventional_structure_sum_area = 0

    if serializer.data['areal_features']:

        labels = scenarioTemplate['siteData']['areal_features']['labels']

        for r, obj in serializer.data['areal_features'].items():

            if obj['checkbox'] == True and obj['area'] != "0" and obj['area'] != None:
                areal_features_sum_area += int(float(obj['area']))
                obj['label'] = labels[r]
            else:
                obj['area'] = 0
                obj['label'] = labels[r]

    sum_values['areal_features_sum_area'] = areal_features_sum_area

    pervious_area = 0
    impervious_area = 0
    try:
        pervious_area = int(float(serializer.data['embedded_scenario']['pervious_area']))
    except:
        pass
    try:
        impervious_area = int(float(serializer.data['embedded_scenario']['impervious_area']))
    except:
        pass

    sum_values['pervious_impervious_area'] = pervious_area + impervious_area

    # load the labels for structures
    labels = scenarioTemplate['siteData']['conventional_structures']['labels']
    if serializer.data['conventional_structures'] is not None:
        for r, obj in serializer.data['conventional_structures'].items():
            if obj['checkbox'] == True and obj['area'] != "0" and obj['area'] != None:
                conventional_structure_sum_area += int(float(obj['area']))

            try:
                obj['label'] = labels[r]
            except:
                obj['label'] = r
    sum_values['conventional_structure_sum_area'] = conventional_structure_sum_area

    labels = scenarioTemplate['siteData']['nonconventional_structures']['labels']
    if serializer.data['nonconventional_structures'] is not None:
        for r, obj in serializer.data['nonconventional_structures'].items():
            if obj['checkbox'] == True and obj['area'] != "0" and obj['area'] != None:
                nonconventional_structure_sum_area += int(float(obj['area']))

            obj['label'] = labels[r]
    sum_values['nonconventional_structure_sum_area'] = nonconventional_structure_sum_area

    # load the labels for Cost Items
    cost_item_default_costs = CostItemDefaultCosts.objects.all().order_by("costitem__sort_nu")

    cost_item_user_cost = serializer.data['cost_item_user_costs']

    cost_item_user_cost_dict = {}
    for o in cost_item_user_cost:
        cost_item_user_cost_dict[o['costitem_code']] = o

    cost_item_costs = []

    for cost_item_obj in cost_item_default_costs:
        code = cost_item_obj.costitem.code
        cost_source_tx = 'Eng. Est.'

        unit_cost = cost_item_obj.rsmeans_va
        base_year = ''
        replacement_life = cost_item_obj.replacement_life
        replacement_life_source = 'Default'
        o_and_m_pct = cost_item_obj.o_and_m_pct
        o_and_m_pct_source = 'Default'

        if code in cost_item_user_cost_dict:
            # update stuff
            if cost_item_user_cost_dict[code]['replacement_life'] != replacement_life:
                replacement_life = cost_item_user_cost_dict[code]['replacement_life']
                replacement_life_source = 'User'

            if cost_item_user_cost_dict[code]['o_and_m_pct'] != o_and_m_pct:
                o_and_m_pct = cost_item_user_cost_dict[code]['o_and_m_pct']
                o_and_m_pct_source = 'User'

            if cost_item_user_cost_dict[code]['cost_source'] == 'user':
                cost_source_tx = 'User'
                if cost_item_user_cost_dict[code]['user_input_cost'] is None:
                    unit_cost = Money(0.00, 'USD')
                else:
                    unit_cost = Money(cost_item_user_cost_dict[code]['user_input_cost'], 'USD')
                base_year = cost_item_user_cost_dict[code]['base_year']
            # TBD the cost_source text should match, or almost match, the variable name
            # TODO change text to db_25pct_va or at least db_25pct
            elif cost_item_user_cost_dict[code]['cost_source'] == 'db_25_pct':
                cost_source_tx = 'DB - 25%'
                unit_cost = cost_item_obj.db_25pct_va
            elif cost_item_user_cost_dict[code]['cost_source'] == 'db_50_pct':
                cost_source_tx = 'DB - 50%'
                unit_cost = cost_item_obj.db_50pct_va
            elif cost_item_user_cost_dict[code]['cost_source'] == 'db_75_pct':
                cost_source_tx = 'DB - 75%'
                unit_cost = cost_item_obj.db_75pct_va

        cost_item_costs.append({
            'code': cost_item_obj.costitem.code,
            'label': cost_item_obj.costitem.name,
            'units': cost_item_obj.costitem.units,

            'cost_source': cost_source_tx,
            'unit_cost': unit_cost.amount,
            'base_year': base_year,
            'replacement_life': replacement_life,
            'replacement_life_source': replacement_life_source,
            'o_and_m_pct': o_and_m_pct,
            'o_and_m_pct_source': o_and_m_pct_source
        })

    for cost_item_obj in cost_item_costs:
        code = cost_item_obj['code']

        if code in cost_item_user_cost_dict:
            # update stuff
            cost_item_obj['replacement_life'] = cost_item_user_cost_dict[code]['replacement_life']
            cost_item_obj['o_and_m_pct'] = cost_item_user_cost_dict[code]['o_and_m_pct']

            if cost_item_user_cost_dict[code]['cost_source'] == 'user':
                cost_item_obj['cost_source'] = 'User'
                # change the value to a Money
                cost_item_obj['unit_cost'] = Money(cost_item_user_cost_dict[code]['user_input_cost'] or '0.00', 'USD').amount
                cost_item_obj['base_year'] = cost_item_user_cost_dict[code]['base_year']

    #
    # TODO: now create the computed costs part
    #
    cost_results = scenario.get_costs()

    # dictionary (should be a set) to record which cost items are used
    # in the final results.  later used to remove cost item unit costs if they are not used
    cost_items_seen = set()
    for classification in ['conventional', 'nonconventional']:
        for structure in cost_results[classification]['structures']:
            for cost_item in cost_results[classification]['structures'][structure]['cost_data']:
                cost_items_seen.add(cost_item)

    # remove cost items if they are not used in any cost calculation
    final_cost_item_costs = []
    for cost_item in cost_item_costs:
        if cost_item['code'] in cost_items_seen:
            final_cost_item_costs.append(cost_item)

    project_life_cycle_costs = cost_results.pop('project_life_cycle_costs')
    structure_life_cycle_costs = cost_results.pop('structure_life_cycle_costs')
    cost_results_additional = cost_results

    context = {'scenario': serializer.data,
               'cost_item_costs': final_cost_item_costs,
               'cost_results': cost_results,
               'cost_results_additional': cost_results_additional,
               'sum_values': sum_values,
               'structure_life_cycle_costs': structure_life_cycle_costs,
               'project_life_cycle_costs': project_life_cycle_costs}

    return render_to_string(template_name, context)


class ScenarioExcelResults(generic.View):
    """
    #
    # this is the Excel export function to return the scenario in Excel
    #
    # NOTE: this needs to be redone so that multiple results can be exported to a single workbook
    #
    #
    # created on 2021-11-05
    #
    """
    def get(self, request, pk):
        # create and populate the workbook and return it as an output stream
        output = scenario_workbook([pk, ])

        # Set up the Http response.
        filename = 'scenario_results.xlsx'
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response


class CompareScenarioExcelResults(APIView):

    def get(self, request, multiple_pks):
        pass

    def get(self, request):
        id_tx = request.query_params['id']
        ids = id_tx.split(',')

        # create and populate the workbook and return it as an output stream
        output = scenario_workbook(ids)

        # Set up the Http response.
        filename = 'scenario_results.xlsx'
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response


class ScenarioExtendedExcelReport(APIView):
    """
        this is the wide and very complex export of all the data into a spreadsheet

    """
    def get(self, request, multiple_pks):
        pass

    def get(self, request):
        id_tx = request.query_params['id']
        ids = id_tx.split(',')

        # create and populate the workbook and return it as an output stream
        output = scenario_extended_excel_report(ids)

        # Set up the Http response.
        filename = 'scenario_extended_results.xlsx'
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response


"""
    this populates the workbook on the output stream provides and using the scenario_id provided

"""


def scenario_workbook(scenario_ids):
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()

    # Even though the final file will be in memory the module uses temp
    # files during assembly for efficiency. To avoid this on servers that
    # don't allow temp files, for example the Google APP Engine, set the
    # 'in_memory' Workbook() constructor option as shown in the docs.

    workbook = xlsxwriter.Workbook(output)

    # build up all the formats required
    formats = create_formats(workbook)

    worksheet = workbook.add_worksheet()

    i = 0
    for id in scenario_ids:
        # add the leftmost scenario
        start_col = i
        populate_workbook(workbook, worksheet, id, formats, start_col)
        i += 5

    # Close the workbook before sending the data.
    workbook.close()

    # Rewind the buffer.
    output.seek(0)

    return output


"""
    this populates the workbook on the output stream provides and using the scenario_id provided
    this is the wide version of the export
"""


def scenario_extended_excel_report(scenario_ids):
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()

    # Even though the final file will be in memory the module uses temp
    # files during assembly for efficiency. To avoid this on servers that
    # don't allow temp files, for example the Google APP Engine, set the
    # 'in_memory' Workbook() constructor option as shown in the docs.

    workbook = xlsxwriter.Workbook(output)

    # build up all the formats required
    formats = create_formats(workbook)

    worksheet = workbook.add_worksheet()

    i = 0
    for id in scenario_ids:
        # add the leftmost scenario
        start_row = i
        populate_scenario_extended_excel_report_workbook(workbook, worksheet, id, formats, start_row)
        i += 1

    # Close the workbook before sending the data.
    workbook.close()

    # Rewind the buffer.
    output.seek(0)

    return output


def create_formats(workbook):
    # helper for reusing partial formats
    def copy_format(book, fmt):
        properties = [f[4:] for f in dir(fmt) if f[0:4] == 'set_']
        dft_fmt = book.add_format()
        return book.add_format(
            {k: v for k, v in fmt.__dict__.items() if k in properties and dft_fmt.__dict__[k] != v})

    # NOTE: store these in a dictionary so they can be passed to a function easily
    formats = {}

    # Add a bold format to use to highlight cells.
    formats['bold'] = workbook.add_format({'bold': True})

    formats['label_col'] = workbook.add_format()
    formats['label_col'].set_border(1)

    formats['input_col'] = workbook.add_format({'bg_color': 'DDEBF7', 'align': 'right'})  # light blue
    formats['input_col'].set_top(1)
    formats['input_col'].set_bottom(1)
    formats['input_col'].set_left(1)

    formats['input_col_text'] = copy_format(workbook, formats['input_col'])
    formats['input_col_text'].set_align('left')

    formats['input_col_right'] = copy_format(workbook, formats['input_col'])
    formats['input_col_right'].set_left(0)
    formats['input_col_right'].set_right(1)

    formats['output_col'] = workbook.add_format({'bg_color': 'E2EFDA'})  # light green
    formats['output_col'].set_border(1)

    # Add a number format for cells with money.
    formats['money_big'] = workbook.add_format({'num_format': '$#,##0'})
    formats['money_big'].set_top(1)
    formats['money_big'].set_bottom(1)
    formats['money_big'].set_left(1)

    formats['money_small'] = workbook.add_format({'num_format': '$#,##0.00', 'bg_color': 'DDEBF7'})
    formats['money_small'].set_top(1)
    formats['money_small'].set_bottom(1)
    formats['money_small'].set_left(1)

    formats['output_col_money_big'] = workbook.add_format({'num_format': '$#,##0', 'bg_color': 'E2EFDA'})
    formats['output_col_money_big'].set_top(1)
    formats['output_col_money_big'].set_bottom(1)
    formats['output_col_money_big'].set_left(1)
    formats['output_col_money_big'].set_right(1)

    formats['int_big'] = workbook.add_format({'num_format': '#,##0', 'bg_color': 'DDEBF7'})
    formats['int_big'].set_top(1)
    formats['int_big'].set_bottom(1)
    formats['int_big'].set_left(1)

    formats['int_big_output'] = copy_format(workbook, formats['int_big'])
    formats['int_big_output'].set_bg_color('E2EFDA')
    formats['int_big_output'].set_num_format('$#,##0')

    formats['table_title'] = workbook.add_format({'bold': 'true', 'align': 'center', 'border': 1})

    # header above each sub-section
    formats['merge_format'] = workbook.add_format({'align': 'center', 'valign': 'vcenter', })
    formats['merge_format'].set_top(1)
    formats['merge_format'].set_bottom(1)
    formats['merge_format'].set_left(1)
    formats['merge_format'].set_right(1)


    return formats


def populate_workbook(workbook, worksheet, scenario_id, formats, start_col=0):
    # region --get data--
    #
    # generate the data used in the export
    #
    scenario = get_object_or_404(Scenario, pk=scenario_id)

    cost_results = scenario.get_costs()

    project_life_cycle_costs = cost_results.pop('project_life_cycle_costs')
    structure_life_cycle_costs = cost_results.pop('structure_life_cycle_costs')
    # endregion

    # region --worksheet--

    worksheet.set_column(start_col, start_col, 27)
    worksheet.set_column(start_col + 1, start_col + 1, 20)
    worksheet.set_column(start_col + 2, start_col + 2, 25)

    # Write some data headers.
    worksheet.write(0, start_col, 'Project Title', formats['bold'])
    worksheet.write(0, start_col + 1, scenario.project.project_title, formats['bold'])
    worksheet.write(1, start_col, 'Scenario Title', formats['bold'])
    worksheet.write(1, start_col + 1, scenario.scenario_title, formats['bold'])

    # Some data we want to write to the worksheet.
    project_description = (
        ['Project Organizer', scenario.project.get_project_ownership_display(), formats['input_col_text']],
        ['Location of the project', scenario.project.project_location, formats['input_col_text']],
        ['Project Type', scenario.project.get_project_type_display(), formats['input_col_text']],
        ['Purchase Information', scenario.project.get_project_purchase_information_display(),
         formats['input_col_text']],
        ['Total Project Area', int(scenario.project.project_area), formats['int_big']],
        ['Land cost per ft', scenario.project.land_unit_cost.amount, formats['money_small']],
        ['Land Value', float(scenario.project.project_area) * float(scenario.project.land_unit_cost.amount),
         formats['output_col_money_big']],
    )

    # Start from the first cell below the headers.
    row = 3
    col = start_col

    # Iterate over the data and write it out row by row.
    for label, value, format in project_description:
        worksheet.write(row, col, label, formats['label_col'])
        if format == 'text':
            worksheet.write(row, col + 1, value)
        else:
            worksheet.write(row, col + 1, value, format)
            worksheet.write(row, col + 2, '', formats['input_col_right'])
        row += 1

    # Write a second instance of the total using a formula. Example Only.
    # worksheet.write(row, 0, 'Land Value', label_col)
    # worksheet.write(row, 1, '=B8*B9', output_col_money_big)

    row += 1

    worksheet.merge_range(row, col, row + 1, col + 2, 'Design Elements', formats['merge_format'])

    row += 1
    row += 1

    project_description = (
        ['Nutrient requirements met?', scenario.get_nutrient_req_met_display(), formats['input_col_text']],
        ['Captures 90th pct storm?', scenario.get_captures_90pct_storm_display(), formats['input_col_text']],
        ['Meets peak flow req?', scenario.get_meets_peakflow_req_display(), formats['input_col_text']],
    )

    # Iterate over the data and write it out row by row.
    for label, value, format in (project_description):
        worksheet.write(row, col, label, formats['label_col'])
        if format == 'text':
            worksheet.write(row, col + 1, value)
        else:
            worksheet.write(row, col + 1, value, format)
            worksheet.write(row, col + 2, '', formats['input_col_right'])
        row += 1

    row += 1

    project_description = (
        ['Pervious Area', scenario.pervious_area, formats['int_big']],
        ['Impervious Area', scenario.impervious_area, formats['int_big']],
    )

    # Iterate over the data and write it out row by row.
    for label, value, format in (project_description):
        worksheet.write(row, col, label, formats['label_col'])
        if format == 'text':
            worksheet.write(row, col + 1, value)
        else:
            worksheet.write(row, col + 1, value, format)
            worksheet.write(row, col + 2, '', formats['input_col_right'])
        row += 1

    worksheet.merge_range(row, col, row + 1, col + 2, 'Life Cycle Costs Assumptions', formats['merge_format'])

    row += 1
    row += 1

    project_description = (
        ['Planning and Design Factor', '{} %'.format(scenario.planning_and_design_factor), formats['input_col']],
        ['Study Life', '{} years'.format(scenario.study_life), formats['input_col']],
        ['Discount Rate', '{} %'.format(scenario.discount_rate), formats['input_col']],
    )

    # Iterate over the data and write it out row by row.
    for label, value, format in (project_description):
        worksheet.write(row, col, label, formats['label_col'])
        if format == 'text':
            worksheet.write(row, col + 1, value)
        else:
            worksheet.write(row, col + 1, value, format)
            worksheet.write(row, col + 2, '', formats['input_col_right'])
        row += 1

    # now try and make all 4 cost blocks as a loop on a more complex object

    cost_blocks = (
        ['Project Life Cycle Costs',
         ['Item', 'Dollars'],
         [
             ['Construction', int(project_life_cycle_costs['total']['construction']), formats['output_col_money_big']],
             ['Planning and Design', int(project_life_cycle_costs['total']['planning_and_design']),
              formats['output_col_money_big']],
             ['O & M', int(project_life_cycle_costs['total']['o_and_m']), formats['output_col_money_big']],
             ['Replacement', int(project_life_cycle_costs['total']['replacement']), formats['output_col_money_big']],
             ['Total', int(project_life_cycle_costs['total']['sum']), formats['output_col_money_big']],
         ]
         ],
        ['Project Construction Costs',
         ['Structure Class', 'Construction', 'P & D'],
         [
             ['Non-Conventional (GSI)',
              int(project_life_cycle_costs['nonconventional']['costs']['construction']),
              int(project_life_cycle_costs['nonconventional']['costs']['planning_and_design']),
              formats['output_col_money_big']],
             ['Conventional',
              int(project_life_cycle_costs['conventional']['costs']['construction']),
              int(project_life_cycle_costs['conventional']['costs']['planning_and_design']),
              formats['output_col_money_big']],
             ['Total',
              int(project_life_cycle_costs['total']['construction']),
              int(project_life_cycle_costs['total']['planning_and_design']), formats['output_col_money_big']],
         ]
         ],
        ['O&M and Replacement Costs',
         ['Structure Class', 'O & M', 'Replacement'],
         [
             ['Non-Conventional (GSI)',
              int(structure_life_cycle_costs['nonconventional']['costs']['o_and_m_sum']),
              int(structure_life_cycle_costs['nonconventional']['costs']['replacement_sum']),
              formats['output_col_money_big']],
             ['Conventional',
              int(structure_life_cycle_costs['conventional']['costs']['o_and_m_sum']),
              int(structure_life_cycle_costs['conventional']['costs']['replacement_sum']),
              formats['output_col_money_big']],
             ['Total',
              int(structure_life_cycle_costs['nonconventional']['costs']['o_and_m_sum'])
              + int(structure_life_cycle_costs['conventional']['costs']['o_and_m_sum']),
              int(structure_life_cycle_costs['nonconventional']['costs']['replacement_sum']
                  + int(structure_life_cycle_costs['conventional']['costs']['replacement_sum'])),
              formats['output_col_money_big']],
         ]
         ],
        ['Life Cycle Costs',
         ['Structure', 'Life Cycle Total'],
         [
             ['Non-Conventional (GSI)', int(project_life_cycle_costs['nonconventional']['costs']['sum']),
              formats['output_col_money_big']],
             ['Conventional', int(project_life_cycle_costs['conventional']['costs']['sum']),
              formats['output_col_money_big']],
             ['Total', int(project_life_cycle_costs['total']['sum']), formats['int_big_output']],
         ]],
    )

    for header, titles, values in (cost_blocks):
        worksheet.merge_range(row, col, row + 1, col + 2, header, formats['merge_format'])
        row += 2
        if len(titles) == 2:
            worksheet.write(row, col, titles[0], formats['table_title'])
            worksheet.write(row, col + 1, titles[1], formats['table_title'])
            row += 1
            for label, value, format in values:
                worksheet.write(row, col, label, formats['label_col'])
                if format == 'text':
                    worksheet.write(row, col + 1, value)
                else:
                    worksheet.write(row, col + 1, value, format)
                row += 1
        else:  # there are 2 values per-line
            worksheet.write(row, col, titles[0], formats['table_title'])
            worksheet.write(row, col + 1, titles[1], formats['table_title'])
            worksheet.write(row, col + 2, titles[2], formats['table_title'])
            row += 1
            for label, value1, value2, format in values:
                worksheet.write(row, col, label, formats['label_col'])
                if format == 'text':
                    worksheet.write(row, col + 1, value1)
                    worksheet.write(row, col + 2, value2)
                else:
                    worksheet.write(row, col + 1, value1, format)
                    worksheet.write(row, col + 2, value2, format)
                row += 1

        # endregion





def populate_scenario_extended_excel_report_workbook(workbook, worksheet, scenario_id, formats, start_row=0):
    """

    make the wide version of the export
    Note: this tries to make a sensible row-col inserts, and deals with writing the header also.
    But it is confusing and the names of the navigation variables is ... strange.

    """
    # region --get data--
    #
    # generate the data used in the export
    #
    scenario = get_object_or_404(Scenario, pk=scenario_id)

    cost_results = scenario.get_costs()

    project_life_cycle_costs = cost_results.pop('project_life_cycle_costs')
    structure_life_cycle_costs = cost_results.pop('structure_life_cycle_costs')
    # endregion

    # region --worksheet--
    start_col = 0
    col = 0
    col_title_row = 1
    insert_header = start_row == 0
    # Start from the first cell below the headers.
    row = start_row + 2

    # set the column widths
    worksheet.set_column(start_col, start_col, 13)
    worksheet.set_column(start_col + 1, start_col + 1, 28)
    worksheet.set_column(start_col + 2, start_col + 2, 12)
    worksheet.set_column(start_col + 3, start_col + 3, 29)

    worksheet.set_column(start_col + 4, start_col + 4, 18)
    worksheet.set_column(start_col + 5, start_col + 5, 38)
    worksheet.set_column(start_col + 6, start_col + 6, 30)
    worksheet.set_column(start_col + 7, start_col + 7, 18)
    worksheet.set_column(start_col + 8, start_col + 8, 11.5)
    worksheet.set_column(start_col + 9, start_col + 9, 12)
    worksheet.set_column(start_col + 10, start_col + 10, 12)

    worksheet.set_column(start_col + 11, start_col + 11, 35)
    worksheet.set_column(start_col + 12, start_col + 12, 21)

    for col_index in range(13, 13 + 15 + 7):
        worksheet.set_column(col_index, col_index, 15)

    # remove the blue or green background from some formats
    formats['input_col'].set_bg_color('white')
    formats['input_col_text'].set_bg_color('white')
    formats['int_big'].set_bg_color('white')
    formats['money_small'].set_bg_color('white')
    formats['output_col_money_big'].set_bg_color('white')

    # this was just used for debugging.  it can be removed
    skip_this_section = False

    if skip_this_section is False:
        # Write some data headers.
        if insert_header is True:
            worksheet.merge_range(0, col, 0, 2, 'User', formats['merge_format'])
            worksheet.write(col_title_row, col, 'user_name', formats['bold'])
            worksheet.write(col_title_row, col + 1, 'organization', formats['bold'])
            worksheet.write(col_title_row, col + 2, 'user_type', formats['bold'])

            worksheet.merge_range(0, 3, 0, 10, 'Project', formats['merge_format'])
            worksheet.write(col_title_row, col + 3, 'project_title', formats['bold'])


        worksheet.write(row, col, scenario.project.user.name)
        worksheet.write(row, col + 1, scenario.project.user.organization_tx)
        worksheet.write(row, col + 2, scenario.project.user.profile.user_type)
        worksheet.write(row, col + 3, scenario.project.project_title)


        # Some data we want to write to the worksheet.
        project_description = (
            ['project_ownership', scenario.project.get_project_ownership_display(), formats['input_col_text']],
            ['project_location', scenario.project.project_location, formats['input_col_text']],
            ['project_type', scenario.project.get_project_type_display(), formats['input_col_text']],
            ['project_purchase_information', scenario.project.get_project_purchase_information_display(),
             formats['input_col_text']],
            ['project_area', int(float(scenario.project.project_area)), formats['int_big']],
            ['land_unit_cost', scenario.project.land_unit_cost.amount, formats['money_small']],
            ['land_value', float(scenario.project.project_area) * float(scenario.project.land_unit_cost.amount),
             formats['output_col_money_big']],
        )

        col = 4

        # Iterate over the data and write it out row by row.
        for label, value, format in (project_description):
            if insert_header is True:
                worksheet.write(col_title_row, col, label, formats['bold'])
            worksheet.write(row, col, value, format)
            col += 1

        #TODO: fix this.  it is causing an Excel error, and I can't figure out what.
        # worksheet.merge_range(0, 11, 0, 12, 'Scenario', formats['merge_format'])

        worksheet.write(col_title_row, col , 'scenario_title', formats['bold'])
        worksheet.write(row, col , scenario.scenario_title)


        project_description = (
            ['nutrient_req_met', scenario.get_nutrient_req_met_display(), formats['input_col_text']],
            ['captures_90pct_storm', scenario.get_captures_90pct_storm_display(), formats['input_col_text']],
            ['meets_peakflow_req', scenario.get_meets_peakflow_req_display(), formats['input_col_text']],
        )

        # Iterate over the data and write it out row by row.
        for label, value, format in (project_description):
            if insert_header is True:
                worksheet.write(col_title_row, col, label, formats['bold'])
            worksheet.write(row, col, value, format)
            col += 1

        project_description = (
            ['pervious_area', scenario.pervious_area, formats['int_big']],
            ['impervious_area', scenario.impervious_area, formats['int_big']],
        )

        # Iterate over the data and write it out row by row.
        for label, value, format in (project_description):
            if insert_header is True:
                worksheet.write(col_title_row, col, label, formats['bold'])
            worksheet.write(row, col, value, format)
            col += 1

        project_description = (
            ['planning_and_design_factor', '{} %'.format(scenario.planning_and_design_factor), formats['input_col']],
            ['study_life', '{} years'.format(scenario.study_life), formats['input_col']],
            ['discount_rate', '{} %'.format(scenario.discount_rate), formats['input_col']],
        )

        # Iterate over the data and write it out row by row.
        for label, value, format in (project_description):
            if insert_header is True:
                worksheet.write(col_title_row, col, label, formats['bold'])
            worksheet.write(row, col, value, format)
            col += 1


    # now add the 3 cost-blocks, each with 5 values

    cost_blocks = (
        ['Non-Conventional (GSI) Structures Costs',
         ['Construction', 'P & D', 'O & M', 'Replacement', 'Total'],
         [
             int(structure_life_cycle_costs['nonconventional']['costs']['construction']),
             int(structure_life_cycle_costs['nonconventional']['costs']['planning_and_design']),
             int(structure_life_cycle_costs['nonconventional']['costs']['o_and_m_sum']),
             int(structure_life_cycle_costs['nonconventional']['costs']['replacement_sum']),
             int(project_life_cycle_costs['nonconventional']['costs']['sum']),
         ]
        ],
        ['Conventional Structures Costs',
         ['Construction', 'P & D', 'O & M', 'Replacement', 'Total'],
         [
             int(structure_life_cycle_costs['conventional']['costs']['construction']),
             int(structure_life_cycle_costs['conventional']['costs']['planning_and_design']),
             int(structure_life_cycle_costs['conventional']['costs']['o_and_m_sum']),
             int(structure_life_cycle_costs['conventional']['costs']['replacement_sum']),
             int(project_life_cycle_costs['conventional']['costs']['sum']),
         ]
        ],
        ['Project Life Cycle Costs',
         ['Construction', 'P & D', 'O & M', 'Replacement', 'Total'],
         [
             int(project_life_cycle_costs['total']['construction']),
             int(project_life_cycle_costs['total']['planning_and_design']),
             int(project_life_cycle_costs['total']['o_and_m']),
             int(project_life_cycle_costs['total']['replacement']),
             int(project_life_cycle_costs['total']['sum']),
         ]
        ],
    )


    format = formats['output_col_money_big']
    for header_1, header_2, values in (cost_blocks):
        if insert_header is True:
            col_count = len(header_2)
            worksheet.merge_range(0, col, 0 , col + col_count - 1, header_1, formats['merge_format'])
            hold_col = col
            for label in header_2:
                worksheet.write(1, col, label, formats['bold'])
                col += 1
            col = hold_col

        # Iterate over the data and write it out row by row.
        for value in (values):
            worksheet.write(row, col, value, format)
            col += 1

        # endregion

    return


@login_required
def scenario_list(request, pk=None):
    """
        scenario as function based views using ajax to feed in data

        http://127.0.0.1:92/projects/scenarios/
    """
    project = None
    #
    if not pk == None:
        project = get_object_or_404(Project, id=pk)  # Project.objects.filter(id=pk)

    context_data = {
        # 'scenarios': scenarios,
        # 'projects': projects,
        'project': project,
        'header': 'Scenarios'}
    if request.user.has_perm('scenario.add_project'):
        context_data['can_add'] = True

    # jab - added for beta-user-testing.  allow all users to add
    context_data['can_add'] = True
    context_data['IIS_APP_ALIAS'] = settings.IIS_APP_ALIAS
    return render(request, 'scenario/scenario_index.html', context_data)


# def save_scenario_form(request, form, template_name):
#     data = dict()
#     if request.method == 'POST':
#         if form.is_valid():
#             form.save()
#             data['form_is_valid'] = True
#         else:
#             data['form_is_valid'] = False
#     context = {'form': form}
#     data['html_form'] = render_to_string(template_name, context, request=request)
#     return JsonResponse(data)




def scenario_create(request, project_id=None):
    '''

    If requested using GET This loads a partial that is shown in a modal

    this has to have the pk of the project you are adding the scenario to

    '''
    project = get_object_or_404(Project, id=project_id)

    data = dict()
    if request.method == 'POST':
        form_variable_scenario_title = request.POST.get("scenario_title", None)

        if form_variable_scenario_title == '':
            form_variable_scenario_title = 'BLANK'

        scenarios = Scenario.objects.filter(scenario_title=form_variable_scenario_title)

        # user can reuse the same name 9 times until they get prompted to fix it
        if len(scenarios) > 0:
            r = range(2, 10, 1)
            for i in r:
                test_title = form_variable_scenario_title + ' (' + str(i) + ')'
                if not Scenario.objects.filter(scenario_title=test_title).exists():
                    form_variable_scenario_title = test_title
                    break

        # not functioning yet.  just boilerplate
        scenario = Scenario(
            project=project,
            scenario_title=form_variable_scenario_title,

            # set defaults ??? questionable for some of these
            planning_and_design_factor=20,
            study_life=40,
            discount_rate=2.875,

            pervious_area=0,
            impervious_area=0,
        )

        """
        
        TODO: load default stuff from the scenario_frameworks.DEFAULT_SCENARIO
        
        """

        try:
            scenario.save()

            data['form_is_valid'] = True

        except IntegrityError as exc:
            data['exception'] = "Scenario Title must be unique for the project. Change the Title"

    else:
        context = {'project': project}
        data['html_form'] = render_to_string('scenario/includes/partial_scenario_create.html', context, request=request)

    return JsonResponse(data)





def scenario_duplicate(request, pk):
    """
    ###########################################################################

        If requested using GET This loads a partial that is shown in a modal
        If requested using POST make a copy of the scenario

    ###########################################################################
    """
    scenario = get_object_or_404(Scenario, pk=pk)
    data = dict()
    if request.method == 'POST':

        areal_features = ArealFeatures.objects.filter(scenario=scenario)[0]
        conventional_structures = ConventionalStructures.objects.filter(scenario=scenario)[0]
        nonconventional_structures = NonConventionalStructures.objects.filter(scenario=scenario)[0]

        # aggregate_costs_list = ItemsAggregateCosts.objects.filter(scenario=scenario)
        # if len(aggregate_costs_list) > 0:
        #     aggregate_costs = aggregate_costs_list[0]

        scenario.pk = None
        form_variable_scenario_title = request.POST.get("scenario_title", None)
        # scenario.project_title += ' (copy)'
        if form_variable_scenario_title:
            scenario.scenario_title = form_variable_scenario_title
        else:
            scenario.scenario_title += ' (copy)'

        areal_features.pk = None
        areal_features.scenario = scenario
        areal_features.save()

        conventional_structures.pk = None
        conventional_structures.scenario = scenario
        conventional_structures.save()

        nonconventional_structures.pk = None
        nonconventional_structures.scenario = scenario
        nonconventional_structures.save()

        # if len(aggregate_costs_list) > 0:
        #     aggregate_costs.pk = None
        #     aggregate_costs.scenario = scenario
        #     aggregate_costs.save()

        scenario.areal_features = areal_features
        scenario.conventional_structures = conventional_structures
        scenario.nonconventional_structures = nonconventional_structures
        # if len(aggregate_costs_list) > 0:
        #     scenario.aggregate_costs = aggregate_costs

        try:
            scenario.save()

            new_pk = scenario.pk

            data['form_is_valid'] = True

        except IntegrityError as exc:
            data['exception'] = "Scenario Title must be unique for the project. Change the Title"

    else:
        context = {'scenario': scenario}
        data['html_form'] = render_to_string('scenario/includes/partial_scenario_duplicate.html', context,
                                             request=request)

    return JsonResponse(data)


@login_required
def scenario_update(request, pk):
    """
    ###########################################################################

        This is the function that displays the Cost Tool.
        It loads everything known about the scenario into the template
        and then javascript stuff does a bunch of work

        available via /scenario/{id}/update

    ###########################################################################
    """
    scenario = get_object_or_404(Scenario, pk=pk)

    # get a serialized copy of the scenario and in the users browser it will be loaded into the UI
    serializer_class = ScenarioSerializer
    serializer = serializer_class(scenario)

    scenarioTemplate = Scenario.templateScenario

    structures = Structures.objects.all().order_by("sort_nu")

    cost_item_user_costs = CostItemUserCosts.objects.filter(scenario__id=scenario.id)

    # cost_item_user_assumptions = CostItemUserAssumptions.objects.filter(scenario__id=scenario.id)

    cost_item_default_costs = CostItemDefaultCosts.objects.all().order_by("costitem__sort_nu")

    # load the labels for structure cost drop-down list
    # TBD remove this and use content of Structure model!!!
    labels = scenarioTemplate['siteData']['conventional_structures']['labels']
    if serializer.data['conventional_structures'] is not None:
        for r, obj in serializer.data['conventional_structures'].items():
            obj['code'] = r
            try:
                obj['label'] = labels[r]
            except:
                obj['label'] = r
    labels = scenarioTemplate['siteData']['nonconventional_structures']['labels']
    if serializer.data['nonconventional_structures'] is not None:
        for r, obj in serializer.data['nonconventional_structures'].items():
            obj['code'] = r
            obj['label'] = labels[r]

    # disclaimer_tx = render_to_string('scenario/results_disclaimer.html')

    context = {
        'scenario': serializer.data,
        'project': scenario.project,
        'structures': structures,
        'cost_item_user_costs': cost_item_user_costs,
        # 'cost_item_user_assumptions': cost_item_user_assumptions,#rename StructureCosts
        'cost_item_default_costs': cost_item_default_costs,
        'result_table': 'removing this',  # disclaimer_tx + scenario_table_html(scenario),
        'IIS_APP_ALIAS': settings.IIS_APP_ALIAS,
    }

    return render(request, 'scenario/costtool/index.html', context)


def scenario_delete(request, pk):
    """
        this is the content of the Confirm scenario deletion pop-up
    """
    scenario = get_object_or_404(Scenario, pk=pk)
    data = dict()
    if request.method == 'POST':
        scenario.delete()
        data['form_is_valid'] = True
    else:
        context = {'scenario': scenario}
        data['html_form'] = render_to_string('scenario/includes/partial_scenario_delete.html', context, request=request)
    return JsonResponse(data)


class TemplateScenario(APIView):
    """

    this returns a JSON template stored in the Scenario model
    it is used to toggle disable/enable and look through fields

    """
    template_version = Scenario.templateScenario

    # this part doesn't work.  it returns nothing except 'sort_nu': null
    # cost_items = CostItem.objects.all()
    # serializer_class = CostItemSerializer
    # serializer = serializer_class(cost_items)
    # template_version['cost_items'] = serializer.data

    def get(self, request):
        return Response(self.template_version)


class DefaultScenario(APIView):
    def get(self, request):
        return Response(Scenario.defaultScenario)


class ScenarioList(ExportMixin, SingleTableView):  # TODO , FilterView
    """

        Scenario

    """
    model = Scenario
    table_class = tables.ScenarioTable
    template_name = 'scenarioOLD/generic_list.html'
    exclude_columns = ('edit_column', 'delete_column',)

    # filterset_class = ScenarioFilter
    #
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('accounts:login'))
        return super(ScenarioList, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(ScenarioList, self).get_queryset()

        if not (self.request.user.is_superuser or self.request.user.is_staff):
            qs = qs.filter(user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context_data = super(ScenarioList, self).get_context_data(**kwargs)

        context_data['title'] = 'Scenarios'
        context_data['header_2'] = 'Scenarios'
        context_data['active_link'] = 'scenario'
        context_data['can_add'] = True
        # context_data['new_url'] = reverse('scenario:scenario_create')
        return context_data


"""

I think this is not used and should be removed

"""


class ScenarioUpdate(PermissionRequiredMixin, generic.UpdateView):
    model = Scenario
    form_class = ScenarioEditForm
    table_class = tables.ScenarioTable
    template_name = 'scenarioOLD/generic_form.html'
    success_url = reverse_lazy('scenario:scenario_list')
    permission_required = 'scenario.change_scenario'

    def get_queryset(self):
        # CHECK IF USER HAS PERMISSION TO MAKE CHANGES TO THE MODEL
        try:
            obj = self.model.objects.get(pk=self.kwargs['pk'])
        except self.model.DoesNotExist:
            raise PermissionDenied  # this way they can't "find" which things exist and which dont

        if (not self.request.user.is_superuser) and (obj.user != self.request.user):
            raise PermissionDenied

        return super(ScenarioUpdate, self).get_queryset()

    def get_context_data(self, **kwargs):
        context_data = super(ScenarioUpdate, self).get_context_data(**kwargs)

        # # CHECK IF USER HAS PERMISSION TO MAKE CHANGES TO THE MODEL
        # try:
        #     obj = self.model.objects.get(pk=self.kwargs['pk'])
        # except self.model.DoesNotExist:
        #     raise PermissionDenied # this way they can't "find" which things exist and which dont
        #
        # if obj.user != self.request.user:
        #     raise PermissionDenied

        context_data['title'] = 'Scenario Update'
        if 'next' in self.request.GET:
            context_data['next_url'] = self.request.GET.get('next')
        else:
            context_data['next_url'] = 'scenario:scenario_list'

        context_data['table'] = tables.ScenarioTable
        context_data['active_link'] = 'scenario'
        context_data['test_variable'] = tables.ScenarioTable  # 'This is crazy'
        context_data['test_variable2'] = 'trying to create ScenarioTable'

        return context_data

    def form_valid(self, form):
        response = super(ScenarioUpdate, self).form_valid(form)
        # now save the selected person and location
        self.request.session['user_selected'] = form.cleaned_data['user'].id
        if form.cleaned_data['location']:
            self.request.session['location_selected'] = form.cleaned_data['location'].id
        return response


'''
    provided via /api/structures and /api/structures/?code=TBD
'''


class StructureViewSet(viewsets.ModelViewSet):
    queryset = Structures.objects.all().order_by("sort_nu")
    serializer_class = StructureSerializer

    def get_queryset(self):
        qs = super(StructureViewSet, self).get_queryset()

        code = self.request.query_params.get('code', None)
        if code is not None:
            qs = qs.filter(code=code)

        return qs


'''
    provided via /api/costitems and /api/costitems/?code=fill
'''


class CostItemViewSet(viewsets.ModelViewSet):
    queryset = CostItem.objects.all().order_by("sort_nu")
    serializer_class = CostItemSerializer

    def get_queryset(self):
        qs = super(CostItemViewSet, self).get_queryset()

        code = self.request.query_params.get('code', None)
        if code is not None:
            qs = qs.filter(code=code)

        return qs


'''
    provided via /api/costitemdefaultcosts and /api/costitemdefaultcosts/?code=fill
'''


class CostItemDefaultCostViewSet(viewsets.ModelViewSet):
    queryset = CostItemDefaultCosts.objects.all().order_by("costitem__sort_nu")
    serializer_class = CostItemDefaultCostSerializer

    def get_queryset(self):
        qs = super(CostItemDefaultCostViewSet, self).get_queryset()

        code = self.request.query_params.get('code', None)
        if code is not None:
            qs = qs.filter(costitem__code=code)

        return qs


class CostItemUserCostViewSet(viewsets.ModelViewSet):
    """

        provided via /api/cost_item_user_costs and /api/costitem_user_costs/?code=fill

    """
    queryset = CostItemUserCosts.objects.all().order_by("costitem__sort_nu")
    serializer_class = CostItemUserCostSerializer

    def get_queryset(self):
        qs = super(CostItemUserCostViewSet, self).get_queryset()

        code = self.request.query_params.get('scenario', None)
        if code is not None:
            qs = qs.filter(scenario__id=code)

        code = self.request.query_params.get('code', None)
        if code is not None:
            qs = qs.filter(costitem__code=code)

        return qs


class CostItemDefaultEquationsAndFactors(viewsets.ModelViewSet):
    """
        provided via /api/costitemdefaultequations and /api/costitemdefaultassumptions/?structure=pond&costitem=fill
    """
    queryset = CostItemDefaultEquations.objects.all().order_by('costitem__sort_nu')
    serializer_class = CostItemDefaultEquationsSerializer

    def get_queryset(self):
        qs = super(CostItemDefaultEquationsAndFactors, self).get_queryset()

        code = self.request.query_params.get('costitem', None)
        if code is not None:
            qs = qs.filter(costitem__code=code)

        return qs





class CostItemDefaultFactorsViewSet(viewsets.ModelViewSet):
    """
        provided via /api/costitemdefaultfactors and /api/costitemdefaultfactors/?structure=pond&costitem=fill
    """
    queryset = CostItemDefaultFactors.objects.all().order_by('structure__sort_nu', 'costitem__sort_nu')
    serializer_class = CostItemDefaultFactorsSerializer

    def get_queryset(self):
        qs = super(CostItemDefaultFactorsViewSet, self).get_queryset()

        code = self.request.query_params.get('structure', None)
        if code is not None:
            qs = qs.filter(structure__code=code)

        code = self.request.query_params.get('costitem', None)
        if code is not None:
            qs = qs.filter(costitem__code=code)

        return qs


'''
    provided via /api/scenarios and /api/scenarios/<pk:i>/
    
    also via /api/scenarios/?project=<int>

    Detailed scenario instance(s)
    
'''


class ScenarioViewSet(viewsets.ModelViewSet):
    queryset = Scenario.objects.all().order_by('id')

    # this serializer contains all the details
    serializer_class = ScenarioSerializer

    # this is the change required to use this on the list
    # serializer_class = ScenarioListSerializer  # jab 2019-05-24 ScenarioSerializer

    def get_queryset(self):
        qs = super(ScenarioViewSet, self).get_queryset()

        if not (self.request.user.is_superuser or self.request.user.is_staff):
            qs = qs.filter(project__user=self.request.user)

        # this is getting a single scenario by id
        code = self.request.query_params.get('id', None)
        if code is not None:
            qs = qs.filter(id=code)
        # this is getting a list of scenarios for a project
        project = self.request.query_params.get('project', None)
        if project is not None:
            qs = qs.filter(project__id=project)

        return qs

    # jab - learning 2019-06-02
    # def retrieve(self, request, pk=None):
    #     serializer = self.serializer_class(self.queryset, many=True)
    #     serializer_data = serializer.data
    #     # del(serializer_data.project)
    #     serializer_data.project = 'Hello'
    #     return Response(serializer_data)

    # def list(self, request):
    #     serializer = self.serializer_class(self.queryset, many=True)
    #     serializer_data = serializer.data
    #     # del(serializer_data.project)
    #     serializer_data['project'] = 'Hello'
    #     return Response(serializer_data)


'''
    provided via /api/scenarios and /api/scenarios/<pk:i>/

    also via /api/scenarios/?project=<int>


    this is used in the /project/<pk>/scenario list

'''


class ScenarioListViewSet(viewsets.ModelViewSet):
    queryset = Scenario.objects.all().order_by('id')
    # serializer_class = ScenarioSerializer

    # this is the change required to use this on the list
    serializer_class = ScenarioListSerializer  # jab 2019-05-24 ScenarioSerializer

    def get_queryset(self):
        qs = super(ScenarioListViewSet, self).get_queryset()

        if not (self.request.user.is_superuser or self.request.user.is_staff):
            qs = qs.filter(project__user=self.request.user)

        # this is getting a single scenario by id
        code = self.request.query_params.get('id', None)
        if code is not None:
            qs = qs.filter(id=code)
        # this is getting a list of scenarios for a project
        project = self.request.query_params.get('project', None)
        if project is not None:
            qs = qs.filter(project__id=project)

        return qs


'''
    provided via /api/scenarios and /api/scenarios/<pk:i>/

    also via /api/scenarios/?project=<int>


    this is used in the /project/<pk>/scenario list

'''


class ScenarioAuditViewSet(viewsets.ModelViewSet):
    queryset = Scenario.objects.all().order_by('id')
    # serializer_class = ScenarioSerializer

    # this is the change required to use this on the list
    serializer_class = ScenarioAuditSerializer  # jab 2019-05-24 ScenarioSerializer

    # def get_queryset(self):
    #     qs = super(ScenarioAuditViewSet, self).get_queryset()
    #
    #     if not (self.request.user.is_superuser or self.request.user.is_staff):
    #         qs = qs.filter(project__user=self.request.user)
    #
    #     # this is getting a single scenario by id
    #     code = self.request.query_params.get('id', None)
    #     if code is not None:
    #         qs = qs.filter(id=code)
    #     # this is getting a list of scenarios for a project
    #     project = self.request.query_params.get('project', None)
    #     if project is not None:
    #         qs = qs.filter(project__id=project)
    #
    #     return qs


class CostItemUserAssumptionsViewSet(viewsets.ModelViewSet):
    """
        provided via /api/cost_item_user_factors
        and /api/cost_item_user_factors/?structure=pond&costitem=fill&scenario=8
    """
    queryset = CostItemUserAssumptions.objects.all().order_by('scenario__id', 'structure__sort_nu', 'costitem__sort_nu')
    serializer_class = CostItemUserAssumptionsSerializer

    def get_queryset(self):
        qs = super(CostItemUserAssumptionsViewSet, self).get_queryset()

        code = self.request.query_params.get('scenario', None)
        if code is not None:
            qs = qs.filter(scenario__id=code)

        code = self.request.query_params.get('structure', None)
        if code is not None:
            qs = qs.filter(structure__code=code)

        code = self.request.query_params.get('costitem', None)
        if code is not None:
            qs = qs.filter(costitem__code=code)

        return qs


class UserViewSet(viewsets.ViewSet):
    """
        provided via /api/users
    """
    queryset = User.objects.all().order_by('name')
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = super(UserViewSet, self).get_queryset()

        if not (self.request.user.is_superuser or self.request.user.is_staff):
            qs = qs.filter(project__user=self.request.user)

        code = self.request.query_params.get('id', None)
        if code is not None:
            qs = qs.filter(id=code)

    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)


"""

    this is old stuff left here just in case I need to reuse something

"""
