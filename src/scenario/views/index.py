import json
import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse

from django.contrib.auth.decorators import login_required

from djmoney.money import Money
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response

from scenario.models import Project, Scenario, \
    ArealFeatureLookup, Structures, \
    CostItem, \
    CostItemDefaultCosts, CostItemDefaultEquations, \
    ScenarioCostItemUserCosts, \
    StructureCostItemUserFactors, \
    ScenarioArealFeature, ScenarioStructure

from scenario.forms import ProjectForm

from scenario.serializers import EmbeddedProjectSerializer, \
    ScenarioSerializer, ScenarioCostItemUserCostsSerializer

from scenario.decorators import sql_query_debugger

from .reports import *

logger = logging.getLogger('developer')


# region Project


@login_required
def project_list(request):
    """
        project list as function based views using javascript to load the data and render the table

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


@login_required
def project_save(request, form, template_name):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
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


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
    else:
        form = ProjectForm(user_id=request.user.id)
    return project_save(request, form, 'project/includes/partial_project_create.html')


@login_required
def project_update(request, pk):
    queryset = Project.objects \
        .select_related('user', 'user__profile') \
        .only('project_title', 'project_ownership', 'project_type',
              'project_area', 'land_unit_cost', 'land_unit_cost_currency', 'project_location',
              'project_purchase_information',
              'create_date', 'modified_date',
              'user__name', 'user__email', 'user__phone_tx', 'user__job_title', 'user__organization_tx',
              'user__is_active', 'user__date_joined', 'user__last_login',
              'user__profile__user_type') \
        .all().order_by('project_title')

    if not request.user.is_superuser:
        queryset = queryset.filter(user=request.user)

    project = get_object_or_404(queryset, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
    else:
        form = ProjectForm(instance=project)
    return project_save(request, form, 'project/includes/partial_project_update.html')


@login_required
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


# endregion Project


# region Scenario

@login_required
def scenario_save(request):
    """

        this gets called by 'SaveDB' AND BY EACH AND EVERY EDIT ON THE UI!!!!
        this is URL scenario_save_url

    """
    if request.method != 'POST':
        return JsonResponse({'Error': 'Only POST is accepted by scenario_save()'})

    posted_data = json.loads(request.body.decode('utf-8'))

    form_data = json.loads(posted_data)

    scenario = None

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

            if scenario is not None:
                form_data['scenario_id'] = scenario.id

            # send it off to be processed
            scenario.process_related_data(form_data['siteData'])

            scenario.save()
        except Exception as error:
            form_data['Error'] = {'Type': type(error).__name__,
                                  'message': "Unexpected error:" + error.args[0],
                                  }

            # DB_SPECIFIC
            if error.args[
                0] == "UNIQUE constraint failed: scenario_scenario.user_id, " + \
                    "scenario_scenario.project_title, scenario_scenario.scenario_title":
                form_data['Error']['message'] = "Duplicate Project and Scenario Title.  You can only have one " \
                                                + "scenario with the the same Project Title and Scenario Title"
                form_data['Error']['error_dom_id'] = 'scenario_title_validation_error'

                return JsonResponse(form_data)

        form_data['scenario_id'] = scenario.id

        form_data['uiMessage'] = {'redirect_required':
                                      {'reason': 'added',
                                       'scenario_id': scenario.id,
                                       'redirect_to': reverse('scenario:scenario_update',
                                                              kwargs={'pk': scenario.id})
                                       }
                                  }

    else:  # UPDATE
        # TODO: check that it found the object
        scenario = get_object_or_404(Scenario, pk=form_data['scenario_id'])

        # send it off to be processed
        scenario.process_related_data(form_data['siteData'], form_data['active_tab'])

        scenario.save()

        serializer_class = EmbeddedProjectSerializer

        project_serializer = serializer_class(scenario.project, many=False)

        form_data['siteData']['project'] = project_serializer.data

        form_data['processing_message'] = 'Successfully Saved'

        scenario_cost_item_costs = ScenarioCostItemUserCosts.objects \
            .select_related('scenario', 'costitem') \
            .filter(scenario__id=scenario.id)

        serializer_class = ScenarioCostItemUserCostsSerializer

        cost_item_serializer = serializer_class(scenario_cost_item_costs, many=True)

        form_data['user_costs'] = cost_item_serializer.data

        # I think this can not be true - there is no editing when the active_tab is result
        if form_data['active_tab'] == 'result':
            form_data['html_result'] = results_table_html(scenario)

    return JsonResponse(form_data)


# LoginRequiredMixin,
class CompareScenarioResults(LoginRequiredMixin, APIView):
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
            scenario_table = results_table_html(scenario)
            scenarios[id] = {'id': id, 'html': scenario_table, 'data': scenario}

        left_scenario = scenarios[ids[0]]['data']
        comparison = {}
        if len(ids) == 2:
            right_scenario = scenarios[ids[1]]['data']
            comparison_column_html = comparison_column(left_scenario, right_scenario)

            comparison = {'html': comparison_column_html}

        context = {
            'scenarios': scenarios,
            'comparison': comparison,
            'IIS_APP_ALIAS': settings.IIS_APP_ALIAS
        }
        return Response(context)


class CompareScenarioColumn(APIView):

    def get(self, request, multiple_pks):
        pass

    def get(self, request):
        id_tx = request.query_params['id']
        ids = id_tx.split(',')

        left_scenario = get_object_or_404(Scenario, pk=ids[0])
        right_scenario = get_object_or_404(Scenario, pk=ids[1])

        comparison_column_html = comparison_column(left_scenario, right_scenario)

        return HttpResponse(comparison_column_html)


#
# this is the scenario data in a single html partial table
#
class ScenarioResults(LoginRequiredMixin, APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "scenario/results.html"

    def get(self, request, multiple_pks):
        pass

    # @sql_query_debugger
    def get(self, request, pk):
        scenario = get_object_or_404(Scenario, pk=pk)

        # return the scenario as an HTML table
        disclaimer_tx = render_to_string('scenario/results_disclaimer.html')

        return HttpResponse(disclaimer_tx + results_table_html(scenario))


@login_required
# @sql_query_debugger
def scenario_list(request, pk=None):
    """
        scenario as function based views using ajax to feed in data

        URI/project/{pk}/scenarios/
    """
    project = None
    #
    if pk is not None:
        project = get_object_or_404(Project, id=pk)

    context_data = {
        'project': project,
        'header': 'Scenarios',
        'IIS_APP_ALIAS': settings.IIS_APP_ALIAS
    }

    if request.user.has_perm('scenario.add_project'):
        context_data['can_add'] = True

    # jab - added for beta-user-testing.  allow all users to add
    context_data['can_add'] = True

    return render(request, 'scenario/scenario_index.html', context_data)


@login_required
def scenario_create(request, project_id=None):
    """

    If requested using GET This loads a partial that is shown in a modal

    this has to have the pk of the project you are adding the scenario to

    """
    queryset = Project.objects \
        .select_related('user', 'user__profile') \
        .only('project_title', 'project_ownership', 'project_type',
              'project_area', 'land_unit_cost', 'land_unit_cost_currency', 'project_location',
              'project_purchase_information',
              'create_date', 'modified_date',
              'user__name', 'user__email', 'user__phone_tx', 'user__job_title', 'user__organization_tx',
              'user__is_active', 'user__date_joined', 'user__last_login',
              'user__profile__user_type') \
        .all().order_by('project_title')

    if not request.user.is_superuser:
        queryset = queryset.filter(user=request.user)

    project = get_object_or_404(queryset, id=project_id)
    #
    # project = get_object_or_404(Project, id=project_id)

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

        try:
            scenario.save()
            data['form_is_valid'] = True
        except IntegrityError:
            data['exception'] = "Scenario Title must be unique for the project. Change the Title"

    else:
        context = {'project': project}
        data['html_form'] = render_to_string('scenario/includes/partial_scenario_create.html', context, request=request)

    return JsonResponse(data)


@login_required
def scenario_duplicate(request, pk):
    """
        If requested using GET This loads a partial that is shown in a modal
        If requested using POST make a copy of the scenario
    """
    scenario = get_object_or_404(Scenario, pk=pk)
    data = dict()
    if request.method == 'POST':

        scenario_areal_features = ScenarioArealFeature.objects.filter(scenario=scenario)
        scenario_structures = ScenarioStructure.objects.filter(scenario=scenario)
        scenario_cost_item_costs = ScenarioCostItemUserCosts.objects.filter(scenario=scenario)
        scenario_structure_cost_item_factors = StructureCostItemUserFactors.objects.filter(scenario=scenario)

        scenario.pk = None

        form_variable_scenario_title = request.POST.get("scenario_title", None)
        if form_variable_scenario_title:
            scenario.scenario_title = form_variable_scenario_title
        else:
            scenario.scenario_title += ' (copy)'

        try:
            scenario.save()

            # duplicate all the existing rows
            for s in scenario_areal_features:
                s.pk = None
                s.scenario = scenario
                s.save()

            for s in scenario_cost_item_costs:
                s.pk = None
                s.scenario = scenario
                s.save()

            for s in scenario_structures:
                s.pk = None
                s.scenario = scenario
                s.save()

            for s in scenario_structure_cost_item_factors:
                s.pk = None
                s.scenario = scenario
                s.save()

            data['form_is_valid'] = True

        except IntegrityError:
            data['exception'] = "Scenario Title must be unique for the project. Change the Title"

    else:
        context = {'scenario': scenario}
        data['html_form'] = render_to_string('scenario/includes/partial_scenario_duplicate.html', context,
                                             request=request)

    return JsonResponse(data)


@login_required
# @sql_query_debugger
def scenario_update(request, pk):
    """

        This is the function that displays the Cost Tool.
        It loads everything known about the scenario into the template
        and then javascript stuff does a bunch of work

        available via /scenario/{id}/update

    """
    queryset = Scenario.objects \
        .select_related('project', 'project__user', 'project__user__profile') \
        .filter(pk=pk)
    scenario = get_object_or_404(queryset)

    # get a serialized copy of the scenario and in the user's browser it will be loaded into the UI
    serializer_class = ScenarioSerializer
    serializer = serializer_class(scenario)

    areal_features = ArealFeatureLookup.objects.all().order_by("sort_nu")

    structures = Structures.objects.all().order_by("sort_nu")

    cost_items = CostItem.objects.all()

    cost_item_user_costs = ScenarioCostItemUserCosts.objects \
        .select_related('scenario', 'costitem') \
        .filter(scenario__id=scenario.id)

    default_cost_item_costs = CostItemDefaultCosts.objects \
        .select_related('costitem') \
        .all().order_by('costitem__sort_nu', '-valid_start_date_tx')

    default_cost_item_equations = CostItemDefaultEquations.objects \
        .select_related('costitem') \
        .all().order_by('costitem__sort_nu')

    # move 2 fields from equations into costs - for the Cost Item Unit Costs page
    for cost_item in cost_items:
        cost_item_equations_objs = [x for x in default_cost_item_equations if
                                    x.costitem.code == cost_item.code]

        cost_item.default_costs = [x for x in default_cost_item_costs if
                                    x.costitem.code == cost_item.code]
        # use this to be the default selected option on the page
        # cost_item.default_costs[0].selected = True

        if cost_item_equations_objs is not None and len(cost_item_equations_objs) > 0:
            cost_item_equations_obj = cost_item_equations_objs[0]

            cost_item.replacement_life = cost_item_equations_obj.replacement_life
            cost_item.o_and_m_pct = cost_item_equations_obj.o_and_m_pct
        else:
            cost_item.replacement_life = 999
            cost_item.o_and_m_pct = 999

    # move 2 fields from equations into costs
    for cost_item_costs in default_cost_item_costs:
        cost_item_equations_objs = [x for x in default_cost_item_equations if
                                    x.costitem.code == cost_item_costs.costitem.code]

        if cost_item_equations_objs is not None and len(cost_item_equations_objs) > 0:
            cost_item_equations_obj = cost_item_equations_objs[0]

            cost_item_costs.replacement_life = cost_item_equations_obj.replacement_life
            cost_item_costs.o_and_m_pct = cost_item_equations_obj.o_and_m_pct
        else:
            cost_item_costs.replacement_life = 999
            cost_item_costs.o_and_m_pct = 999

    # struggling with new storage
    # if cost_item_user_costs.count() == 0:
    #     for cost_item in cost_items:
    #         default_costs = [x for x in default_cost_item_costs if
    #                                    x.costitem.code == cost_item.code]

    context = {
        'scenario': serializer.data,
        'project': scenario.project,
        'areal_features': areal_features,
        'structures': structures,
        'cost_items': cost_items,
        'cost_item_user_costs': cost_item_user_costs,
        'cost_item_default_costs': default_cost_item_costs,
        'IIS_APP_ALIAS': settings.IIS_APP_ALIAS,
    }
    return render(request, 'scenario/costtool/index.html', context)


@login_required
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
        data['html_form'] = render_to_string('scenario/includes/partial_scenario_delete.html',
                                             context, request=request)
    return JsonResponse(data)


class TemplateScenario(APIView):
    """

    this returns a JSON template stored in the Scenario model
    it is used to toggle disable/enable and look through fields

    """
    template_version = Scenario.templateScenario

    def get(self, request):
        return Response(self.template_version)


class StructureHelp(APIView):
    """
    I think this is aspirational and not used yet.  It should work just like the help for CostItem (see below)
    Currently, the help for Structures is wired into the page content and toggled on/off
    """
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


def structure_help_html(structure_meta, structure_code):
    template_name = "scenario/includes/partial_structure_help.html"
    context = {
        'structure_code': structure_code,
        'structure_meta': structure_meta,
    }
    return render_to_string(template_name, context)


class CostItemHelp(APIView):
    """
    return an HTML snippet when the Cost Item label is clicked in either the
       Cost Item Unit Costs tab or the
       Structure Cost Item User Factors tab
    """
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, multiple_pks):
        pass

    def get(self, request, costitem_code):
        costitem_meta = CostItem.objects.filter(code=costitem_code)
        default_cost_item_cost = None
        if len(costitem_meta) == 0:
            costitem_meta = CostItem.objects.all()
        else:
            default_cost_item_cost = CostItemDefaultCosts.objects \
                .select_related('costitem') \
                .filter(costitem__code=costitem_code).first()
            costitem_meta = costitem_meta[0]

        # return the scenario as an HTML table
        return HttpResponse(costitem_help_html(costitem_meta, costitem_code, default_cost_item_cost))


def costitem_help_html(costitem_meta, costitem_code, cost_item_default_cost):
    template_name = "scenario/includes/partial_costitem_help.html"
    context = {
        'costitem_code': costitem_code,
        'costitem_meta': costitem_meta,
        'cost_item_default_cost': cost_item_default_cost,
    }
    return render_to_string(template_name, context)


# @sql_query_debugger
def results_table_html(scenario):
    """
    generate the Results table and return as an HTML string

    :param scenario:
    :return:
    """
    logger.debug("################################ results_table_html({})".format(scenario))

    template_name = "scenario/results.html"

    serializer_class = ScenarioSerializer
    serializer = serializer_class(scenario)

    sum_values = {}

    areal_features_sum_area = 0
    conventional_structure_sum_area = 0
    nonconventional_structure_sum_area = 0

    if serializer.data['a_features']:
        for obj in serializer.data['a_features']:
            if obj['is_checked'] is True and obj['area'] != "0" and obj['area'] is not None:
                areal_features_sum_area += int(float(obj['area']))
                obj['label'] = obj['areal_feature_name']
            else:
                obj['area'] = 0
                obj['label'] = obj['areal_feature_name']

    sum_values['areal_features_sum_area'] = areal_features_sum_area

    pervious_area = 0
    impervious_area = 0
    try:
        pervious_area = int(float(serializer.data['embedded_scenario']['pervious_area']))
    except TypeError:
        pass
    try:
        impervious_area = int(float(serializer.data['embedded_scenario']['impervious_area']))
    except TypeError:
        pass

    sum_values['pervious_impervious_area'] = pervious_area + impervious_area

    for test_structure in serializer.data['c_structures']:
        if test_structure['is_checked'] is True and test_structure['area'] is not None:
            conventional_structure_sum_area += int(float(test_structure['area']))
    sum_values['conventional_structure_sum_area'] = conventional_structure_sum_area
    for test_structure in serializer.data['nc_structures']:
        if test_structure['is_checked'] is True and test_structure['area'] is not None:
            nonconventional_structure_sum_area += int(float(test_structure['area']))
    sum_values['nonconventional_structure_sum_area'] = nonconventional_structure_sum_area

    # load the labels for Cost Items
    cost_item_default_costs = CostItemDefaultCosts.objects \
        .select_related('costitem') \
        .all().order_by("costitem__sort_nu")

    cost_item_default_equations = CostItemDefaultEquations.objects \
        .select_related('costitem') \
        .only('costitem__code', 'replacement_life', 'o_and_m_pct') \
        .all().order_by("costitem__sort_nu")

    for cost_item_obj in cost_item_default_costs:
        default_equations_objs = [x for x in cost_item_default_equations if x.costitem_id == cost_item_obj.id]
        if default_equations_objs is not None and len(default_equations_objs) > 0:
            default_equations_obj = default_equations_objs[0]

            cost_item_obj.replacement_life = default_equations_obj.replacement_life
            cost_item_obj.o_and_m_pct = default_equations_obj.o_and_m_pct
        else:
            cost_item_obj.replacement_life = -88
            cost_item_obj.o_and_m_pct = -88

    cost_item_user_cost = serializer.data['cost_item_user_costs']

    cost_item_user_cost_dict = {}
    for o in cost_item_user_cost:
        cost_item_user_cost_dict[o['costitem_code']] = o

    cost_item_costs = []

    for cost_item_obj in cost_item_user_cost:
        code = cost_item_obj['costitem_code']
        cost_source_tx = 'Eng. Est.'

        unit_cost = 222222222222222
        base_year = ''
        replacement_life = cost_item_obj['replacement_life']
        replacement_life_source = 'Default'
        o_and_m_pct = cost_item_obj['o_and_m_pct']
        o_and_m_pct_source = 'Default'

        if cost_item_obj['cost_source'] == 'user':
            cost_source_tx = 'User'
            if cost_item_obj['user_input_cost'] is None:
                unit_cost = Money(0.00, 'USD')
            else:
                unit_cost = Money(cost_item_obj['user_input_cost'], 'USD')
            base_year = cost_item_obj['base_year']
        elif 'default_cost' in cost_item_obj and cost_item_obj['default_cost'] is not None:
            d = cost_item_obj['default_cost']
            cost_source_tx = d['cost_type']
            base_year = d['valid_start_date_tx']
            unit_cost = Money(d['value_numeric'], 'USD')  # TODO fix misspelling. should be value_numeric

        # if code in cost_item_user_cost_dict:
        #     # update stuff
        #     if cost_item_user_cost_dict[code]['replacement_life'] != replacement_life:
        #         replacement_life = cost_item_user_cost_dict[code]['replacement_life']
        #         replacement_life_source = 'User'
        #
        #     if cost_item_user_cost_dict[code]['o_and_m_pct'] != o_and_m_pct:
        #         o_and_m_pct = cost_item_user_cost_dict[code]['o_and_m_pct']
        #         o_and_m_pct_source = 'User'
        #
        #     if cost_item_user_cost_dict[code]['cost_source'] == 'user':
        #         cost_source_tx = 'User'
        #         if cost_item_user_cost_dict[code]['user_input_cost'] is None:
        #             unit_cost = Money(0.00, 'USD')
        #         else:
        #             unit_cost = Money(cost_item_user_cost_dict[code]['user_input_cost'], 'USD')
        #         base_year = cost_item_user_cost_dict[code]['base_year']
        #     # TBD the cost_source text should match, or almost match, the variable name
        #     elif 'default_cost' in cost_item_user_cost_dict[code] and cost_item_user_cost_dict[code][
        #         'default_cost'] is not None:
        #         d = cost_item_user_cost_dict[code]['default_cost']
        #         cost_source_tx = "{} - {} - {}".format(d['cost_type'], d['valid_numeric'], d['valid_start_date_tx'])
        #         unit_cost = Money(d['valid_start_date_tx'], 'USD')
        #     else:
        #         cost_source_tx = 'NOT WORKING CORRECTLY'
        #         unit_cost = 6666666666666666

        cost_item_costs.append({
            'code': cost_item_obj['costitem_code'],
            'label': cost_item_obj['costitem_name'],
            'units': cost_item_obj['units'],

            'cost_source': cost_source_tx,
            'unit_cost': unit_cost.amount,
            'base_year': base_year,
            'replacement_life': replacement_life,
            'replacement_life_source': replacement_life_source,
            'o_and_m_pct': o_and_m_pct,
            'o_and_m_pct_source': o_and_m_pct_source
        })

    # for cost_item_obj in cost_item_costs:
    #     code = cost_item_obj['code']
    #
    #     if code in cost_item_user_cost_dict:
    #         # update stuff
    #         cost_item_obj['replacement_life'] = cost_item_user_cost_dict[code]['replacement_life']
    #         cost_item_obj['o_and_m_pct'] = cost_item_user_cost_dict[code]['o_and_m_pct']
    #
    #         if cost_item_user_cost_dict[code]['cost_source'] == 'user':
    #             cost_item_obj['cost_source'] = 'User'
    #             # change the value to a Money
    #             cost_item_obj['unit_cost'] = Money(cost_item_user_cost_dict[code]['user_input_cost'] or '0.00',
    #                                                'USD').amount
    #             cost_item_obj['base_year'] = cost_item_user_cost_dict[code]['base_year']

    # for cost_item_obj in cost_item_default_costs:
    #     code = cost_item_obj.costitem.code
    #     cost_source_tx = 'Eng. Est.'
    #
    #     unit_cost = cost_item_obj.rsmeans_va
    #     base_year = ''
    #     replacement_life = cost_item_obj.replacement_life
    #     replacement_life_source = 'Default'
    #     o_and_m_pct = cost_item_obj.o_and_m_pct
    #     o_and_m_pct_source = 'Default'
    #
    #     if code in cost_item_user_cost_dict:
    #         # update stuff
    #         if cost_item_user_cost_dict[code]['replacement_life'] != replacement_life:
    #             replacement_life = cost_item_user_cost_dict[code]['replacement_life']
    #             replacement_life_source = 'User'
    #
    #         if cost_item_user_cost_dict[code]['o_and_m_pct'] != o_and_m_pct:
    #             o_and_m_pct = cost_item_user_cost_dict[code]['o_and_m_pct']
    #             o_and_m_pct_source = 'User'
    #
    #         if cost_item_user_cost_dict[code]['cost_source'] == 'user':
    #             cost_source_tx = 'User'
    #             if cost_item_user_cost_dict[code]['user_input_cost'] is None:
    #                 unit_cost = Money(0.00, 'USD')
    #             else:
    #                 unit_cost = Money(cost_item_user_cost_dict[code]['user_input_cost'], 'USD')
    #             base_year = cost_item_user_cost_dict[code]['base_year']
    #         # TBD the cost_source text should match, or almost match, the variable name
    #         elif 'default_cost' in cost_item_user_cost_dict[code] and cost_item_user_cost_dict[code]['default_cost'] is not None:
    #             d = cost_item_user_cost_dict[code]['default_cost']
    #             cost_source_tx = "{} - {} - {}".format(d['cost_type'], d['valid_numeric'], d['valid_start_date_tx'])
    #             unit_cost = Money(d['valid_start_date_tx'], 'USD')
    #         else:
    #             cost_source_tx = 'NOT WORKING CORRECTLY'
    #             unit_cost = 6666666666666666
    #
    #     cost_item_costs.append({
    #         'code': cost_item_obj.costitem.code,
    #         'label': cost_item_obj.costitem.name,
    #         'units': cost_item_obj.costitem.units,
    #
    #         'cost_source': cost_source_tx,
    #         'unit_cost': unit_cost.amount,
    #         'base_year': base_year,
    #         'replacement_life': replacement_life,
    #         'replacement_life_source': replacement_life_source,
    #         'o_and_m_pct': o_and_m_pct,
    #         'o_and_m_pct_source': o_and_m_pct_source
    #     })



    #
    # TODO: now create the computed costs part
    #
    cost_results = scenario.get_costs()

    # dictionary (should be a set) to record which cost items are used
    # in the final results.  later used to remove cost item unit costs if they are not used
    # cost_items_seen = set()
    # for classification in ['conventional', 'nonconventional']:
    #     for structure in cost_results[classification]['structures']:
    #         for cost_item in cost_results[classification]['structures'][structure]['cost_data']:
    #             cost_items_seen.add(cost_item)

    # this was not a good idea.
    # remove cost items if they are not used in any cost calculation
    # final_cost_item_costs = []
    # for cost_item in cost_item_costs:
    #     if cost_item['code'] in cost_items_seen:
    #         final_cost_item_costs.append(cost_item)

    project_life_cycle_costs = cost_results.pop('project_life_cycle_costs')
    structure_life_cycle_costs = cost_results.pop('structure_life_cycle_costs')
    cost_results_additional = cost_results

    context = {'scenario': serializer.data,
               'cost_item_costs': cost_item_costs,
               'cost_results': cost_results,
               'cost_results_additional': cost_results_additional,
               'sum_values': sum_values,
               'structure_life_cycle_costs': structure_life_cycle_costs,
               'project_life_cycle_costs': project_life_cycle_costs}

    return render_to_string(template_name, context)


def comparison_column(left_scenario, right_scenario):
    """

    generate the Results table and return as an HTML string

    :param left_scenario:
    :param right_scenario:
    :return:
    """
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

    diff['pervious_area'] = (left.pervious_area if left.pervious_area is not None else 0) - (
        right.pervious_area if right.pervious_area is not None else 0)
    diff['impervious_area'] = (left.impervious_area if left.impervious_area is not None else 0) - (
        right.impervious_area if right.impervious_area is not None else 0)

    diff['pervious'] = False
    if left.impervious_area != right.impervious_area:
        diff['pervious'] = True

    left_total = left_costs['project_life_cycle_costs']['total']
    right_total = right_costs['project_life_cycle_costs']['total']

    costs = dict()
    costs['construction'] = left_total['construction'] - right_total['construction']
    costs['planning_and_design'] = left_total['planning_and_design'] - right_total['planning_and_design']
    costs['o_and_m'] = left_total['o_and_m'] - right_total['o_and_m']
    costs['replacement'] = left_total['replacement'] - right_total['replacement']
    costs['total'] = costs['construction'] + costs['planning_and_design'] + \
                     costs['o_and_m'] + costs['replacement']

    diff['project_life_cycle_costs'] = costs

    # left_total = left_costs['project_life_cycle_costs']['conventional']['costs']
    # right_total = right_costs['project_life_cycle_costs']['conventional']['costs']

    for structure_type in ['conventional', 'nonconventional']:
        left_total = left_costs['project_life_cycle_costs'][structure_type]['costs']
        right_total = right_costs['project_life_cycle_costs'][structure_type]['costs']

        costs = dict()
        costs['construction'] = left_total['construction'] - right_total['construction']
        costs['planning_and_design'] = left_total['planning_and_design'] - right_total['planning_and_design']
        costs['o_and_m'] = left_total['o_and_m'] - right_total['o_and_m']
        costs['replacement'] = left_total['replacement'] - right_total['replacement']
        costs['total'] = costs['construction'] + \
                         costs['planning_and_design'] + \
                         costs['o_and_m'] + costs['replacement']

        diff[structure_type] = costs

    # left_total = left_costs['project_life_cycle_costs']['nonconventional']['costs']
    # right_total = right_costs['project_life_cycle_costs']['nonconventional']['costs']

    # costs = dict()
    # costs['construction'] = left_total['construction'] - right_total['construction']
    # costs['planning_and_design'] = left_total['planning_and_design'] - right_total['planning_and_design']
    # costs['o_and_m'] = left_total['o_and_m'] - right_total['o_and_m']
    # costs['replacement'] = left_total['replacement'] - right_total['replacement']
    # costs['total'] = costs['construction'] + costs['planning_and_design'] + \
    #                  costs['o_and_m'] + costs['replacement']
    #
    # diff['nonconventional'] = costs

    areal_features = {
        'total_area': 0,
        'item_list': {}
    }

    # # region old treatment
    # serializer_class = ScenarioSerializer
    # left_serializer = serializer_class(left_scenario)
    # right_serializer = serializer_class(right_scenario)
    #
    # diff_area_sum = 0
    # for left_obj in left_serializer.data['a_features']:
    #     code = left_obj['areal_feature_code']
    #     right_obj = None
    #     for obj in right_serializer.data['a_features']:
    #         if obj['areal_feature_code'] == code:
    #             right_obj = obj
    #             break
    #
    #     right_area = right_obj['area'] if right_obj is not None and right_obj['is_checked'] is True else 0
    #     left_area = left_obj['area'] if left_obj['is_checked'] is True else 0
    #     diff_area = left_area if left_area is not None else 0 - right_area if right_area is not None else 0
    #     diff_area_sum += diff_area
    #     areal_features['item_list'][code] = {'label': left_obj['areal_feature_name'], 'area': diff_area}
    #     if code == 'stormwater_management_feature':
    #         areal_features['item_list'][code]['project_land_unit_cost'] = \
    #             left_scenario.project.land_unit_cost
    #         areal_features['item_list'][code]['project_land_cost_diff'] = \
    #             (left_area if left_area is not None else 0 -
    #                                                      right_area if right_area is not None else 0) * left_scenario.project.land_unit_cost
    #
    # areal_features['total_area'] = diff_area_sum
    # diff['areal_features'] = areal_features
    # # endregion old treatment

    # region new treatment
    a_features = {
        'total_area': 0,
        'item_list': {}
    }

    areal_features = ArealFeatureLookup.objects.all().order_by('sort_nu')
    left_areal_features = ScenarioArealFeature.objects \
        .filter(scenario=left_scenario).values('areal_feature_id', 'scenario_id', 'area', 'is_checked')
    right_areal_features = ScenarioArealFeature.objects \
        .filter(scenario=right_scenario).values('areal_feature_id', 'scenario_id', 'area', 'is_checked')

    left_dict = {}
    right_dict = {}
    for obj in left_areal_features:
        left_dict[obj['areal_feature_id']] = obj
    for obj in right_areal_features:
        right_dict[obj['areal_feature_id']] = obj

    diff_area_sum = 0
    for areal_feature in areal_features:

        left_area = 0
        right_area = 0
        if areal_feature.id in left_dict:
            left_area = left_dict[areal_feature.id]['area']
        if areal_feature.id in right_dict:
            right_area = right_dict[areal_feature.id]['area']

        if left_area is None and right_area is None:
            diff_area = 'N/A'
        else:
            diff_area = (left_area if left_area is not None else 0) - (right_area if right_area is not None else 0)

        # diff_area = left_area - right_area
        a_features['item_list'][areal_feature.code] = {'label': areal_feature.name, 'area': diff_area, 'diff_area': '-999'}
        diff_area_sum += diff_area

        # if areal_feature.code in list_of_values:
        #     area_value = list_of_values[areal_feature.code]['area'] or None
        #     is_checked = list_of_values[areal_feature.code]['checkbox'] or False
    diff['areal_features'] = a_features
    # endregion new treatment

    context = {
        'diff': diff,
    }

    return render_to_string(template_name, context)

# endregion Scenario
