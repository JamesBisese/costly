from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator

from rest_framework import viewsets, mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework import serializers
from scenario.decorators import sql_query_debugger

from authtools.models import User
from scenario.models import Project, \
    Scenario, \
    Structures, CostItem, CostItemDefaultCosts, \
    ScenarioCostItemUserCosts, CostItemDefaultEquations, \
    StructureCostItemDefaultFactors, StructureCostItemUserFactors

from scenario.serializers import UserSerializer, ProjectSerializer, \
    ScenarioListSerializer, ScenarioSerializer, ScenarioAuditSerializer, \
    StructureSerializer, CostItemSerializer, CostItemDefaultCostSerializer, \
    ScenarioCostItemUserCostsSerializer, CostItemDefaultEquationsSerializer, \
    StructureCostItemDefaultFactorsSerializer, StructureCostItemUserFactorsSerializer

"""
    generate and return data via 'api' calls.  aka return JSON data
"""

class UserViewSet(UserPassesTestMixin, viewsets.ViewSet):
    def test_func(self):
        return self.request.user.is_active

    """
        provided via /api/users
    """
    # .only('name', 'organization_tx', 'email', 'job_title', 'phone_tx', 'date_joined', 'last_login', 'is_staff', 'is_superuser',
    #       'profile__user_type')\
    queryset = User.objects\
        .select_related('profile')\
        .all().order_by('name')
    serializer_class = UserSerializer


    def get_queryset(self):
        qs = super(UserViewSet, self).get_queryset()

        if not (self.request.user.is_superuser or self.request.user.is_staff):
            qs = qs.filter(id=self.request.user.id)

        code = self.request.query_params.get('id', None)
        if code is not None:
            qs = qs.filter(id=code)

        return qs

    # @sql_query_debugger
    def list(self, request):
        if not (self.request.user.is_superuser or self.request.user.is_staff):
            self.queryset = self.queryset.filter(id=self.request.user.id)

        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)


class ProjectViewSet(UserPassesTestMixin, mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    def test_func(self):
        return self.request.user.is_active
    """
    this is what populates the Scenario table

        provided via /api/projects

    """
    queryset = Project.objects \
        .select_related('user', 'user__profile') \
        .only('project_title', 'project_ownership', 'project_type',
              'project_area', 'land_unit_cost', 'project_location',
              'project_purchase_information',
              'create_date', 'modified_date',
              'user__name', 'user__email', 'user__phone_tx', 'user__job_title', 'user__organization_tx',
              'user__is_active', 'user__is_staff', 'user__is_superuser', 'user__date_joined', 'user__last_login',
              'user__profile__user_type') \
        .annotate(num_scenarios=Count('scenario'))\
        .all().order_by('project_title')
    serializer_class = ProjectSerializer

    # @sql_query_debugger
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


class ProjectScenarioViewSet(viewsets.ModelViewSet):
    """
        /api/project/{pk}/scenarios
    """
    pk = 1
    queryset = Scenario.objects\
        .select_related('project', 'project__user', 'project__user__profile') \
        .only('project__project_title', 'project__project_type', 'project__project_ownership',
              'project__project_area', 'project__land_unit_cost', 'project__project_location',
              'project__project_purchase_information',
              'project__user__name', 'project__user__phone', 'project__user__organization_tx',
              'project__user__profile__user_type') \
        .filter(project__id=pk)\
        .order_by('project__project_title', 'scenario_title')
    serializer_class = ScenarioSerializer

    def get_queryset(self):
        qs = super(ProjectScenarioViewSet, self).get_queryset()
        return qs


class StructureViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    """
        provided via /api/structures and /api/structures/?code=TBD
    """
    queryset = Structures.objects.all().order_by("sort_nu")
    serializer_class = StructureSerializer

    @method_decorator(staff_member_required, name='dispatch')
    def create(self, request):
        serializer = StructureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        qs = super(StructureViewSet, self).get_queryset()
        code = self.request.query_params.get('code', None)
        if code is not None:
            qs = qs.filter(code=code)
        return qs

    @method_decorator(staff_member_required, name='dispatch')
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class CostItemViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    """
        provided via /api/costitems and /api/costitems/?code=fill
    """
    queryset = CostItem.objects.all().order_by("sort_nu")
    serializer_class = CostItemSerializer

    @method_decorator(staff_member_required, name='dispatch')
    def create(self, request):
        serializer = CostItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        qs = super(CostItemViewSet, self).get_queryset()

        code = self.request.query_params.get('code', None)
        if code is not None:
            qs = qs.filter(code=code)

        return qs

    @method_decorator(staff_member_required, name='dispatch')
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class CostItemDefaultCostViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    """
        provided via /api/costitemdefaultcosts and /api/costitemdefaultcosts/?code=fill
    """
    queryset = CostItemDefaultCosts.objects\
        .select_related('costitem')\
        .all().order_by("costitem__sort_nu")
    serializer_class = CostItemDefaultCostSerializer

    def get_queryset(self):
        qs = super(CostItemDefaultCostViewSet, self).get_queryset()

        code = self.request.query_params.get('code', None)
        if code is not None:
            qs = qs.filter(costitem__code=code)

        return qs



class CostItemUserCostViewSet(UserPassesTestMixin, viewsets.ModelViewSet):
    """

        provided via /api/cost_item_user_costs and /api/costitem_user_costs/?code=fill
    TODO: remove the extra fields for this.  there is too much going on in the serializer
    """
    def test_func(self):
        return self.request.user.is_active

    queryset = ScenarioCostItemUserCosts.objects\
        .select_related('costitem', 'scenario', 'scenario__project',
                        'scenario__project__user', 'scenario__project__user__profile')\
        .all().order_by("costitem__sort_nu")
    serializer_class = ScenarioCostItemUserCostsSerializer

    def get_queryset(self):
        qs = super(CostItemUserCostViewSet, self).get_queryset()

        if not (self.request.user.is_superuser or self.request.user.is_staff):
            qs = qs.filter(scenario__project__user=self.request.user)

        code = self.request.query_params.get('scenario', None)
        if code is not None:
            qs = qs.filter(scenario__id=code)

        code = self.request.query_params.get('code', None)
        if code is not None:
            qs = qs.filter(costitem__code=code)

        return qs


class CostItemDefaultEquationsAndFactors(LoginRequiredMixin, viewsets.ModelViewSet):
    """
        provided via /api/costitemdefaultequations and
        /api/costitemdefaultassumptions/?structure=pond&costitem=fill
    """
    queryset = CostItemDefaultEquations.objects \
        .select_related('costitem') \
        .all().order_by('costitem__sort_nu')
    serializer_class = CostItemDefaultEquationsSerializer

    def get_queryset(self):
        qs = super(CostItemDefaultEquationsAndFactors, self).get_queryset()

        code = self.request.query_params.get('costitem', None)
        if code is not None:
            qs = qs.filter(costitem__code=code)

        return qs


class StructureCostItemDefaultFactorsViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    """
        provided via
        /api/costitemdefaultfactors and
        /api/costitemdefaultfactors/?structure=pond and
        /api/costitemdefaultfactors/?structure=pond&costitem=clearing


    """
    queryset = StructureCostItemDefaultFactors.objects \
        .select_related('costitem', 'structure') \
        .all().order_by('structure__sort_nu', 'costitem__sort_nu')
    serializer_class = StructureCostItemDefaultFactorsSerializer

    def get_queryset(self):
        qs = super(StructureCostItemDefaultFactorsViewSet, self).get_queryset()

        code = self.request.query_params.get('structure', None)
        if code is not None:
            qs = qs.filter(structure__code=code)

        code = self.request.query_params.get('costitem', None)
        if code is not None:
            qs = qs.filter(costitem__code=code)

        return qs


class ScenarioViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    """
        provided via /api/scenarios and /api/scenarios/<pk:i>/

        also via /api/scenarios/?project=<int>

        Detailed scenario instance(s)

    """
    queryset = Scenario.objects \
        .select_related('project', 'project__user', 'project__user__profile') \
        .only(
            'scenario_title',
            'captures_90pct_storm', 'meets_peakflow_req', 'nutrient_req_met',
            'pervious_area', 'impervious_area',
            'planning_and_design_factor', 'study_life', 'discount_rate', 'project__priority_watershed',
            'create_date', 'modified_date',
            'project__project_title', 'project__project_type', 'project__project_ownership',
            'project__project_area',
            'project__land_unit_cost', 'project__land_unit_cost_currency',
            'project__project_location',
            'project__project_purchase_information',
            'project__user__profile__user_type',
            'project__user__email',
            'project__user__job_title',
            'project__user__last_login', 'project__user__date_joined',
            'project__user__is_staff', 'project__user__is_superuser',
            'project__user__name', 'project__user__phone_tx', 'project__user__organization_tx',
            'project__user__profile__user_type'
        ) \
        .all().order_by('project__project_title', 'scenario_title')


    # this serializer contains all the details
    serializer_class = ScenarioSerializer

    # @sql_query_debugger
    def get_queryset(self):
        qs = super(ScenarioViewSet, self).get_queryset()

        if not (self.request.user.is_superuser or self.request.user.is_staff):
            qs = qs.filter(project__user=self.request.user)

        # this is getting a single scenario by id
        id = self.request.query_params.get('id', None)
        if id is not None:
            qs = qs.filter(id=id)
        # this is getting a list of scenarios for a project
        project = self.request.query_params.get('project', None)
        if project is not None:
            qs = qs.filter(project__id=project)

        return qs


class ScenarioListViewSet(UserPassesTestMixin, viewsets.ModelViewSet):
    """
        provided via /api/scenario_list and /api/scenario_list.<pk:i>/

    """
    def test_func(self):
        return self.request.user.is_active

    queryset = Scenario.objects\
        .select_related('project', 'project__user', 'project__user__profile') \
        .only('project__project_title',
              'project__user__job_title',
              'project__user__last_login', 'project__user__date_joined',
              'project__user__is_staff', 'project__user__is_superuser',
              'scenario_title', 'create_date', 'modified_date',
              'nutrient_req_met', 'captures_90pct_storm',
              'meets_peakflow_req', 'pervious_area', 'impervious_area',
              'create_date', 'modified_date',
               ) \
        .all().order_by('id')
    # serializer_class = ScenarioSerializer

    # this is the change required to use this on the list
    serializer_class = ScenarioListSerializer  # jab 2019-05-24 ScenarioSerializer

    # @sql_query_debugger
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


class ScenarioAuditViewSet(UserPassesTestMixin, viewsets.ModelViewSet):
    """
        provided via /api/scenario_audit and /api/scenarios/<pk:i>/ where pk is Scenario.id

    """
    def test_func(self):
        return self.request.user.is_active

    # .only('project__project_title',
    #       # 'project__project_type', 'project__project_ownership',
    #       # 'project__project_area', 'project__land_unit_cost', 'project__project_location',
    #       # 'project__project_purchase_information',
    #       'project__user__name', 'project__user__phone_tx', 'project__user__organization_tx',
    #       # 'project__create_date', 'project__modified_date',
    #       'project__user__profile__user_type',
    #       'scenario_title', 'create_date', 'modified_date', ) \
    queryset = Scenario.objects \
        .select_related('project', 'project__user', 'project__user__profile') \
        .all().order_by('id')

    # @sql_query_debugger
    def get_queryset(self):
        qs = super(ScenarioAuditViewSet, self).get_queryset()
        return qs

    # this is the change required to use this on the list
    serializer_class = ScenarioAuditSerializer


class StructureCostItemUserFactorsViewSet(UserPassesTestMixin, viewsets.ModelViewSet):
    """
        provided via /api/structure_user_cost_item_factors
        and /api/structure_user_cost_item_factors/?structure=pond&costitem=fill&scenario=8
    """
    def test_func(self):
        return self.request.user.is_active

    queryset = StructureCostItemUserFactors.objects\
        .select_related('scenario',
                        'scenario__project', 'scenario__project__user', 'scenario__project__user__profile',
                        'structure', 'costitem')\
        .all().order_by('scenario__id', 'structure__sort_nu', 'costitem__sort_nu')
    serializer_class = StructureCostItemUserFactorsSerializer

    def get_queryset(self):
        qs = super(StructureCostItemUserFactorsViewSet, self).get_queryset()

        if not (self.request.user.is_superuser or self.request.user.is_staff):
            qs = qs.filter(scenario__project__user=self.request.user)

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




#
# this is the Structure Cost data in JSON
#
class StructureCosts(UserPassesTestMixin, APIView):
    """
    URI/scenario/<int:pk>/structure_costs/<slug:structure_code>/
    example: /scenario/55/structure_costs/swale/

    """
    def test_func(self):
        return self.request.user.is_active


        # .filter(pk=pk)

    def get(self, request, multiple_pks):
        pass

    # def get_queryset(self):
    #     # qs = super(StructureCosts, self).get_queryset()
    #
    #     qs = Scenario.objects \
    #         .select_related('project')
    #
    #     if not (self.request.user.is_superuser or self.request.user.is_staff):
    #         qs = qs.filter(scenario__project__user=self.request.user)
    #
    #     return qs

    # @sql_query_debugger
    def get(self, request, pk, structure_code, costitem_code=None):

        # pk = self.request.query_params.get('pk', None)
        # structure_code = self.request.query_params.get('structure_code', None)
        # costitem_code = self.request.query_params.get('costitem_code', None)


        queryset = Scenario.objects \
            .select_related('project')\
            .filter(pk=pk)

        if not (self.request.user.is_superuser or self.request.user.is_staff):
            queryset = queryset.filter(project__user_id=self.request.user.id)

        # queryset = self.get_queryset()
        # queryset = queryset.filter(pk=pk)

        scenario = get_object_or_404(queryset)
        serializer_class = ScenarioSerializer
        serializer = serializer_class(scenario)
        scenario_data = serializer

        structure = Structures.objects.get(code=structure_code)

        # debugging
        # costitem_code = None

        """
        this explicit version is to allow filtering for just a certain costitem.
        this is the first time I've used this syntax
        """
        q = {}
        if costitem_code is not None:
            q.update({'costitem__code': costitem_code})

        default_cost_item_costs = CostItemDefaultCosts.objects\
            .select_related('costitem')\
            .filter(**q).order_by("costitem__sort_nu")

        q2 = {}
        q2.update({'structure': structure})
        if costitem_code is not None:
            q2.update({'costitem__code': costitem_code})

        default_cost_item_factors = StructureCostItemDefaultFactors.objects\
            .select_related('structure', 'costitem')\
            .filter(**q2)

        # q3 = {}
        # q3.update({'scenario': scenario})
        # if costitem_code is not None:
        #     q3.update({'costitem__code': costitem_code})
        #
        # scenario_cost_item_costs = ScenarioCostItemUserCosts.objects \
        #     .select_related('costitem', 'scenario') \
        #     .filter(**q3)

        q4 = {}
        q4.update({'scenario__id': pk})
        q4.update({'structure': structure})
        if costitem_code is not None:
            q4.update({'costitem__code': costitem_code})

        scenario_structure_cost_item_factors = StructureCostItemUserFactors.objects\
            .select_related('scenario', 'structure', 'costitem')\
            .filter(**q4)

        cost_item_default_equations = CostItemDefaultEquations.objects \
            .select_related('costitem') \
            .filter(**q).order_by("costitem__sort_nu")

        # return the content as JSON
        return JsonResponse(structure_cost_item_json(structure,
                                                     scenario_data,
                                                     default_cost_item_costs,
                                                     default_cost_item_factors,
                                                     # scenario_cost_item_costs,
                                                     scenario_structure_cost_item_factors,
                                                     cost_item_default_equations
                                                     ))


def structure_cost_item_json(structure,
                             scenario_data,
                             default_cost_item_costs,
                             default_cost_item_factors,
                             # cost_item_user_costs,
                             cost_item_user_assumptions,
                             cost_item_default_equations
                             ):
    """
        This is called when the user changes the 'Structure' selection

        return JSON to cost tool for processing by javascript to populate
        the 'Structure/Cost Item Costs' tab

        ajax call to
        /scenario/<scenario_id>/structure_costs/<structure_code>/?format=json

    """
    structure.area = -9

    for test_structure in scenario_data.data['c_structures']:
        if test_structure['structure_code'] == structure.code:
            structure.area = test_structure['area']
            continue
    if structure.area == -9:
        for test_structure in scenario_data.data['nc_structures']:
            if test_structure['structure_code'] == structure.code:
                structure.area = test_structure['area']
                continue

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

    """
        these are cost items that the user edited on Structure Costs 
        edit can be
        1. checked cost item
        2. set value in Factor Assumptions, Sizing Factor (k) or Sizing Factor (n)
    """
    # jab new - get equation from CostItemDefaultEquations table
    for obj in cost_item_default_equations:
        costitem_code = obj.costitem.code
        structure_costs['data'][costitem_code] = {'equation': obj.equation_tx,
                                                  'units': obj.costitem.units,
                                                  'checked': False,
                                                  # 'a_area': obj.a_area,
                                                  # 'z_depth': obj.z_depth,
                                                  # 'd_density': obj.d_density,
                                                  # 'n_number': obj.n_number,

                                                  'o_and_m_pct': obj.o_and_m_pct,
                                                  'replacement_life': obj.replacement_life,

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
    for obj in default_cost_item_factors:
        costitem_code = obj.costitem.code

        if costitem_code not in seen_costitem_codes:
            structure_costs['data'][costitem_code]['checked'] = True
            structure_costs['data'][costitem_code]['a_area'] = obj.a_area
            structure_costs['data'][costitem_code]['z_depth'] = obj.z_depth
            structure_costs['data'][costitem_code]['d_density'] = obj.d_density
            structure_costs['data'][costitem_code]['n_number'] = obj.n_number

    """
        new change to use defaults from CostItemDefaultEquations table
    """

    # first add in the cost_item_user_costs
    # for obj in cost_item_user_costs:
    for obj in scenario_data.data['cost_item_user_costs']:
        costitem_code = obj['costitem_code']

        cost_source = None
        unit_cost = None

        if 'user_input_cost' in obj and obj['user_input_cost'] is not None:
            # note: this is a Money field
            unit_cost = obj['user_input_cost']

        cost_source = obj['cost_source']

        """
            the only cost data that is available here is the 'user' input costs - not
            rsmean, db25, db50, etc.
        """
        if cost_source == 'user':
            if 'user_input_cost' in obj and obj['user_input_cost'] is not None:
                # note: this is a Money field and this just uses the decimal part
                unit_cost = obj['user_input_cost']


        # add the user costs data
        structure_costs['data'][costitem_code]['cost_source'] = cost_source
        structure_costs['data'][costitem_code]['unit_cost'] = unit_cost
        structure_costs['data'][costitem_code]['o_and_m_pct'] = int(obj['o_and_m_pct'])
        structure_costs['data'][costitem_code]['replacement_life'] = int(obj['replacement_life'] or "0")

    # then add in the default costs to update the non 'user' (cost_source) costs

    for obj in default_cost_item_costs:
        costitem_code = obj.costitem.code

        # make the blank structure
        if not costitem_code in structure_costs['data']:
            structure_costs['data'][costitem_code] = {'cost_source': 'rsmeans'}
            # structure_costs['data'][costitem_code]['cost_source'] = 'rsmeans'

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

        if 'checked' not in cost_item_data:
            cost_item_data['checked'] = False

        if cost_item_data['checked'] is True:

            factors = {
                'a_area': 1,
                'z_depth': 1,
                'd_density': 1,
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
            equation = equation.replace('=', '')
            equation = equation.replace('x', '(' + str(structure.area) + '*' + str(unit_conversion) + ')')
            equation = equation.replace('area', str(factors['a_area']))
            equation = equation.replace('depth', str(factors['z_depth']))
            equation = equation.replace('density', str(factors['d_density']))
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
    if scenario_data['embedded_scenario'].value['planning_and_design_factor'] is None:
        planning_and_design_factor = 0
    else:
        planning_and_design_factor = int(scenario_data['embedded_scenario'].value['planning_and_design_factor'])
    if scenario_data['embedded_scenario'].value['study_life'] is None:
        study_life = 0
    else:
        study_life = int(scenario_data['embedded_scenario'].value['study_life'])
    if scenario_data['embedded_scenario'].value['discount_rate'] is None:
        discount_rate = 0
    else:
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

            structure_costs['data'][cost_item]['costs'] = {
                'construction': construction_cost,
                'planning_and_design': planning_and_design_costs,
                'o_and_m': round(o_and_m_costs, 2),
                'first_replacement': value_of_first_replacement,
                'replacement': round(replacement_costs, 2),
                'replacement_years': replacement_years,
            }

    return structure_costs


def get_unit_conversion(structure_units, cost_item_units):
    """
        convert units between Structure Units and Cost Item units
        i.e. ft2 and square yards, ft2 and AC

    """
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
