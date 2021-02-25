from rest_framework import serializers

import scenario.views

from .models import Project, Scenario, Structures, \
    CostItem, \
    CostItemDefaultCosts, \
    CostItemUserCosts, \
    CostItemDefaultEquations, \
    CostItemDefaultFactors, \
    CostItemUserAssumptions
from djmoney.contrib.django_rest_framework import MoneyField
# from django.contrib.auth.models import User
# from django.conf import settings
# try:
#     from django.contrib.auth import get_user_model
#     User = settings.AUTH_USER_MODEL
# except ImportError:
#     from django.contrib.auth.models import User

from authtools.models import User

from profiles.models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):

    profile = ProfileSerializer()

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
            'profile',
            'date_joined',
            'last_login',
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
        return Scenario.objects.filter(project__id=obj.id).count()

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
            'priority_watershed',
            'scenario_count',
            # 'create_date',
            # 'modified_date',
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
            'user': { 'email': value.user.email },
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




"""

"""
class EmbeddedArealFeatures(serializers.Field):
    def to_representation(self, value):
        ret = {
                "stormwater_management_feature": {
                    "label": 'Stormwater Management Feature',
                    "checkbox": value.stormwater_management_feature_checkbox,
                    "area": value.stormwater_management_feature_area
                },
                "amenity_plaza": {
                    "label": 'Amenity Plaza',
                    "checkbox": value.amenity_plaza_checkbox,
                    "area": value.amenity_plaza_area
                },
                "protective_yard": {
                    "label": 'Protective Yard',
                    "checkbox": value.protective_yard_checkbox,
                    "area": value.protective_yard_area
                },
                "parking_island": {
                    "label": 'Parking Island',
                    "checkbox": value.parking_island_checkbox,
                    "area": value.parking_island_area
                },
                "building": {
                    "label": 'Building',
                    "checkbox": value.building_checkbox,
                    "area": value.building_area
                },
                "drive_thru_facility": {
                    "label": 'Drive-Thru Facility',
                    "checkbox": value.drive_thru_facility_checkbox,
                    "area": value.drive_thru_facility_area
                },
                "landscape": {
                    "label": 'Miscellaneous Landscaping/Open Space',
                    "checkbox": value.landscape_checkbox,
                    "area": value.landscape_area
                },
                "sidewalk": {
                    "label": 'Sidewalk',
                    "checkbox": value.sidewalk_checkbox,
                    "area": value.sidewalk_area
                },
                "street": {
                    "label": 'Street',
                    "checkbox": value.street_checkbox,
                    "area": value.street_area
                },
                "median": {
                    "label": 'Median',
                    "checkbox": value.median_checkbox,
                    "area": value.median_area
                },
                "parking_lot": {
                    "label": 'Parking Lot',
                    "checkbox": value.parking_lot_checkbox,
                    "area": value.parking_lot_area
                },
                "driveway_and_alley": {
                    "label": 'Driveway and Alley',
                    "checkbox": value.driveway_and_alley_checkbox,
                    "area": value.driveway_and_alley_area
                }
            }
        return ret

    def to_internal_value(self, data):
        ret = {
            'project_title': data['project_title'],
            'scenario_title': data['scenario_title'],
            'land_unit_cost': data['land_unit_cost'],
            'project_type': data['project_type'],
            'project_ownership': data['project_ownership'],
            'project_area': data['project_area']
        }
        return ret

"""

"""
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
        read_only_fields = [f.name for f in Structures._meta.get_fields()]
"""

"""
class EmbeddedConventionalStructures(serializers.Field):
    def to_representation(self, value):
        ret = {
                "stormwater_wetland": {
                    "checkbox": value.stormwater_wetland_checkbox,
                    "area": value.stormwater_wetland_area
                },
                "pond": {
                    "checkbox": value.pond_checkbox,
                    "area": value.pond_area
                },
                "rooftop": {
                    "checkbox": value.rooftop_checkbox,
                    "area": value.rooftop_area
                },
                "concrete": {
                    "checkbox": value.concrete_checkbox,
                    "area": value.concrete_area
                },
                "asphalt": {
                    "checkbox": value.asphalt_checkbox,
                    "area": value.asphalt_area
                },
                "lawn": {
                    "checkbox": value.lawn_checkbox,
                    "area": value.lawn_area
                },
                "landscaping": {
                    "checkbox": value.landscaping_checkbox,
                    "area": value.landscaping_area
                },
                "trench": {
                    "checkbox": value.trench_checkbox,
                    "area": value.trench_area
                },
                "curb_and_gutter": {
                    "checkbox": value.curb_and_gutter_checkbox,
                    "area": value.curb_and_gutter_area
                },
        }
        return ret

    def to_internal_value(self, data):
        ret = {
            'project_title': data['project_title'],
            'scenario_title': data['scenario_title'],
            'land_unit_cost': data['land_unit_cost'],
            'project_type': data['project_type'],
            'project_ownership': data['project_ownership'],
            'project_area': data['project_area']
        }
        return ret

"""

"""
class EmbeddedNonConventionalStructures(serializers.Field):
    def to_representation(self, value):
        ret = {
                "swale": {
                    "checkbox": value.swale_checkbox,
                    "area": value.swale_area
                },

            "rain_harvesting_device": {
                "checkbox": value.rain_harvesting_device_checkbox,
                "area": value.rain_harvesting_device_area
            },
            "bioretention_cell": {
                "checkbox": value.bioretention_cell_checkbox,
                "area": value.bioretention_cell_area
            },
            "filter_strip": {
                "checkbox": value.filter_strip_checkbox,
                "area": value.filter_strip_area
            },
            "green_roof": {
                "checkbox": value.green_roof_checkbox,
                "area": value.green_roof_area
            },
            "planter_box": {
                "checkbox": value.planter_box_checkbox,
                "area": value.planter_box_area
            },
            "porous_pavement": {
                "checkbox": value.porous_pavement_checkbox,
                "area": value.porous_pavement_area
            },
        }
        return ret

    def to_internal_value(self, data):
        ret = {
            'project_title': data['project_title'],
            'scenario_title': data['scenario_title'],
            'land_unit_cost': data['land_unit_cost'],
            'project_type': data['project_type'],
            'project_ownership': data['project_ownership'],
            'project_area': data['project_area']
        }
        return ret

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
        read_only_fields = [f.name for f in CostItem._meta.get_fields()]

"""

    default values
    /api/costitemdefaultcosts

"""
class CostItemDefaultCostSerializer(serializers.ModelSerializer):

    # each default cost is applied to a single costitem
    costitem = CostItemSerializer(many=False, read_only=True)

    class Meta:
        model = CostItemDefaultCosts
        fields = (
            'costitem',
            'id',
            'replacement_life',
            'o_and_m_pct',
            'rsmeans_va',
            'db_25pct_va',
            'db_50pct_va',
            'db_75pct_va',
        )
        read_only_fields = [f.name for f in CostItemDefaultCosts._meta.get_fields()]


"""

"""
class CostItemDefaultEquationsSerializer(serializers.ModelSerializer):

    """
        the logic of the many=False is that in this case,
        there is one structure and one costitem for each 'CostItemDefaultAssumptions'

    """
    # structure = StructureSerializer(many=False, read_only=True)
    costitem = CostItemSerializer(many=False, read_only=True)

    class Meta:
        model = CostItemDefaultEquations
        fields = (
            'costitem',
            'id',
            'a_area',
            'z_depth',
            'd_density',
            'n_number',
            'equation_tx',
            'help_text',
        )
        read_only_fields = [f.name for f in CostItemDefaultEquations._meta.get_fields()]


class CostItemDefaultFactorsSerializer(serializers.ModelSerializer):

    """
        the logic of the many=False is that in this case,
        there is one structure and one costitem for each 'CostItemDefaultAssumptions'

    """
    structure = StructureSerializer(many=False, read_only=True)
    costitem = CostItemSerializer(many=False, read_only=True)

    class Meta:
        model = CostItemDefaultFactors
        fields = (
            'structure',
            'costitem',
            'id',
            'a_area',
            'z_depth',
            'd_density',
            'n_number',
        )
        read_only_fields = [f.name for f in CostItemDefaultFactors._meta.get_fields()]
# example
# {
#     "scenario_id": "1",
#     "project_title": "test 13333",
#     "scenario_title": "conventional #1",
#     "structure": {
#         "id": 1,
#         "code": "swale",
#         "name": "Swales",
#         "classification": "nonconventional",
#         "classification_display": "Non-Conventional",
#         "sort_nu": 1,
#         "units": "ft2",
#         "units_html": "ft2",
#         "help_text": "This is help text for the nonconventional structure Swales"
#     },
#     "costitem": {
#         "sort_nu": 1,
#         "code": "clearing",
#         "name": "Clearing and Grubbing",
#         "units": "Ac",
#         "help_text": "Clearing and Grubbing: includes all costs associated with preparation and mobilization of equipment. "
#     },
#     "checked": true,
#     "conversion_factor": "NOT FOUND for element clearing",
#     "factor_assumption_tx": "",
#     "sizing_factor_k": "",
#     "sizing_factor_n": "",
#     "construction_cost_factor_equation": ""
# },
class CostItemUserAssumptionsSerializer(serializers.ModelSerializer):
    # scenario = ScenarioSerializer(many=False, read_only=True)
    # structure = StructureSerializer(many=False, read_only=True)
    # costitem = CostItemSerializer(many=False, read_only=True)

    scenario_id = serializers.CharField(read_only=True, source="scenario.id")
    project_title = serializers.CharField(read_only=True, source="scenario.project.project_title")
    scenario_title = serializers.CharField(read_only=True, source="scenario.scenario_title")

    structure_code = serializers.CharField(read_only=True, source="structure.code")
    # structure_name = serializers.CharField(read_only=True, source="structure.name")
    # structure_units = serializers.CharField(read_only=True, source="structure.units")
    # structure_classification = serializers.CharField(read_only=True, source="structure.classification")

    # structure = StructureSerializer(many=False, read_only=True)
    # costitem = CostItemSerializer(many=False, read_only=True)

    costitem_code = serializers.CharField(read_only=True, source="costitem.code")
    # costitem_name = serializers.CharField(read_only=True, source="costitem.name")
    # costitem_units = serializers.CharField(read_only=True, source="costitem.units")

    class Meta:
        model = CostItemUserAssumptions
        fields = (
            'scenario_id',
            'project_title',
            'scenario_title',
            # 'structure',
            'structure_code',
            # 'structure_name',
            # 'structure_units',
            # 'structure_classification',
            # 'costitem',
            'costitem_code',
            # 'costitem_name',
            # 'costitem_units',

            'checked',
            # 'conversion_factor',
            'factor_assumption_tx',
            'sizing_factor_k',
            'sizing_factor_n',

            # 'construction_cost_factor_equation',
        )
        read_only_fields = [f.name for f in CostItemUserAssumptions._meta.get_fields()]
"""
    this is returned into results in /projects/{pk}/scenario to just 
    list all the scenarios is first loaded
    it is used to populate the table on the Scenarios page
    
    Example:
http://127.0.0.1:92/api/projects/1/scenarios/

"""
#

#
class ScenarioListSerializer(serializers.ModelSerializer):

    # user = UserSerializer()

    # project = EmbeddedProjectFields()
    #
    # embedded_scenario = EmbeddedScenarioFields(source='*')

    project_title = serializers.SerializerMethodField()
    def get_project_title(self, scenario):
        return '%s' % scenario.project.project_title

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

# used for Audit page

#
class ScenarioAuditSerializer(serializers.ModelSerializer):

    # user = UserSerializer()

    # project = EmbeddedProjectFields()
    #
    # embedded_scenario = EmbeddedScenarioFields(source='*')
    user = UserSerializer(many=False, read_only=True)
    project = ProjectSerializer()

    create_date = serializers.DateTimeField(format="%Y-%m-%d %I:%M %p %Z")
    modified_date = serializers.DateTimeField(format="%Y-%m-%d %I:%M %p %Z")

    # nutrient_req_met = serializers.SerializerMethodField()
    # captures_90pct_storm = serializers.SerializerMethodField()
    # meets_peakflow_req = serializers.SerializerMethodField()

    # def get_nutrient_req_met(self, obj):
    #     return obj.get_nutrient_req_met_display()
    # def get_captures_90pct_storm(self, obj):
    #     return obj.get_captures_90pct_storm_display()
    # def get_meets_peakflow_req(self, obj):
    #     return obj.get_meets_peakflow_req_display()

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

            'id',
            'user',
            'project',
            # 'project_title',

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


"""

    scenario - users values

"""
class CostItemUserCostSerializer(serializers.ModelSerializer):

    # each default cost is applied to a single costitem
    # scenario_id = serializers.CharField(read_only=True, source="scenario.id")
    #
    costitem_code = serializers.CharField(read_only=True, source="costitem.code")
    costitem_name = serializers.CharField(read_only=True, source="costitem.name")
    # each default cost is applied to a single costitem
    # project = ProjectSerializer(source='scenario')
    scenario = ScenarioListSerializer(many=False, read_only=True)
    project = ProjectSerializer(source='scenario.project',many=False, read_only=True)

    # costitem = CostItemSerializer(many=False, read_only=True)

    # # NOTE: the underlying model has to have a field marked with matching related_name. (I have no idea why)
    # # i.e. related_name="cost_item_user_costs"
    # cost_item_user_costs = serializers.SerializerMethodField()
    #
    # def get_cost_item_user_costs(self, instance):
    #     user_cost_items = instance.cost_item_user_costs.all().order_by('costitem__sort_nu')
    #     return CostItemUserCostSerializer(user_cost_items, many=True).data
    # user = serializers.SerializerMethodField()
    #
    # def get_user(self, obj):
    #     user1 = obj.scenario.project.user
    #     return UserSerializer(user1, many=False).data

    scenario_id = serializers.SerializerMethodField()
    def get_scenario_id(self, obj):
        return obj.scenario.id

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

    class Meta:
        model = CostItemUserCosts
        fields = (
            'id',
            # 'user',
            'scenario',
            'project',
            'scenario_id',
            'costitem',
            'costitem_code',
            'costitem_name',
            'units',
            'cost_source',
            'user_input_cost',
            'base_year',
            'replacement_life',
            'o_and_m_pct'
        )
        read_only_fields = [f.name for f in CostItemUserCosts._meta.get_fields()]

    # def to_representation(self, data):
    #     res = super(CostItemUserCostSerializer, self).to_representation(data)
    #     return {res['costitem_code']: res}




"""

    this contains all the data for the scenario

    /api/scenarios/1/

 this is returned into results in /scenario/{pk}/update is first loaded


"""

class ScenarioSerializer(serializers.ModelSerializer):

    # user = UserSerializer()

    project = EmbeddedProjectFields()

    embedded_scenario = EmbeddedScenarioFields(source='*')

    areal_features = EmbeddedArealFeatures()
    conventional_structures = EmbeddedConventionalStructures()
    nonconventional_structures = EmbeddedNonConventionalStructures()

    # add in other related models that have 1-to-many relationships
    # this works, but only shows the string representation of the user costs
    # cost_item_user_costs = serializers.StringRelatedField(many=True)

    # this just shows the primary key in the target
    # cost_item_user_costs = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    # NOTE: the underlying model has to have a field marked with matching related_name. (I have no idea why)
    # i.e. related_name="cost_item_user_costs"
    cost_item_user_costs = serializers.SerializerMethodField()

    def get_cost_item_user_costs(self, instance):
        user_cost_items = instance.cost_item_user_costs.all().order_by('costitem__sort_nu')
        return CostItemUserCostSerializer(user_cost_items, many=True).data

    # cost_item_user_costs = CostItemUserCostSerializer(read_only=True, many=True)

    # cost_item_user_assumptions = CostItemUserAssumptionsSerializer(read_only=True, many=True)
    #
    # structure_cost_item_costs = serializers.SerializerMethodField()
    #
    # """
    #     this duplicates code in the function views.structure_cost_item_json
    #     ZIP
    # """
    # def get_structure_cost_item_costs(self, instance):
    #
    #     #TODO
    #     structure = Structures.objects.get(code='pond')
    #
    #     cost_item_default_costs = CostItemDefaultCosts.objects.all()
    #
    #     cost_item_default_assumptions = CostItemDefaultAssumptions.objects.filter(structure=structure)
    #
    #     cost_item_user_costs = CostItemUserCosts.objects.filter(scenario=instance)
    #
    #     cost_item_user_assumptions = CostItemUserAssumptions.objects.filter(scenario=instance, structure=structure)
    #
    #
    #     json_data = scenario.views.structure_cost_item_json(structure,
    #                                                   instance,
    #                                                   cost_item_default_costs,
    #                                                   cost_item_default_assumptions,
    #                                                   cost_item_user_costs,
    #                                                   cost_item_user_assumptions,
    #                                                   )
    #
    #     #end TODO
    #
    #
    #     user_cost_items = instance.cost_item_user_costs.all().order_by('costitem__sort_nu')
    #
    #     return CostItemUserCostSerializer(user_cost_items, many=True).data


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
            'cost_item_user_assumptions',
            'scenario_title',
            'project',
            'embedded_scenario',

            'areal_features',
            'nonconventional_structures',
            'conventional_structures',


            'cost_item_user_costs',

            # 'structure_cost_item_costs',

            'create_date',
            'modified_date',
        )
        read_only_fields = [f.name for f in Scenario._meta.get_fields()]
