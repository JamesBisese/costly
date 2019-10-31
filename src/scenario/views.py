import sys
import json
import copy

from django.conf import settings
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import HttpResponseRedirect, render, get_object_or_404
from django_tables2 import SingleTableView
from django_tables2.export.views import ExportMixin
from django.template.loader import render_to_string
from django.views import generic
from django.urls import reverse,reverse_lazy

from django.contrib.auth.mixins import PermissionRequiredMixin

from djmoney.money import Money

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Project, Scenario, ArealFeatures, Structures, \
    ConventionalStructures, NonConventionalStructures, \
    CostItem, CostItemDefaultEquations, \
    CostItemDefaultCosts,  CostItemUserCosts, \
    CostItemDefaultFactors, CostItemUserAssumptions

from .forms import ProjectForm, ScenarioEditForm, ScenarioDeleteForm
from . import tables

from authtools.models import User

from .serializers import UserSerializer, ProjectSerializer, EmbeddedProjectSerializer, \
    ScenarioSerializer, ScenarioListSerializer, \
    StructureSerializer, \
    CostItemDefaultCostSerializer, CostItemUserCostSerializer, \
    CostItemDefaultEquationsSerializer, CostItemDefaultFactorsSerializer, CostItemSerializer, CostItemUserAssumptionsSerializer

"""
    Project functionality
"""

"""
    project list as function based views using ajax to feed in data
    
    http://127.0.0.1:92/projects/
"""
def project_list(request):
    projects = Project.objects.all()
    context_data = {'projects': projects,
                    'header': 'Projects'}
    if request.user.has_perm('scenario.add_project'):
        context_data['can_add'] = True

    #jab - added for beta-user-testing.  allow all users to add
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
    queryset = Scenario.objects.filter(project__id=pk).order_by("sort_nu")
    serializer_class = ScenarioSerializer

    def get_queryset(self):
        qs = super(ProjectScenarioViewSet, self).get_queryset()

        # code = self.request.query_params.get('code', None)
        # if code is not None:
        #     qs = qs.filter(code=code)

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

#### also never removed

class ProjectList(ExportMixin, SingleTableView): # TODO , FilterView
    model = Project
    table_class = tables.ProjectTable
    template_name = 'scenarioOLD/generic_list.html'
    exclude_columns = ('edit_column','delete_column',)
    # filterset_class = ScenarioFilter
    #
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
        context_data['new_url'] = '' # reverse('scenario:project_create')
        return context_data

"""
###############################################################################

    end Project functionality

"""


def test_partial(request):
    sortid = request.GET.get('sortid')
    cost_item_default_costs = CostItemDefaultCosts.objects.all() # .order_by('user').order_by('project_title')

    context = {'something':'here'}

    if request.is_ajax():
        template = 'test_partial/partial-results.html'
    else:
        template = 'test_partial/result-page.html'
    return render(request, template,   {'cost_item_default_costs':cost_item_default_costs}, context)


"""
    available via /structures/
"""
class StructuresList(ExportMixin, SingleTableView): # TODO , FilterView
    model = Structures
    table_class = tables.StructuresTable
    template_name = 'scenario/structures_list.html'
    # exclude_columns = ('edit_column','delete_column',)
    # filterset_class = ScenarioFilter
    #
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('accounts:login'))
        return super(StructuresList, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(StructuresList, self).get_queryset()

        # if not (self.request.user.is_superuser or self.request.user.is_staff):
        #     qs = qs.filter(user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context_data = super(StructuresList, self).get_context_data(**kwargs)

        context_data['title'] = 'Structures'
        context_data['header_2'] = 'Structures'
        context_data['IIS_APP_ALIAS'] = settings.IIS_APP_ALIAS
        return context_data

"""
    available via /costitems/
"""
class CostItemsList(ExportMixin, SingleTableView): # TODO , FilterView
    model = CostItem
    table_class = tables.CostItemsTable
    template_name = 'scenario/costitems_list.html'
    # exclude_columns = ('edit_column','delete_column',)
    # filterset_class = ScenarioFilter
    #
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('accounts:login'))
        return super(CostItemsList, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(CostItemsList, self).get_queryset()

        # if not (self.request.user.is_superuser or self.request.user.is_staff):
        #     qs = qs.filter(user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context_data = super(CostItemsList, self).get_context_data(**kwargs)

        context_data['title'] = 'Cost Items'
        context_data['header_2'] = 'Cost Items'
        context_data['IIS_APP_ALIAS'] = settings.IIS_APP_ALIAS
        return context_data

"""
    available via /cost_item/default_costs/
"""
class CostItemDefaultCostsList(ExportMixin, SingleTableView): # TODO , FilterView
    model = CostItemDefaultCosts
    table_class = tables.CostItemDefaultCostsTable
    template_name = 'scenario/costitems_default_costs_list.html'
    # exclude_columns = ('edit_column','delete_column',)
    # filterset_class = ScenarioFilter
    #
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('accounts:login'))
        return super(CostItemDefaultCostsList, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(CostItemDefaultCostsList, self).get_queryset()

        # if not (self.request.user.is_superuser or self.request.user.is_staff):
        #     qs = qs.filter(user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context_data = super(CostItemDefaultCostsList, self).get_context_data(**kwargs)

        context_data['title'] = 'Cost ItemDefaultCostsList'
        context_data['header_2'] = 'Cost Item Default Costs'
        context_data['active_link'] = 'scenario'
        context_data['can_add'] = True
        context_data['IIS_APP_ALIAS'] = settings.IIS_APP_ALIAS
        # context_data['new_url'] = reverse('scenario:scenario_create')
        return context_data


"""
    available via /cost_item/default_assumptions/
"""
class CostItemDefaultEquationsList(ExportMixin, SingleTableView): # TODO , FilterView
    model = CostItemDefaultEquations
    table_class = tables.CostItemDefaultEquationsTable
    template_name = 'scenario/costitems_default_equations_list.html'
    # exclude_columns = ('edit_column','delete_column',)
    # filterset_class = ScenarioFilter
    #
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('accounts:login'))
        return super(CostItemDefaultEquationsList, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(CostItemDefaultEquationsList, self).get_queryset()

        # if not (self.request.user.is_superuser or self.request.user.is_staff):
        #     qs = qs.filter(user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context_data = super(CostItemDefaultEquationsList, self).get_context_data(**kwargs)

        context_data['title'] = 'Cost ItemDefaultEquationList'
        context_data['header_2'] = 'Cost Item Default Equations'
        context_data['active_link'] = 'scenario'
        context_data['IIS_APP_ALIAS'] = settings.IIS_APP_ALIAS
        return context_data

"""
    available via /cost_item/default_factors/
"""
class CostItemDefaultFactorsList(ExportMixin, SingleTableView): # TODO , FilterView
    model = CostItemDefaultFactors
    table_class = tables.CostItemDefaultFactorsTable
    template_name = 'scenario/costitems_default_factors_list.html'
    # exclude_columns = ('edit_column','delete_column',)
    # filterset_class = ScenarioFilter
    #
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('accounts:login'))
        return super(CostItemDefaultFactorsList, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(CostItemDefaultFactorsList, self).get_queryset()

        # if not (self.request.user.is_superuser or self.request.user.is_staff):
        #     qs = qs.filter(user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context_data = super(CostItemDefaultFactorsList, self).get_context_data(**kwargs)

        context_data['title'] = 'Cost ItemDefaultFactorsList'
        context_data['header_2'] = 'Cost Item Default Factors'
        context_data['active_link'] = 'scenario'
        context_data['IIS_APP_ALIAS'] = settings.IIS_APP_ALIAS
        return context_data

"""
    TBD
"""
def costitem_defaultcosts_update(request, pk):
    costitem_defaultcosts = get_object_or_404(CostItemDefaultCosts, pk=pk)

    # get a serialized copy of the scenario and in the users browser it will be loaded into the UI
    serializer_class = CostItemDefaultCostSerializer
    serializer = serializer_class(costitem_defaultcosts)

    context_data = {'costitem_defaultcosts': serializer.data}
    context_data['IIS_APP_ALIAS'] = settings.IIS_APP_ALIAS
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
    #TODO: remove this - we will do adds using the db, not this UI
    if ('scenario_id' in form_data
            and (form_data['scenario_id'] == 'undefined'
                or form_data['scenario_id'] == '')):

        try:
            scenario = Scenario.objects.create(
                # user = request.user,
                project_id = form_data['project_id'],
                scenario_title = form_data['siteData']['embedded_scenario']['scenario_title'],

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

            #DB_SPECIFIC
            if (error.args[0] == "UNIQUE constraint failed: scenario_scenario.user_id, scenario_scenario.project_title, scenario_scenario.scenario_title"):
                form_data['Error']['message'] = "Duplicate Project and Scenario Title.  You can only have one " \
                                                + "scenario with the the same Project Title and Scenario Title"
                form_data['Error']['error_dom_id'] = 'scenario_title_validation_error'

                return JsonResponse(form_data)

        form_data['scenario_id'] = scenario.id

        form_data['uiMessage'] = {'redirect_required':
                                     { 'reason': 'added',
                                       'scenario_id': scenario.id,
                                       'redirect_to': reverse('scenario:scenario_update', kwargs={'pk': scenario.id})
                                     }
                                }

    else: # UPDATE
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
            if (error.args[0] == "UNIQUE constraint failed: scenario_scenario.user_id, scenario_scenario.project_title, scenario_scenario.scenario_title"):
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

    # if len(cost_item_user_assumptions) > 0:
    #     for obj in cost_item_user_assumptions:
    #         structure_costs['data'][obj.costitem.code] = {'checked': obj.checked,
    #                                                       # 'factor_assumption_tx': obj.factor_assumption_tx,
    #                                                       'a_area': obj.a_area,
    #                                                       'n_number': obj.n_number,
    #                                                       'cost_source': 'TBD1',
    #                                                       'unit_cost': 'TBD1',
    #                                                       'units': obj.costitem.units,
    #                                                       'equation': 'TBD1'
    #                                                       }
    # else:
    for obj in cost_item_default_assumptions:
        structure_costs['data'][obj.costitem.code] = {'checked': True,
                                                      # 'factor_assumption_tx': obj.factor_assumption_tx,
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
        structure_costs['data'][costitem_code]['equation'] = cost_item_default_assumptions_obj.construction_cost_factor_equation

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
                cost_item_data['equation_value'] = '${:,.2f}'.format(cost_amount)
                cost_item_data['unit_cost_formatted'] = '${:,.2f}'.format(cost_item_data['unit_cost'])
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
                              cost_item_default_factors, # this knows which items to check 'by default'
                              cost_item_user_costs,
                              cost_item_user_assumptions, # this knows which items the user checked

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

    # TODO: make this legibile. I can't figure out what is going on.
    # this has all the assumptions, with the 'structure_code' in there.
    #   scenario_json['cost_item_user_assumptions']
    # cost_item_user_assumptions = scenario_json['cost_item_user_assumptions']

    structure_costs = {'structure': { 'code': structure.code,
                                      'name': structure.name,
                                      'area': structure.area,
                                      'units': structure.units,
                                      'units_html': structure.units_html,
                                      },
                                       'data': {} }

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
    #jab new - get equation from CostItemDefaultEquations table
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
        unit_cost_formatted = ''

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
                unit_cost_formatted = '${:,.2f}'.format(unit_cost)

        # add the user costs data
        structure_costs['data'][costitem_code]['cost_source'] = cost_source
        structure_costs['data'][costitem_code]['unit_cost'] = unit_cost
        structure_costs['data'][costitem_code]['unit_cost_formatted'] = unit_cost_formatted


    # then add in the default costs to update the non 'user' (cost_source) costs

    for obj in cost_item_default_costs:
        costitem_code = obj.costitem.code

        # make the blank structure
        if not costitem_code in structure_costs['data']:
            structure_costs['data'][costitem_code]['cost_source'] = 'rsmeans'

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
            structure_costs['data'][costitem_code]['unit_cost_formatted'] = '${:,.2f}'.format(unit_cost)

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

            #TODO: figure out where to put this
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
                cost_item_data['equation_value'] = '${:,.2f}'.format(cost_amount)
                cost_item_data['unit_cost_formatted'] = '${:,.2f}'.format(cost_item_data['unit_cost'])
            except :
                cost_amount = equation
                cost_item_data['equation_value'] = 'err:' + cost_amount

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

                                   structure_cost_items_data,#TODO change to whatever this should be
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



class MultipleScenarioResults(APIView):
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
            scenarios[id] = {'id': id, 'html': scenario_table}

        context = {'scenarios': scenarios}
        #
        #
        return Response(context)

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
        disclaimer_tx = '<p>Hello World!</p>'
        return HttpResponse(disclaimer_tx + scenario_table_html(scenario))






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
        replacement_life =cost_item_obj.replacement_life
        o_and_m_pct = cost_item_obj.o_and_m_pct


        if code in cost_item_user_cost_dict:
            # update stuff
            replacement_life = cost_item_user_cost_dict[code]['replacement_life']
            o_and_m_pct = cost_item_user_cost_dict[code]['o_and_m_pct']

            if cost_item_user_cost_dict[code]['cost_source'] == 'user':
                cost_source_tx = 'User'
                unit_cost = cost_item_user_cost_dict[code]['user_input_cost']
                base_year = cost_item_user_cost_dict[code]['base_year']
            #TBD the cost_source text should match, or almost match, the variable name
            #TODO change text to db_25pct_va or at least db_25pct
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
            'unit_cost': unit_cost,
            'base_year': base_year,
            'replacement_life': replacement_life,
            'o_and_m_pct': o_and_m_pct,
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
                cost_item_obj['unit_cost'] = Money(cost_item_user_cost_dict[code]['user_input_cost'], 'USD')
                cost_item_obj['base_year'] = cost_item_user_cost_dict[code]['base_year']


    #
    # TODO: now create the computed costs part
    #
    cost_results = scenario.get_costs()

    # dictionary (should be a set) to record which cost items are used
    # in the final results.  later used to remove cost item unit costs if they are not used
    cost_items_seen = set()
    for classification in cost_results:
        for structure in cost_results[classification]['structures']:
            for cost_item in cost_results[classification]['structures'][structure]['cost_data']:
                cost_items_seen.add(cost_item)

    # remove cost items if they are not used in any cost calculation
    final_cost_item_costs = []
    for cost_item in cost_item_costs:
        if cost_item['code'] in cost_items_seen:
            final_cost_item_costs.append(cost_item)

    context = {'scenario': serializer.data,
               'cost_item_costs': final_cost_item_costs,
               'cost_results': cost_results,
               'sum_values': sum_values}

    return render_to_string(template_name, context)





"""
    scenario as function based views using ajax to feed in data
    
    http://127.0.0.1:92/projects/scenarios/
"""
def scenario_list(request, pk=None):
    scenarios = Scenario.objects.all()
    projects = Project.objects.all()
    project = None

    if not pk==None:
        scenarios = Scenario.objects.filter(project__id=pk)
        project = get_object_or_404(Project, id=pk) # Project.objects.filter(id=pk)
    elif not (request.user.is_superuser or request.user.is_staff):
        scenarios = Scenario.objects.filter(project__user=request.user, project__id=projects[0].id)
        projects = Project.objects.filter(user=request.user)

    if request.method == 'POST':
        # filter scenarios by project
        scenarios = Scenario.objects.filter(project__id=request.POST.get('project_id'))

    context_data = {'scenarios': scenarios,
                    'projects': projects,
                    'project': project,
                    'header': 'Scenarios'}
    if request.user.has_perm('scenario.add_project'):
        context_data['can_add'] = True

    #jab - added for beta-user-testing.  allow all users to add
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

'''
this has to have the pk of the project you are adding the scenario to

'''
def scenario_create(request, project_id=None):
    project = get_object_or_404(Project, id=project_id)
    # structures = Structures.objects.all().order_by("sort_nu")
    #
    #
    # cost_item_default_costs = CostItemDefaultCosts.objects.all()
    # context = {'scenario': Scenario.templateScenario,
    #            'structures': structures,
    #            'project': project,
    #            'cost_item_default_costs': cost_item_default_costs,
    #            }
    # return render(request, 'scenario/costtool/index.html', context)
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


"""
###########################################################################

    This loads a partial that is shown in a modal

    
###########################################################################
"""
def scenario_duplicate(request, pk):
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
        data['html_form'] = render_to_string('scenario/includes/partial_scenario_duplicate.html', context, request=request)

    return JsonResponse(data)


"""
###########################################################################

    This is the function that displays the Cost Tool.
    It loads everything known about the scenario into the template
    and then javascript stuff does a bunch of work

###########################################################################
"""
def scenario_update(request, pk):
    scenario = get_object_or_404(Scenario, pk=pk)

    # this is available at scenario.project
    # project = get_object_or_404(Project, id=scenario.project_id)

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

    disclaimer_tx = render_to_string('scenario/results_disclaimer.html')

    context = {
                'scenario': serializer.data,
                'project': scenario.project,
                'structures': structures,
                'cost_item_user_costs': cost_item_user_costs,
                # 'cost_item_user_assumptions': cost_item_user_assumptions,#rename StructureCosts
                'cost_item_default_costs': cost_item_default_costs,
                'result_table': disclaimer_tx + scenario_table_html(scenario),
                'IIS_APP_ALIAS': settings.IIS_APP_ALIAS,
               }

    return render(request, 'scenario/costtool/index.html', context)



"""
    this is the content of the Confirm scenario deletion pop-up
"""
def scenario_delete(request, pk):
    scenario = get_object_or_404(Scenario, pk=pk)
    data = dict()
    if request.method == 'POST':
        scenario.delete()
        data['form_is_valid'] = True
    else:
        context = {'scenario': scenario}
        data['html_form'] = render_to_string('scenario/includes/partial_scenario_delete.html', context, request=request)
    return JsonResponse(data)

#
# this returns a JSON template stored in the Scenario model
#  it is used to toggle disable/enable and look through fields
#
class TemplateScenario(APIView):

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



"""

    Scenario
    
"""
class ScenarioList(ExportMixin, SingleTableView): # TODO , FilterView
    model = Scenario
    table_class = tables.ScenarioTable
    template_name = 'scenarioOLD/generic_list.html'
    exclude_columns = ('edit_column','delete_column',)
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
            raise PermissionDenied # this way they can't "find" which things exist and which dont

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

'''
    provided via /api/costitemusercosts and /api/costitemusercosts/?code=fill
'''
class CostItemUserCostViewSet(viewsets.ModelViewSet):
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


'''
    provided via /api/costitemdefaultequations and /api/costitemdefaultassumptions/?structure=pond&costitem=fill
'''
class CostItemDefaultEquationsViewSet(viewsets.ModelViewSet):
    queryset = CostItemDefaultEquations.objects.all().order_by('costitem__sort_nu')
    serializer_class = CostItemDefaultEquationsSerializer

    def get_queryset(self):
        qs = super(CostItemDefaultEquationsViewSet, self).get_queryset()

        code = self.request.query_params.get('costitem', None)
        if code is not None:
            qs = qs.filter(costitem__code=code)

        return qs

'''
    provided via /api/costitemdefaultfactors and /api/costitemdefaultfactors/?structure=pond&costitem=fill
'''
class CostItemDefaultFactorsViewSet(viewsets.ModelViewSet):
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
    #serializer_class = ScenarioListSerializer  # jab 2019-05-24 ScenarioSerializer

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

    #jab - learning 2019-06-02
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
    provided via /api/costitemuserassumptions 
    and /api/costitemuserassumptions/?structure=pond&costitem=fill&scenario=8
'''
class CostItemUserAssumptionsViewSet(viewsets.ModelViewSet):
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

'''
    provided via /api/users
'''
class UserViewSet(viewsets.ViewSet):
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

# # not used

# # not used
# """
#     example of rest-service updating of single variable
# """
# def scenario_increment(request, pk):
#     scenario = get_object_or_404(Scenario, pk=pk)
#     scenario.counter += 1
#     scenario.save()
#     data = dict()
#     data['form_is_valid'] = True
#     return JsonResponse(data)
# """
#     example of rest-service updating of single variable
# """
# def scenario_decrement(request, pk):
#     scenario = get_object_or_404(Scenario, pk=pk)
#     if scenario.counter > 0:
#         scenario.counter -= 1
#         scenario.save()
#     data = dict()
#     data['form_is_valid'] = True
#     return JsonResponse(data)
#


# load the labels for structure cost drop-down list
# TBD remove this and use content of Structure model!!!
# scenarioTemplate = Scenario.templateScenario
# labels = scenarioTemplate['siteData']['conventional_structures']['labels']
# if serializer.data['conventional_structures'] is not None:
#     for r, obj in serializer.data['conventional_structures'].items():
#         obj['code'] = r
#         try:
#             obj['label'] = labels[r]
#         except:
#             obj['label'] = r
# labels = scenarioTemplate['siteData']['nonconventional_structures']['labels']
# if serializer.data['nonconventional_structures'] is not None:
#     for r, obj in serializer.data['nonconventional_structures'].items():
#         obj['code'] = r
#         obj['label'] = labels[r]

# class ScenarioCreate(PermissionRequiredMixin, generic.CreateView):
#     model = Scenario
#     form_class = ScenarioEditForm
#     template_name = 'scenario/costtool/index.html'
#     # success_url = reverse_lazy('scenario:scenario_list')
#     permission_required = 'scenario.add_scenario'
#
#     def has_change_permission(self, request, obj=None):
#         if obj is not None and obj.user != request.user:
#             return False
#         return True
#
#     def get_form_kwargs(self):
#         kwargs = super(ScenarioCreate, self).get_form_kwargs()
#         # set the selection to the last thing they selected
#         # if not self.request.user.is_superuser:
#         #     kwargs['user_id'] = self.request.user.id
#         #
#         # if 'user_selected' in self.request.session:
#         #     kwargs['initial']['user'] = self.request.session['user_selected']
#         # if 'location_selected' in self.request.session:
#         #     kwargs['initial']['location'] = self.request.session['location_selected']
#         return kwargs
#
#     def get_context_data(self, **kwargs):
#         context_data = super(ScenarioCreate, self).get_context_data(**kwargs)
#         context_data['title'] = 'Scenario Create'
#         context_data['active_link'] = 'scenario'
#         # if 'next' in self.request.GET:
#         #     context_data['next_url'] = self.request.GET.get('next')
#         # else:
#         #     context_data['next_url'] = 'scenario:scenario_list'
#         return context_data
#
#     # def form_valid(self, form):
#     #     response = super(ScenarioCreate, self).form_valid(form)
#     #     # now save the selected person and location
#     #     self.request.session['user_selected'] = form.cleaned_data['user'].id
#     #     if form.cleaned_data['location']:
#     #         self.request.session['location_selected'] = form.cleaned_data['location'].id
#     #     return response

# #
# # not used.  use the function based partial view - scenario_delete
# #
# class ScenarioDelete(PermissionRequiredMixin, SingleTableView, generic.DeleteView):
#     model = Scenario
#     form_class = ScenarioDeleteForm
#     template_name = 'scenarioOLD/confirm_delete.html'
#     table_class = ScenarioTable
#     success_url = reverse_lazy('scenario:scenario_list')
#     permission_required = 'scenario.delete_scenario'
#
#     def get_context_data(self, **kwargs):
#         # CHECK IF USER HAS PERMISSION TO MAKE CHANGES TO THE MODEL
#         try:
#             obj = self.model.objects.get(pk=self.kwargs['pk'])
#         except self.model.DoesNotExist:
#             raise PermissionDenied # this way they can't "find" which things exist and which dont
#
#         if obj.user != self.request.user:
#             raise PermissionDenied
#
#         def has_delete_permission(self, request, obj=None):
#             if obj is not None and obj.user != request.user:
#                 return False
#             return True
#
#         context_data = {}
#         context_data['table'] = ScenarioTable(self.object_list.filter(pk=self.kwargs['pk']), orderable=False)
#         context_data['active_link'] = 'scenario'
#         context_data['header'] = 'Delete Scenario'
#         context_data['confirmation_line'] = 'Are you sure you want to delete this scenario?'
#         context_data['next_url'] = reverse_lazy('scenario:scenario_list')
#
#         return context_data

# #
# # unknown????
# #
# def index(request):
#     # This view is missing all form handling logic for simplicity of the example
#     return render(request, 'index.html', {'title': 'Donated Welcome'})

# context = {'something':'here'}
#
# if request.is_ajax():
#     template = 'test_partial/partial-results.html'
# else:
#     template = 'test_partial/result-page.html'
# return render(request, template,   {'cost_item_default_costs':cost_item_default_costs}, context)

# # get a serialized copy of the scenario and in the users browser
# # it will be loaded into the Results tab
# serializer_class = ScenarioSerializer
# serializer = serializer_class(scenario)
#
# scenarioTemplate = Scenario.templateScenario
#
# # this holds calculated values used in the tables but not stored in a
# # scenario variable
#
# sum_values = {}
#
# areal_features_sum_area = 0
#
# if serializer.data['areal_features']:
#
#     toggles = scenarioTemplate['siteData']['areal_features']['toggles']
#     labels = scenarioTemplate['siteData']['areal_features']['labels']
#
#     # my_areal_features = copy.deepcopy(serializer.data['areal_features'])
#     for r, obj in serializer.data['areal_features'].items():
#
#         # skip this if the scenario conditions make it 'disabled'
#         toggle = {}
#         for t in toggles:
#             if t['name'] == r:
#                 toggle = t
#                 break
#
#         if (not ((scenario.project_type == 'parcel' and toggle['is_parcel'] == False) \
#             or (scenario.project_type == 'row' and toggle['is_row'] == False)\
#             or (scenario.project_ownership == 'public' and toggle['is_public'] == False)\
#             or (scenario.project_ownership == 'private' and toggle['is_private'] == False))):
#
#             if obj['checkbox'] == True and obj['area'] != "0" and obj['area'] != None:
#                 areal_features_sum_area += int(float(obj['area']))
#                 obj['label'] = labels[r]
#         else:
#             obj['checkbox'] = False
#
#     #
#     # serializer.data.pop('areal_features')
#     # serializer.data['areal_features'] = my_areal_features
#
# sum_values['areal_features_sum_area'] = areal_features_sum_area
#
# pervious_area = 0
# impervious_area = 0
# try:
#     pervious_area = int(float(serializer.data['location']['pervious_area']))
# except:
#     pass
# try:
#     impervious_area = int(float(serializer.data['location']['impervious_area']))
# except:
#     pass
#
# sum_values['pervious_impervious_area'] = pervious_area + impervious_area
#
# # load the labels for structures
# labels = scenarioTemplate['siteData']['conventional_structures']['labels']
# for r, obj in serializer.data['conventional_structures'].items():
#     try:
#         obj['label'] = labels[r]
#     except:
#         obj['label'] = r
# labels = scenarioTemplate['siteData']['nonconventional_structures']['labels']
# for r, obj in serializer.data['nonconventional_structures'].items():
#     obj['label'] = labels[r]
#
# context = {'scenario': serializer.data, 'sum_values': sum_values}
#
#
# return Response(context)


# return scenario_update(request, new_pk)

# # get a serialized copy of the scenario and in the users browser it will be loaded into the UI
# serializer_class = ScenarioSerializer
# serializer = serializer_class(scenario)
#
# scenarioTemplate = Scenario.templateScenario
#
# structures = Structures.objects.all().order_by("sort_nu")
#
# cost_item_user_assumptions = CostItemUserAssumptions.objects.filter(scenario__id=scenario.id)
#
# cost_item_default_costs = CostItemDefaultCosts.objects.all()
#
# # load the labels for structure cost drop-down list
# # TBD remove this and use content of Structure model!!!
# labels = scenarioTemplate['siteData']['conventional_structures']['labels']
# for r, obj in serializer.data['conventional_structures'].items():
#     obj['code'] = r
#     try:
#         obj['label'] = labels[r]
#     except:
#         obj['label'] = r
# labels = scenarioTemplate['siteData']['nonconventional_structures']['labels']
#
# for r, obj in serializer.data['nonconventional_structures'].items():
#     obj['code'] = r
#     obj['label'] = labels[r]
#
# context = {
#             'scenario': serializer.data,
#             'structures': structures,
#             'result_table': scenario_table_html(scenario),
#             'cost_item_user_assumptions': cost_item_user_assumptions,
#             'cost_item_default_costs': cost_item_default_costs,
#            }
#
# return render(request, 'scenario/costtool/index.html', context)

# serializer_class = ScenarioSerializer
# serializer = serializer_class(scenario)
# scenario_data = serializer
#
# # cost_items = CostItemViewSet.as_view({'get': 'list'})
#
# # this is what serializers are supposed to do, but I don't understand how
# cost_items_dict = {}
# cost_items = CostItem.objects.all()
# for cost_item in cost_items:
#     cost_items_dict[cost_item.code] = {'code': cost_item.code,
#                                        'name': cost_item.name,
#                                        'units': cost_item.units}
# # serializer_class = CostItemSerializer
# # serializer = serializer_class(data=cost_items)
# # serializer.is_valid(raise_exception=True)
# # cost_items_dict = serializer.data
# # serializer.is_valid(raise_exception=True)
#
# # serializer_class = CostItemSerializer
# # serializer = serializer_class(cost_items)
# # template_version['cost_items'] = serializer.data
# result = {}
#
# structures = Structures.objects.all().order_by('sort_nu')
# cost_item_default_costs = CostItemDefaultCosts.objects.all()
# cost_item_user_costs = CostItemUserCosts.objects.filter(scenario=scenario)
#
# # build up the costs dictionaries
# # first add in the cost_item_user_costs
#
# costs = {}
#
# for cost_item_user_costs_obj in cost_item_user_costs:
#     costitem_code = cost_item_user_costs_obj.costitem.code
#     unit_cost = None
#     cost_source = None
#     if cost_item_user_costs_obj.user_input_cost is not None:
#         # note: this is a Money field
#         unit_cost = cost_item_user_costs_obj.user_input_cost.amount
#     cost_source = cost_item_user_costs_obj.cost_source
#     if cost_source == 'user':
#         if cost_item_user_costs_obj.user_input_cost is not None:
#             # note: this is a Money field
#             unit_cost = cost_item_user_costs_obj.user_input_cost.amount
#
#     if not costitem_code in costs:
#         costs[costitem_code] = {'cost_source': cost_source,
#                                 'unit_cost': unit_cost,
#                                 'units': cost_items_dict[costitem_code]['units'],
#                                }
#     else:
#         if cost_source == 'user':
#             costs[costitem_code]['unit_cost'] = unit_cost
#             costs[costitem_code]['units'] = cost_items_dict[costitem_code]['units']
#
#         costs[costitem_code]['cost_source'] = cost_source
#
# # then add in the default costs to update the non 'user' (cost_source) costs
# for cost_item_default_costs_obj in cost_item_default_costs:
#     costitem_code = cost_item_default_costs_obj.costitem.code
#     if costitem_code in costs:
#         if costs[costitem_code]['cost_source'] != 'user':
#             cost_source = costs[costitem_code]['cost_source']
#             # the user selected or entered data in assumptions tab, but not in cost tab
#             if cost_source == 'TBD1':
#                 costs[costitem_code]['cost_source'] = 'rsmeans'
#                 cost_source = 'rsmeans'
#
#             unit_cost = None
#             if cost_source == 'rsmeans':
#                 unit_cost = cost_item_default_costs_obj.rsmeans_va.amount
#             elif cost_source == 'db_25_pct':
#                 unit_cost = cost_item_default_costs_obj.db_25pct_va.amount
#             elif cost_source == 'db_50_pct':
#                 unit_cost = cost_item_default_costs_obj.db_50pct_va.amount
#             elif cost_source == 'db_75_pct':
#                 unit_cost = cost_item_default_costs_obj.db_75pct_va.amount
#
#             costs[costitem_code]['unit_cost'] = unit_cost
#             costs[costitem_code]['units'] = cost_items_dict[costitem_code]['units']
#     else:
#         costs[costitem_code] = {'cost_source': 'rsmeans',
#                                 'unit_cost': cost_item_default_costs_obj.rsmeans_va.amount,
#                                 'units': cost_items_dict[costitem_code]['units'],
#                                }
#
#
# # serializer_class = CostItemDefaultCostSerializer
# # serializer = serializer_class(cost_item_default_costs)
# # d = serializer.data
#
# conventional_structures = ConventionalStructures.objects.filter(scenario=scenario)[0]
# nonconventional_structures = NonConventionalStructures.objects.filter(scenario=scenario)[0]
#
# for structure in structures:
#
#     structure_code = structure.code
#     is_checked = False
#     if structure.classification == 'conventional':
#         is_checked = getattr(conventional_structures, structure_code + '_checkbox')
#         structure.area = getattr(conventional_structures, structure_code + '_area')
#     else:
#         is_checked = getattr(nonconventional_structures, structure_code + '_checkbox')
#         structure.area = getattr(nonconventional_structures, structure_code + '_area')
#
#     if is_checked == False:
#         continue
#
#     cost_item_user_assumptions = CostItemUserAssumptions.objects.filter(scenario=scenario, structure=structure, checked=True)
#
#     cost_results = {}
#
#     for cost_item in cost_item_user_assumptions:
#         costitem_code = cost_item.costitem.code
#         cost_results[costitem_code] = {}
#
#         assumptions = {
#             'units': cost_items_dict[costitem_code]['units'],
#             'name': cost_items_dict[costitem_code]['name'],
#             'factor_assumption_tx': cost_item.factor_assumption_tx,
#             'sizing_factor_k': cost_item.sizing_factor_k,
#             'sizing_factor_n': cost_item.sizing_factor_n,
#             'equation': cost_item.construction_cost_factor_equation,
#         }
#         cost_item_default_assumptions = CostItemDefaultAssumptions.objects.filter(structure=structure, costitem=cost_item.costitem_id)
#
#         if len(cost_item_default_assumptions) > 0:
#             if assumptions['factor_assumption_tx'] is None:
#                assumptions['factor_assumption_tx'] = cost_item_default_assumptions[0].factor_assumption_tx
#             if assumptions['sizing_factor_k'] is None:
#                 assumptions['sizing_factor_k'] = cost_item_default_assumptions[0].sizing_factor_k
#             if assumptions['sizing_factor_n'] is None:
#                 assumptions['sizing_factor_n'] = cost_item_default_assumptions[0].sizing_factor_n
#
#             assumptions['construction_cost_factor_equation'] = cost_item_default_assumptions[0].construction_cost_factor_equation
#
#         if assumptions['sizing_factor_k'] in ["", None]:
#             assumptions['sizing_factor_k'] = "1"
#         if assumptions['sizing_factor_n'] in ["", None]:
#             assumptions['sizing_factor_n'] = "1"
#
#         if assumptions['equation'] is None:
#             if assumptions['units'] == 'Ea.':
#                 assumptions['equation'] = '=sizing_factor_n*$'
#             else:
#                 assumptions['equation'] = '=x*sizing_factor_k*sizing_factor_n*$'
#
#             if assumptions['factor_assumption_tx'] is None:
#                 assumptions['factor_assumption_tx'] = 'Non-standard cost item'
#
#         cost_results[costitem_code]['assumptions'] = assumptions
#
#         cost_results[costitem_code]['costs'] = costs[costitem_code]
#
#         results = {}
#
#         structure_units = structure.units
#         cost_item_units = cost_items_dict[costitem_code]['units']
#         unit_conversion = 1
#         if structure_units != cost_item_units:
#             unit_conversion = get_unit_conversion(structure_units, cost_item_units)
#
#         results['unit_conversion'] = unit_conversion
#
#         equation = assumptions['equation']
#
#         # TODO: figure out where to put this
#         equation = equation + '*' + 'unit_conversion'
#
#         equation = equation.replace('=', '')
#         equation = equation.replace('x', str(structure.area))
#         equation = equation.replace('unit_conversion', str(unit_conversion))
#         equation = equation.replace('sizing_factor_k', assumptions['sizing_factor_k'])
#         equation = equation.replace('sizing_factor_n', assumptions['sizing_factor_n'])
#         equation = equation.replace('$', str(costs[costitem_code]['unit_cost']))
#
#         results['equation_calc'] = equation
#
#         cost_results[costitem_code]['results'] = results
#
#         try:
#             cost_amount = eval(equation)
#             results['value'] = '${:,.2f}'.format(cost_amount)
#         except:
#             cost_amount = equation
#             results['value'] = cost_amount
#
#     result[structure_code] = {'structure':
#                                   {'code': structure.code,
#                                      'name': structure.name,
#                                      'area': structure.area,
#                                      'units': structure.units,
#                                      'units_html': structure.units_html,
#                                      },
#                                     'cost_data': cost_results}
#
# return JsonResponse(result)