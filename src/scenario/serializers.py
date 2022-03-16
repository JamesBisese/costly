from rest_framework import serializers

from .models import Project, Scenario, ArealFeatureLookup, Structures, \
    CostItem, \
    CostItemDefaultCosts, \
    ScenarioCostItemUserCosts, \
    CostItemDefaultEquations, \
    StructureCostItemDefaultFactors, \
    StructureCostItemUserFactors, \
    ScenarioArealFeature, \
    ScenarioStructure
from authtools.models import User
from profiles.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    user_type = serializers.CharField()

    def get_user_type(self, profile):
        return '%s' % profile.user_type.capitalize()
        pass

    class Meta:
        model = Profile
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    #
    name = serializers.CharField()

    def get_name(self, user):
        return '%s' % user.name.lower()

    # end

    # profile = ProfileSerializer()
    profile = serializers.SerializerMethodField()

    def get_profile(self, user):
        fields = {
            'user_type': user.profile.user_type
        }
        return fields

    date_joined = serializers.DateTimeField(format="%Y-%m-%d %I:%M %p %Z")
    last_login = serializers.DateTimeField(format="%Y-%m-%d %I:%M %p %Z")

    class Meta:
        model = User
        fields = (
            # '__all__'
            'id',
            'name',
            'email',
            'phone_tx',
            'organization_tx',
            'job_title',
            'is_active',
            'is_staff',
            'is_superuser',
            'profile',
            'date_joined',
            'last_login',
        )
        # Specifying fields in datatables_always_serialize
        # will also force them to always be serialized.
        datatables_always_serialize = ('id',)

        read_only_fields = [f.name for f in User._meta.get_fields()]


class UserSimpleSerializer(serializers.ModelSerializer):
    #
    name = serializers.CharField()

    def get_name(self, user):
        return '%s' % user.name.lower()

    # end

    # profile = ProfileSerializer()
    user_type = serializers.SerializerMethodField()

    def get_user_type(self, user):
        return user.profile.user_type

    # date_joined = serializers.DateTimeField(format="%Y-%m-%d %I:%M %p %Z")
    # last_login = serializers.DateTimeField(format="%Y-%m-%d %I:%M %p %Z")

    class Meta:
        model = User
        fields = (
            # '__all__'
            'id',
            'name',
            'organization_tx',
            'user_type',
        )
        # Specifying fields in datatables_always_serialize
        # will also force them to always be serialized.
        datatables_always_serialize = ('id',)

        read_only_fields = [f.name for f in User._meta.get_fields()]


class ProjectSerializer(serializers.ModelSerializer):
    # DRF-Datatables can deal with nested serializers as well.
    user = UserSerializer()

    # If you want, you can add special fields understood by Datatables,
    # the fields starting with DT_Row will always be serialized.
    # See: https://datatables.net/manual/server-side#Returned-data
    DT_RowId = serializers.SerializerMethodField()
    DT_RowAttr = serializers.SerializerMethodField()

    project_ownership = serializers.SerializerMethodField()
    project_type = serializers.SerializerMethodField()
    project_purchase_information = serializers.SerializerMethodField()

    create_date = serializers.DateTimeField(format="%Y-%m-%d %I:%M %p %Z")
    modified_date = serializers.DateTimeField(format="%Y-%m-%d %I:%M %p %Z")

    scenario_count = serializers.SerializerMethodField()

    def get_DT_RowId(self, project):
        return 'row_%d' % project.pk

    def get_DT_RowAttr(self, project):
        return {'data-pk': project.pk}

    def get_project_ownership(self, obj):
        return obj.get_project_ownership_display()

    def get_project_type(self, obj):
        return obj.get_project_type_display()

    def get_project_purchase_information(self, obj):
        return obj.get_project_purchase_information_display()

    def get_scenario_count(self, obj):
        # return Scenario.objects.filter(project__id=obj.id).count()
        return obj.num_scenarios

    class Meta:
        model = Project
        fields = (
            'DT_RowId', 'DT_RowAttr',
            'user',
            'id',
            'user',
            'project_title',
            'project_ownership',
            'project_type',
            'project_area',
            'land_unit_cost',
            'project_location',
            'project_purchase_information',
            'scenario_count',
            'create_date',
            'modified_date',
        )
        read_only_fields = [f.name for f in Project._meta.get_fields()]


class EmbeddedProjectSerializer(ProjectSerializer):
    class Meta:
        model = Project
        fields = (
            'project_title',
            'project_ownership',
            'project_type',
            'project_area',
            'land_unit_cost',
            'project_location',
            'project_purchase_information',
            'priority_watershed',
        )
        read_only_fields = [f.name for f in Project._meta.get_fields()]


class EmbeddedProjectFields(serializers.Field):

    def get_project_ownership(self, obj):
        return obj.project.get_project_ownership_display()

    def get_project_type(self, obj):
        return obj.project.get_project_type_display()

    def get_project_purchase_information(self, obj):
        return obj.get_project_purchase_information_display()

    def to_representation(self, value):
        ret = {
            'project_id': value.id,
            'user': {
                'email': value.user.email,
                'name': value.user.name,
                'user_type': value.user.profile.get_user_type_display()
            },
            'project_title': value.project_title,
            # 'scenario_title': value.scenario_title,
            'land_unit_cost': value.land_unit_cost.amount,
            #
            'project_type': value.project_type,
            'project_ownership': value.project_ownership,
            'project_area': value.project_area,
            #
            'project_location': value.project_location,
            'project_purchase_information': value.project_purchase_information,
            'priority_watershed': value.priority_watershed,

            # these are display fields that show the CHOICE text
            'project_type_display': value.get_project_type_display(),
            'project_ownership_display': value.get_project_ownership_display(),
            'project_purchase_information_display': value.get_project_purchase_information_display(),
            'priority_watershed_display': value.get_priority_watershed_display(),
        }
        return ret

    def to_internal_value(self, data):
        ret = {

            'scenario_title': data['scenario_title'],

            'pervious_area': data['pervious_area'],
            'impervious_area': data['impervious_area'],

            'nutrient_req_met': data['nutrient_req_met'],
            'captures_90pct_storm': data['captures_90pct_storm'],
            'meets_peakflow_req': data['meets_peakflow_req'],

        }
        return ret


class EmbeddedScenarioFields(serializers.Field):

    def to_representation(self, value):
        ret = {
            'scenario_id': value.id,
            'scenario_title': value.scenario_title,
            'project_title': value.project.project_title,

            'nutrient_req_met': value.nutrient_req_met,
            'captures_90pct_storm': value.captures_90pct_storm,
            'meets_peakflow_req': value.meets_peakflow_req,

            # these are display fields that show the CHOICE text
            'nutrient_req_met_display': value.get_nutrient_req_met_display(),
            'captures_90pct_storm_display': value.get_captures_90pct_storm_display(),
            'meets_peakflow_req_display': value.get_meets_peakflow_req_display(),

            'pervious_area': value.pervious_area,
            'impervious_area': value.impervious_area,

            "planning_and_design_factor": value.planning_and_design_factor,
            "study_life": value.study_life,
            "discount_rate": value.discount_rate,
        }
        return ret

    def to_internal_value(self, data):
        ret = {
            'scenario_id': data['scenario_id'],
            'scenario_title': data['scenario_title'],

            'nutrient_req_met': data['nutrient_req_met'],
            'captures_90pct_storm': data['captures_90pct_storm'],
            'meets_peakflow_req': data['meets_peakflow_req'],

            'pervious_area': data['pervious_area'],
            'impervious_area': data['impervious_area'],
        }
        return ret


class ArealFeatureLookupSerializer(serializers.ModelSerializer):

    class Meta:
        model = ArealFeatureLookup
        fields = (
            'id',
            'code',
            'name',
            'sort_nu',
            'units',
            'units_html',
            'help_text',
        )
        # read_only_fields = [f.name for f in Structures._meta.get_fields()]

class StructureSerializer(serializers.ModelSerializer):
    classification_display = serializers.SerializerMethodField()

    def get_classification_display(self, obj):
        return obj.get_classification_display()

    class Meta:
        model = Structures
        fields = (
            'id',
            'code',
            'name',
            'classification',
            'classification_display',
            'sort_nu',
            'units',
            'units_html',
            'help_text',
        )
        # read_only_fields = [f.name for f in Structures._meta.get_fields()]


class EmbeddedScenarioArealFeatureSerializer(serializers.ModelSerializer):

    areal_feature_code = serializers.CharField(read_only=True, source="areal_feature.code")
    areal_feature_name = serializers.CharField(read_only=True, source="areal_feature.name")

    class Meta:
        model = ScenarioArealFeature
        fields = (
            'id',
            'areal_feature_code',
            'areal_feature_name',
            'area',
            'is_checked',
        )
        read_only_fields = [f.name for f in ScenarioArealFeature._meta.get_fields()]


class EmbeddedScenarioStructureSerializer(serializers.ModelSerializer):

    structure_code = serializers.CharField(read_only=True, source="structure.code")
    structure_name = serializers.CharField(read_only=True, source="structure.name")

    class Meta:
        model = ScenarioStructure
        fields = (
            'id',
            'structure_code',
            'structure_name',
            'area',
            'is_checked',
            # 'classification',
            # 'classification_display',
            # 'sort_nu',
            # 'units',
            # 'units_html',
            # 'help_text',
        )
        read_only_fields = [f.name for f in ScenarioStructure._meta.get_fields()]

"""

"""


class CostItemSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        many = kwargs.pop('many', True)
        super(CostItemSerializer, self).__init__(many=many, *args, **kwargs)

    class Meta:
        model = CostItem
        fields = (
            'sort_nu',
            'code',
            'name',
            'units',
            'help_text',
        )
        # read_only_fields = [f.name for f in CostItem._meta.get_fields()]


class CostItemDefaultCostSerializer(serializers.ModelSerializer):
    """

        default values
        /api/costitemdefaultcosts

        Note: updated 2022-03-11 to hold multiple values for each CostItem

    """
    costitem = CostItemSerializer(many=False, read_only=True)

    created_date = serializers.DateTimeField(format="%Y-%m-%d %I:%M %p %Z")
    modified_date = serializers.DateTimeField(format="%Y-%m-%d %I:%M %p %Z")

    class Meta:
        model = CostItemDefaultCosts
        fields = (
            'costitem',
            'id',
            # region new storage
            'cost_type',
            'value_numeric',
            'valid_start_date_tx',
            'created_date',
            'modified_date',
            # endregion new storage
            'rsmeans_va',
            'db_25pct_va',
            'db_50pct_va',
            'db_75pct_va',
        )
        read_only_fields = [f.name for f in CostItemDefaultCosts._meta.get_fields()]


class CostItemDefaultEquationsSerializer(serializers.ModelSerializer):
    """
        the logic of the many=False is that in this case,
        there is one structure and one costitem for each 'CostItemDefaultEquations'

    """
    # structure = StructureSerializer(many=False, read_only=True)
    costitem = CostItemSerializer(many=False, read_only=True)

    class Meta:
        model = CostItemDefaultEquations
        fields = (
            'costitem',
            'id',
            'replacement_life',
            'o_and_m_pct',
            'equation_tx',
            'help_text',
        )
        read_only_fields = [f.name for f in CostItemDefaultEquations._meta.get_fields()]


class StructureCostItemDefaultFactorsSerializer(serializers.ModelSerializer):
    """
        the logic of the many=False is that in this case,
        there is one structure and one costitem for each 'CostItemDefaultAssumptions'
    """
    structure = StructureSerializer(many=False, read_only=True)
    costitem = CostItemSerializer(many=False, read_only=True)

    class Meta:
        model = StructureCostItemDefaultFactors
        fields = (
            'structure',
            'costitem',
            'id',
            'a_area',
            'z_depth',
            'd_density',
            'n_number',
        )
        read_only_fields = [f.name for f in StructureCostItemDefaultFactors._meta.get_fields()]


class StructureCostItemUserFactorsSerializer(serializers.ModelSerializer):
    """

    via /api/cost_item_user_factors

    """
    user = serializers.SerializerMethodField()
    structure = StructureSerializer(many=False, read_only=True)
    costitem = CostItemSerializer(many=False, read_only=True)

    def get_user(self, obj):
        user1 = obj.scenario.project.user
        return UserSerializer(user1, many=False).data

    scenario_id = serializers.CharField(read_only=True, source="scenario.id")
    project_title = serializers.CharField(read_only=True, source="scenario.project.project_title")
    scenario_title = serializers.CharField(read_only=True, source="scenario.scenario_title")

    class Meta:
        model = StructureCostItemUserFactors
        fields = (
            'user',
            'scenario_id',
            'project_title',
            'scenario_title',
            'structure',
            'costitem',
            'checked',
            'a_area',
            'z_depth',
            'd_density',
            'n_number',
        )
        read_only_fields = [f.name for f in StructureCostItemUserFactors._meta.get_fields()]


class ScenarioListSerializer(serializers.ModelSerializer):
    """
        this is returned into results in /projects/{pk}/scenario to just
        list all the scenarios is first loaded
        it is used to populate the table on the Scenarios page

        Example:
    http://127.0.0.1:92/api/projects/1/scenarios/

    """

    project_title = serializers.SerializerMethodField()

    def get_project_title(self, scenario):
        return '%s' % scenario.project.project_title

    create_date = serializers.DateTimeField(format="%Y-%m-%d %I:%M %p %Z")
    modified_date = serializers.DateTimeField(format="%Y-%m-%d %I:%M %p %Z")

    nutrient_req_met = serializers.SerializerMethodField()
    captures_90pct_storm = serializers.SerializerMethodField()
    meets_peakflow_req = serializers.SerializerMethodField()

    def get_nutrient_req_met(self, obj):
        return obj.get_nutrient_req_met_display()

    def get_captures_90pct_storm(self, obj):
        return obj.get_captures_90pct_storm_display()

    def get_meets_peakflow_req(self, obj):
        return obj.get_meets_peakflow_req_display()

    DT_RowId = serializers.SerializerMethodField()
    DT_RowAttr = serializers.SerializerMethodField()

    #
    def get_DT_RowId(self, scenario):
        return 'row_%d' % scenario.pk

    def get_DT_RowAttr(self, scenario):
        return {'data-pk': scenario.pk}

    class Meta:
        model = Scenario
        fields = (
            'DT_RowId', 'DT_RowAttr',
            # 'user',
            'id',
            'project_title',

            'scenario_title',

            'nutrient_req_met',
            'captures_90pct_storm',
            'meets_peakflow_req',

            'pervious_area',
            'impervious_area',

            'create_date',
            'modified_date',
        )
        read_only_fields = [f.name for f in Scenario._meta.get_fields()]



class ScenarioAuditSerializer(serializers.ModelSerializer):
    """
    data source for Audit Scenarios

    """
    user = serializers.SerializerMethodField()
    def get_user(self, scenario):
        return {
            'name': scenario.project.user.name,
            'organization_tx': scenario.project.user.organization_tx,
            'user_type': scenario.project.user.profile.user_type
        }
    # user2 = UserSerializer(many=False, read_only=True, source='project.user')
    project2 = serializers.SerializerMethodField()

    def get_project2(self, scenario):
        return {
            'project_title': scenario.project.project_title
        }

    create_date = serializers.DateTimeField(format="%Y-%m-%d %I:%M %p %Z")
    modified_date = serializers.DateTimeField(format="%Y-%m-%d %I:%M %p %Z")

    DT_RowId = serializers.SerializerMethodField()
    DT_RowAttr = serializers.SerializerMethodField()

    def get_DT_RowId(self, scenario):
        return 'row_%d' % scenario.pk

    def get_DT_RowAttr(self, scenario):
        return {'data-pk': scenario.pk}

    class Meta:
        model = Scenario
        fields = (
            'DT_RowId', 'DT_RowAttr',

            'id',
            'user',
            'project2',

            'scenario_title',

            'create_date',
            'modified_date',
        )

        read_only_fields = [f.name for f in Scenario._meta.get_fields()]


class ScenarioCostItemUserCostsSerializer(serializers.ModelSerializer):
    """

        CostItem User Cost - users values

    """
    # each default cost is applied to a single costitem
    # scenario_id = serializers.CharField(read_only=True, source="scenario.id")
    #
    costitem_code = serializers.CharField(read_only=True, source="costitem.code")
    costitem_name = serializers.CharField(read_only=True, source="costitem.name")
    # each default cost is applied to a single costitem

    scenario2 = serializers.SerializerMethodField()
    def get_scenario2(self, obj):
        return {
            'id': obj.scenario.id,
            'scenario_title': obj.scenario.scenario_title
        }

    project = serializers.SerializerMethodField()
    def get_project(self, obj):
        return {'project_title': obj.scenario.project.project_title}

    # ProjectSerializer(source='scenario.project', many=False, read_only=True)

    # costitem = CostItemSerializer(many=False, read_only=True)

    # # NOTE: the underlying model has to have a field marked with matching related_name. (I have no idea why)
    # # i.e. related_name="cost_item_user_costs"
    # cost_item_user_costs = serializers.SerializerMethodField()
    #
    # def get_cost_item_user_costs(self, instance):
    #     user_cost_items = instance.cost_item_user_costs.all().order_by('costitem__sort_nu')
    #     return StructureCostItemUserCostSerializer(user_cost_items, many=True).data

    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        user1 = obj.scenario.project.user
        return UserSimpleSerializer(user1, many=False).data
    # scenario = ScenarioListSerializer(many=False, read_only=True)
    #
    # # the uncommented 'project' controls what fields are included
    # project = EmbeddedProjectFields(source='scenario.project')

    # scenario_id = serializers.SerializerMethodField()
    #
    # def get_scenario_id(self, obj):
    #     return obj.scenario.id

    costitem_code = serializers.SerializerMethodField()

    def get_costitem_code(self, obj):
        return obj.costitem.code

    costitem_name = serializers.SerializerMethodField()

    def get_costitem_name(self, obj):
        return obj.costitem.name

    units = serializers.SerializerMethodField()

    def get_units(self, obj):
        return obj.costitem.units

    o_and_m_pct = serializers.SerializerMethodField()

    def get_o_and_m_pct(self, obj):
        return str(obj.o_and_m_pct)

    default_cost = serializers.SerializerMethodField()

    def get_default_cost(self, obj):
        # return str(obj.default_cost)
        if obj.default_cost is None:
            return None

        l = ['cost_type',
             # 'value_numeric',
             'valid_start_date_tx']
        d = {key: getattr(obj.default_cost, key) for key in l}
        d['value_numeric'] = obj.default_cost.value_numeric.amount

        return d

    class Meta:
        model = ScenarioCostItemUserCosts
        fields = (
            'id',
            'user',
            'scenario2',
            'project',
            # 'scenario_id',
            'costitem',
            'costitem_code',
            'costitem_name',
            'units',
            'cost_source',
            'default_cost',
            'user_input_cost',
            'base_year',
            'replacement_life',
            'o_and_m_pct'
        )
        read_only_fields = [f.name for f in ScenarioCostItemUserCosts._meta.get_fields()]


class ScenarioSerializer(serializers.ModelSerializer):
    """

        serialize all the data for the scenario

        /api/scenarios/1/

     this is returned into results in /scenario/{pk}/update is first loaded


    """
    project = EmbeddedProjectFields()

    embedded_scenario = EmbeddedScenarioFields(source='*')

    # areal_features = EmbeddedArealFeatures()
    # conventional_structures = EmbeddedConventionalStructures()
    # nonconventional_structures = EmbeddedNonConventionalStructures()

    a_features = serializers.SerializerMethodField()

    def get_a_features(self, obj):
        a_features = ScenarioArealFeature.objects\
            .select_related('areal_feature')\
            .filter(scenario=obj)\
            .order_by('areal_feature__sort_nu')
        return EmbeddedScenarioArealFeatureSerializer(a_features, many=True).data

    # 2022-01-12 work on proposed new datamodel for user Structure data
    c_structures = serializers.SerializerMethodField()

    def get_c_structures(self, obj):
        structures = ScenarioStructure.objects \
            .select_related('structure') \
            .filter(scenario=obj, structure__classification='conventional')\
            .order_by('structure__sort_nu')
        return EmbeddedScenarioStructureSerializer(structures, many=True).data

    nc_structures = serializers.SerializerMethodField()

    def get_nc_structures(self, obj):
        structures = ScenarioStructure.objects\
            .select_related('structure')\
            .filter(scenario=obj, structure__classification='nonconventional')\
            .order_by('structure__sort_nu')
        return EmbeddedScenarioStructureSerializer(structures, many=True).data

    # add in other related models that have 1-to-many relationships
    # this works, but only shows the string representation of the user costs
    # cost_item_user_costs = serializers.StringRelatedField(many=True)

    # this just shows the primary key in the target
    # cost_item_user_costs = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    # NOTE: the underlying model has to have a field marked with matching related_name. (I have no idea why)
    # i.e. related_name="cost_item_user_costs"
    cost_item_user_costs = serializers.SerializerMethodField()

    def get_cost_item_user_costs(self, instance):
        user_cost_items = instance.cost_item_user_costs\
            .select_related('costitem', 'default_cost')\
            .all().order_by('costitem__sort_nu')
        return ScenarioCostItemUserCostsSerializer(user_cost_items, many=True).data

    DT_RowId = serializers.SerializerMethodField()
    DT_RowAttr = serializers.SerializerMethodField()

    def get_DT_RowId(self, scenario):
        return 'row_%d' % scenario.pk

    def get_DT_RowAttr(self, scenario):
        return {'data-pk': scenario.pk}

    class Meta:
        model = Scenario
        fields = (
            'DT_RowId', 'DT_RowAttr',
            # 'user',
            'id',


            'scenario_title',
            'project',  # debug - trying to figure out where Cannon resolve keywork project into fields
            'embedded_scenario',

            # 'areal_features',

            # new version of ScenarioArealFeature(s)
            'a_features',

            # 'nonconventional_structures',
            # 'conventional_structures',

            'c_structures',
            'nc_structures',

            'cost_item_user_costs',
            'cost_item_user_assumptions',
            # 'structure_cost_item_costs',

            'create_date',
            'modified_date',
        )
        read_only_fields = [f.name for f in Scenario._meta.get_fields()]
