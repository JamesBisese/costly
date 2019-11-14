from decimal import Decimal

from django.db import models

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django import forms
from django.contrib.auth import get_user_model
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from .scenario_frameworks import TEMPLATE_SCENARIO, DEFAULT_SCENARIO

User = get_user_model()

"""
    convert units between Structure Units and Cost Item units
    i.e. ft2 and square yards, ft2 and AC

"""
def get_unit_conversion(structure_units, cost_item_units):

    conversion_factor = '1'
    structure_units = structure_units.upper()
    cost_item_units = cost_item_units.upper()

    if structure_units == cost_item_units:
        conversion_factor = 1
    elif structure_units == 'SF':
        if cost_item_units == 'AC':
            conversion_factor = '1/43560'
        elif cost_item_units == 'SY':
            conversion_factor = '1/9'
        # TN works because the density factor is in TN/CY
        elif cost_item_units in ['CY', 'TN']:
            conversion_factor = '1/27'
    elif structure_units == 'CF':
        if cost_item_units == 'AC':
            conversion_factor = '1/43560'
        elif cost_item_units == 'SY':
            conversion_factor = '1/9'
        elif cost_item_units == 'CY':
            conversion_factor = '1/27'
    elif structure_units == 'SY':
        if cost_item_units == 'AC':
            conversion_factor = '1/43560'
        elif cost_item_units == 'SY':
            conversion_factor = '1/9'
        elif cost_item_units == 'CY':
            conversion_factor = '1/27'
    elif structure_units == 'LF':
        if cost_item_units == 'AC':
            conversion_factor = '1/43560'
        elif cost_item_units == 'SY':
            conversion_factor = '1/9'
        elif cost_item_units == 'CY':
            conversion_factor = '1/27'


    return conversion_factor

'''
    this starts with all the 1-1 and 1-many models that are included in the scenario
'''

'''

    this is a set of tuples - each tuple has a checkbox and an area
    TODO: label the fields as necessary.
    
'''
class ArealFeatures(models.Model):

    stormwater_management_feature_area = models.IntegerField("Stormwater Management Feature Area", default=0,
                                                             blank=True, null=True)
    stormwater_management_feature_checkbox = models.BooleanField("Stormwater Management Feature Checked", default=False,
                                                             blank=True, null=True)
    amenity_plaza_area = models.IntegerField("Amenity Areas/Urban Plaza Area", default=0,
                                                             blank=True, null=True)
    amenity_plaza_checkbox = models.BooleanField("Amenity Areas/Urban Plaza Checked", default=False,
                                                             blank=True, null=True)
    protective_yard_area = models.IntegerField("Protective Yards Area", default=0,
                                                             blank=True, null=True)
    protective_yard_checkbox = models.BooleanField("Protective Yards Checked", default=False,
                                                             blank=True, null=True)

    parking_island_checkbox = models.BooleanField(" Checked", default=False,blank=True, null=True)
    parking_island_area = models.IntegerField(" Area", default=0,blank=True, null=True)
    building_checkbox = models.BooleanField(" Checked", default=False,blank=True, null=True)
    building_area = models.IntegerField(" Area", default=0,blank=True, null=True)
    drive_thru_facility_checkbox = models.BooleanField(" Checked", default=False,blank=True, null=True)
    drive_thru_facility_area = models.IntegerField(" Area", default=0,blank=True, null=True)
    landscape_checkbox = models.BooleanField(" Checked", default=False,blank=True, null=True)
    landscape_area = models.IntegerField(" Area", default=0,blank=True, null=True)
    sidewalk_checkbox = models.BooleanField(" Checked", default=False,blank=True, null=True)
    sidewalk_area = models.IntegerField(" Area", default=0,blank=True, null=True)
    street_checkbox = models.BooleanField(" Checked", default=False,blank=True, null=True)
    street_area = models.IntegerField(" Area", default=0,blank=True, null=True)
    median_checkbox = models.BooleanField(" Checked", default=False,blank=True, null=True)
    median_area = models.IntegerField(" Area", default=0,blank=True, null=True)
    parking_lot_checkbox = models.BooleanField(" Checked", default=False,blank=True, null=True)
    parking_lot_area = models.IntegerField(" Area", default=0,blank=True, null=True)
    driveway_and_alley_checkbox = models.BooleanField(" Checked", default=False,blank=True, null=True)
    driveway_and_alley_area = models.IntegerField(" Area", default=0,blank=True, null=True)


'''

    this is a look-up table of Structures. Meta data table

'''
class Structures(models.Model):

    CLASSIFICATION_VALUES = ('conventional', 'nonconventional')
    CLASSIFICATION_TEXTS = ('Conventional', 'Non-Conventional')
    CLASSIFICATION_CHOICES = zip(CLASSIFICATION_VALUES, CLASSIFICATION_TEXTS)

    code = models.CharField(unique=True, max_length=100, default=None, blank=False, null=False)
    name = models.CharField(unique=True, max_length=100, default=None, blank=False, null=False)
    classification = models.CharField(unique=False, choices=CLASSIFICATION_CHOICES, max_length=15, default=None, blank=False, null=False)
    sort_nu = models.PositiveIntegerField("Sort Number", default=0, blank=True, null=True)
    units = models.CharField(unique=False, max_length=12, default=None, blank=False, null=False)
    units_html = models.CharField(unique=False, max_length=25, default=None, blank=False, null=False)
    help_text = models.CharField(unique=False, max_length=1000, default="TBD", blank=False, null=False)

    def __str__(self):
        return self.classification + ' - ' + self.name

    class Meta:
        verbose_name_plural = "Structures"
        ordering = ['sort_nu', ]
'''

    this is a data table of ConventionalStructures

'''
class ConventionalStructures(models.Model):
    stormwater_wetland_checkbox = models.BooleanField("Stormwater Wetland Checked", default=False, blank=True, null=True)
    stormwater_wetland_area = models.IntegerField("Stormwater Wetland Area", default=0, blank=True, null=True)
    stormwater_wetland_first_year_costs = MoneyField("1st year maintenance costs", \
        decimal_places=2, max_digits=11, default=0, default_currency='USD', blank=True, null=True)

    pond_checkbox = models.BooleanField(default=False, blank=True, null=True)
    pond_area = models.IntegerField(default=0, blank=True, null=True)
    rooftop_checkbox = models.BooleanField(default=False, blank=True, null=True)
    rooftop_area = models.IntegerField(default=0, blank=True, null=True)
    lawn_checkbox = models.BooleanField(default=False, blank=True, null=True)
    lawn_area = models.IntegerField(default=0, blank=True, null=True)
    landscaping_checkbox = models.BooleanField(default=False, blank=True, null=True)
    landscaping_area = models.IntegerField(default=0, blank=True, null=True)
    trench_checkbox = models.BooleanField(default=False, blank=True, null=True)
    trench_area = models.IntegerField(default=0, blank=True, null=True)
    concrete_checkbox = models.BooleanField(default=False, blank=True, null=True)
    concrete_area = models.IntegerField(default=0, blank=True, null=True)
    asphalt_checkbox = models.BooleanField(default=False, blank=True, null=True)
    asphalt_area = models.IntegerField(default=0, blank=True, null=True)
    curb_and_gutter_checkbox = models.BooleanField(default=False, blank=True, null=True)
    curb_and_gutter_area = models.IntegerField(default=0, blank=True, null=True)

'''

    this is a OneToOne data table of senario.NonConventionalStructures

'''
class NonConventionalStructures(models.Model):
    swale_area = models.IntegerField("Swale Area", default=0, blank=True, null=True)
    swale_checkbox = models.BooleanField("Swale Checked", default=False, blank=True, null=True)
    rain_harvesting_device_checkbox = models.BooleanField(default=False, blank=True, null=True)
    rain_harvesting_device_area = models.IntegerField(default=0, blank=True, null=True)
    bioretention_cell_checkbox = models.BooleanField(default=False, blank=True, null=True)
    bioretention_cell_area = models.IntegerField(default=0, blank=True, null=True)
    filter_strip_checkbox = models.BooleanField(default=False, blank=True, null=True)
    filter_strip_area = models.IntegerField(default=0, blank=True, null=True)
    green_roof_checkbox = models.BooleanField(default=False, blank=True, null=True)
    green_roof_area = models.IntegerField(default=0, blank=True, null=True)
    planter_box_checkbox = models.BooleanField(default=False, blank=True, null=True)
    planter_box_area = models.IntegerField(default=0, blank=True, null=True)
    porous_pavement_checkbox = models.BooleanField(default=False, blank=True, null=True)
    porous_pavement_area = models.IntegerField(default=0, blank=True, null=True)


'''

    this is Meta Data table for Cost Items - 

'''
class CostItem(models.Model):
    code = models.CharField(unique=True, max_length=50, default=None, blank=False, null=False)
    name = models.CharField(unique=True, max_length=50, default=None, blank=False, null=False)
    sort_nu = models.PositiveIntegerField("Sort Number", default=0, blank=True, null=True)
    units = models.CharField(unique=False, max_length=12, default=None, blank=False, null=False)
    help_text = models.CharField(unique=False, max_length=1000, default="TBD", blank=False, null=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['sort_nu', ]
#
# this stores the 'default' values for the costitem costs.
# each row is attached to one CostItem for one Scenario
#
#
#
'''

    this is a look-up table of the 'default' costs associated with each Cost Items
    
    the 'user' costs are stored in CostItemUserCosts which is defined after Scenario model
    
'''
class CostItemDefaultCosts(models.Model):

    costitem = models.OneToOneField(CostItem, on_delete=models.CASCADE, default=None, blank=False, null=False)

    #TODO: this is 'Engineering Estimate' and should be named 'eng_estimate' or similar
    rsmeans_va = MoneyField('RSMeans unit cost', decimal_places=2, max_digits=11,
                                default_currency='USD', blank=True, null=True)
    db_25pct_va = MoneyField('DB 25-percentile unit cost', decimal_places=2, max_digits=11,
                                default_currency='USD', blank=True, null=True)
    db_50pct_va = MoneyField('DB Average unit cost', decimal_places=2, max_digits=11,
                                default_currency='USD',
                                blank=True, null=True)
    db_75pct_va = MoneyField('DB 75-percentile unit cost', decimal_places=2, max_digits=11,
                                default_currency='USD', blank=True, null=True)

    # TODO these 2 might be in the wrong model!!!
    replacement_life = models.PositiveIntegerField(default=40,
                                           validators=[MinValueValidator(0),
                                                       MaxValueValidator(100)
                                                       ],
                                           blank=True, null=True)
    o_and_m_pct = models.PositiveIntegerField(default=0,
                                              validators=[MinValueValidator(0),
                                                          MaxValueValidator(100)
                                                          ],
                                              blank=False, null=False)

    # added 2019-08-13 to help manage unit costs for all structures
    equation = models.CharField("Construction Costs Equation ", max_length=150, default=None, blank=True, null=True)

    def __str__(self):
        return self.costitem.code + " -- default costs"

    class Meta:
        verbose_name_plural = "Cost Item Default Costs"
        ordering = ['costitem__sort_nu', ]
'''

    this is a look-up table of the 'default' costs assumptions with each Cost Items
    each one is connected to a specific structure

    the 'user' cost assumptions are stored in CostItemUserAssumptions which is defined after Scenario model

'''


class CostItemDefaultFactors(models.Model):
    structure = models.ForeignKey(Structures, on_delete=models.DO_NOTHING, default=None, blank=False, null=False)
    costitem = models.ForeignKey(CostItem, on_delete=models.DO_NOTHING, default=None, blank=False, null=False)

    a_area = models.CharField("Area (a)", max_length=10, default=None, blank=True, null=True)
    z_depth = models.CharField("Depth (z)", max_length=10, default=None, blank=True, null=True)
    d_density = models.CharField("Density (d)", max_length=10, default=None, blank=True, null=True)
    n_number = models.CharField("Count (n)", max_length=10, default=None, blank=True, null=True)

    def __str__(self):
        return self.structure.code + " -- " + self.costitem.code

    class Meta:
        verbose_name_plural = "Structure Cost Item Default Factors"
        unique_together = (('structure', "costitem"))
        ordering = ['costitem__sort_nu', ]

'''
    2019-08-15 Cost Item Default Equations
    
    this is a look-up table of the 'default' costs equations and factors for each Cost Items
    AND NOT connected to a specific structure

    Loaded from CSV file CostItemDefaultEquations
'''


class CostItemDefaultEquations(models.Model):
    costitem = models.OneToOneField(CostItem, unique=True, on_delete=models.DO_NOTHING, default=None, blank=False, null=False)

    equation_tx = models.CharField("Equation", max_length=150, default=None, blank=True, null=True)
    a_area = models.CharField("Area (a)", max_length=10, default=None, blank=True, null=True)
    z_depth = models.CharField("Depth (z)", max_length=10, default=None, blank=True, null=True)
    d_density = models.CharField("Density (d)", max_length=10, default=None, blank=True, null=True)
    r_ratio = models.CharField("Ratio (r)", max_length=10, default=None, blank=True, null=True)
    n_number = models.CharField("Count (n)", max_length=10, default=None, blank=True, null=True)
    help_text = models.CharField(unique=False, max_length=1000, default="Help Text", blank=False, null=False)

    def __str__(self):
        return self.costitem.code + " -- " + self.equation_tx

    class Meta:
        verbose_name_plural = "Cost Item Default Equations"
        ordering = ['costitem__sort_nu', ]

class Project(models.Model):
    OWNERSHIP_TYPE_VALUES = ('private', 'public')
    OWNERSHIP_TYPE_TEXTS = ('Private', 'Public')
    OWNERSHIP_TYPE_CHOICES = zip(OWNERSHIP_TYPE_VALUES, OWNERSHIP_TYPE_TEXTS)

    PROJECT_TYPE_VALUES = ('redevelopment',
                           'development',
                           'voluntary_redevelopment')
    PROJECT_TYPE_TEXTS = ('redevelopment project focused on additional new impervious area',
                          'whole site (new development)',
                          'BMP retrofit to existing development only (voluntary redevelopment)')
    PROJECT_TYPE_CHOICES = zip(PROJECT_TYPE_VALUES, PROJECT_TYPE_TEXTS)

    PURCHASE_TYPE_VALUES = ('to_be_purchased', 'owned')
    PURCHASE_TYPE_TEXTS = ('Site property needs to be purchased by developer', 'Site property is owned by developer')
    PURCHASE_TYPE_CHOICES = zip(PURCHASE_TYPE_VALUES, PURCHASE_TYPE_TEXTS)

    WATERSHED_VALUES = ('please_name', 'no')
    WATERSHED_TEXTS = ('Yes - please name', 'No')
    WATERSHED_CHOICES = zip(WATERSHED_VALUES, WATERSHED_TEXTS)

    NUTRIENT_REQ_VALUES = ('with_buy_down', 'without_buy_down', 'unknown')
    NUTRIENT_REQ_TEXTS = ('With Nutrient Buy Down', 'Without Nutrient Buy Down', 'Unknown')
    NUTRIENT_CHOICES = zip(NUTRIENT_REQ_VALUES, NUTRIENT_REQ_TEXTS)

    REGS_REQ_VALUES = ('yes', 'no', 'unknown')
    REGS_REQ_TEXTS = ('Yes', 'No', 'unknown')
    REGS_CHOICES = zip(REGS_REQ_VALUES, REGS_REQ_TEXTS)
    REGS_CHOICES2 = zip(REGS_REQ_VALUES, REGS_REQ_TEXTS)

    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, blank=False, null=False)

    project_title = models.CharField('Project Title', unique=False, max_length=200, default=None, blank=False,null=False)

    project_ownership = models.CharField('Project Organizer', choices=OWNERSHIP_TYPE_CHOICES, max_length=15, blank=True, null=True)
    project_location = models.CharField('Location of the project', max_length=150, default=None, blank=True, null=True)

    project_type = models.CharField('Project Type', choices=PROJECT_TYPE_CHOICES, max_length=25, blank=True, null=True)
    project_purchase_information = models.CharField('Purchase Information', choices=PURCHASE_TYPE_CHOICES,
                                                    max_length=15, default=None, blank=True, null=True)
    priority_watershed = models.CharField('Priority Watershed', choices=WATERSHED_CHOICES, max_length=15, default=None, blank=True, null=True)

    project_area = models.CharField('Total Project Area (square feet)', max_length=15,  default=None, blank=False, null=False)
    land_unit_cost = MoneyField('Cost per ft2 of Project site',
                                decimal_places=2, max_digits=11, default=1,
                                default_currency='USD', blank=False, null=False)


    def __str__(self):
        return self.project_title

    class Meta:
        verbose_name_plural = "Projects"
        unique_together = (("user", "project_title"))

"""
    TODO: replace this with building the JSON object using model content

"""
def get_TEMPLATE_SCENARIO():

    raw_ts = TEMPLATE_SCENARIO
    structures = Structures.objects.all().order_by('sort_nu').values()
    fields = []
    labels = {}
    inputs = {}

    for structure in structures:
        if structure['classification'] == 'conventional':
            fields.append(structure['code'])
            labels[structure['code']] = structure['name']
            inputs[structure['code']] = ['checkbox', 'area']
    raw_ts['siteData']['conventional_structures']['fields'] = fields
    raw_ts['siteData']['conventional_structures']['labels'] = labels
    raw_ts['siteData']['conventional_structures']['inputs'] = inputs
    fields = []
    labels = {}
    inputs = {}
    for structure in structures:
        if structure['classification'] == 'nonconventional':
            fields.append(structure['code'])
            labels[structure['code']] = structure['name']
            inputs[structure['code']] = ['checkbox', 'area']

    raw_ts['siteData']['nonconventional_structures']['fields'] = fields
    raw_ts['siteData']['nonconventional_structures']['labels'] = labels
    raw_ts['siteData']['nonconventional_structures']['inputs'] = inputs

    cost_items = CostItem.objects.all().order_by('sort_nu').values()
    fields = []
    for cost_item in cost_items:
        fields.append(cost_item['code'])
    raw_ts['siteData']['cost_items']['fields'] = fields

    return raw_ts

class Scenario(models.Model):

    # this is a template used in Javascript to figure out how to manage the UI
    # it is stored in a module 'scenario_frameworks' just because it is big and ugly
    templateScenario = get_TEMPLATE_SCENARIO()

    # this is an object used as the default scenario when a user creates a new scenario
    # again, it is stored in a module 'scenario_frameworks' just because it is big and ugly
    defaultScenario = DEFAULT_SCENARIO

    NUTRIENT_REQ_VALUES = ('with_buy_down', 'without_buy_down', 'unknown')
    NUTRIENT_REQ_TEXTS = ('With Nutrient Buy Down', 'Without Nutrient Buy Down', 'Unknown')
    NUTRIENT_CHOICES = zip(NUTRIENT_REQ_VALUES, NUTRIENT_REQ_TEXTS)

    REGS_REQ_VALUES = ('yes', 'no', 'unknown')
    REGS_REQ_TEXTS = ('Yes', 'No', 'unknown')
    REGS_CHOICES = zip(REGS_REQ_VALUES, REGS_REQ_TEXTS)
    REGS_CHOICES2 = zip(REGS_REQ_VALUES, REGS_REQ_TEXTS)

    project = models.ForeignKey(Project, on_delete=models.CASCADE, default=None, blank=False, null=False)

    # project_title = models.CharField('Project Name', unique=False, max_length=200, default=None, blank=True,null=True)
    scenario_title = models.CharField('Scenario Name', unique=False, max_length=200, default=None, blank=False, null=False)
    scenario_date = models.DateField('Scenario Date', auto_now_add=False, default=None, blank=True,null=True)

    pervious_area = models.IntegerField(default=0, blank=True, null=True)
    impervious_area = models.IntegerField(default=0, blank=True, null=True)

    nutrient_req_met = models.CharField('Level of nutrient requirements met', choices=NUTRIENT_CHOICES, max_length=25,  default='unknown', blank=True, null=True)
    captures_90pct_storm = models.CharField('Site captures the 90th percentile storm volume', choices=REGS_CHOICES, max_length=25,  default='unknown', blank=True, null=True)
    meets_peakflow_req = models.CharField('Site meets peak flow requirements', choices=REGS_CHOICES2, max_length=25,  default='unknown', blank=True, null=True)

    # cost elements
    planning_and_design_factor = models.CharField("Planning and Design Factor (Multiplier)", max_length=12, default='', blank=True, null=True)
    study_life = models.IntegerField("Study Life(years)", default=0, blank=True, null=True)
    discount_rate =models.FloatField("Discount Rate(DISC)", default=0, blank=True, null=True)

    areal_features = models.OneToOneField(
        ArealFeatures,
        on_delete=models.CASCADE,
        primary_key=False,
        default=None,
        blank=True,
        null=True
    )
    conventional_structures = models.OneToOneField(
        ConventionalStructures,
        on_delete=models.CASCADE,
        primary_key=False,
        default=None,
        blank=True,
        null=True
    )
    nonconventional_structures = models.OneToOneField(
        NonConventionalStructures,
        on_delete=models.CASCADE,
        primary_key=False,
        default=None,
        blank=True,
        null=True
    )

    counter = models.IntegerField('Integer Counter', default=0, blank=False, null=False)

    create_date = models.DateTimeField('Create Date', auto_now_add=True)
    modified_date = models.DateTimeField('Modified Date', auto_now=True)

    def __str__(self):
        return self.project.project_title + " -- " + self.scenario_title

    class Meta:
        verbose_name_plural = "Scenarios"
        unique_together = (("project", "scenario_title"))

    """
    
        process all the scenario related data (structures, costs, assumptions, etc.)
    
    """
    def process_related_data(self, form_data):

        scenarioTemplate = Scenario.templateScenario['siteData']

        #TODO: need to change this to split out project and scenario fields
        list_of_attributes = scenarioTemplate['embedded_scenario']['fields']
        list_of_values = form_data['embedded_scenario']

        """
            removed edits of project from Cost Tool.  Now only editable in projects
        """
        # for field in list_of_attributes:
        #     if hasattr(self.project, field):
        #         val = list_of_values[field]
        #         # print("field='{}', value='{}'".format(field, val))
        #         setattr(self.project, field, list_of_values[field])

        for field in list_of_attributes:
            if hasattr(self, field):
                val = list_of_values[field]

                val = None if val == '' else val
                setattr(self, field, val)

        areal_features = self.areal_features

        if areal_features == None:
            areal_features = ArealFeatures()

        list_of_attributes = scenarioTemplate['areal_features']['inputs']
        list_of_values = form_data['areal_features']
        for feature_name in list_of_attributes:
            for field in list_of_attributes[feature_name]:
                if hasattr(areal_features, feature_name + '_' + field):
                    field_value = list_of_values[feature_name][field]
                    if field == 'area' and field_value == '':
                        field_value = None
                    # print(feature_name + '_' + field + ": " + str(field_value))
                    setattr(areal_features, feature_name + '_' + field, field_value)

        areal_features.save()
        self.areal_features_id = areal_features.id

        ''' now structures '''
        conventional_structures = self.conventional_structures

        if conventional_structures == None:
            conventional_structures = ConventionalStructures()

        list_of_attributes = scenarioTemplate['conventional_structures']['inputs']
        list_of_values = form_data['conventional_structures']
        for feature_name in list_of_attributes:
            for field in list_of_attributes[feature_name]:
                if hasattr(conventional_structures, feature_name + '_' + field):
                    field_value = list_of_values[feature_name][field]
                    if field == 'area' and field_value == '':
                        field_value = None
                    # print(feature_name + '_' + field + ": " + str(field_value))
                    setattr(conventional_structures, feature_name + '_' + field, field_value)

        try:
            conventional_structures.save()
        except Exception:
            test = {'Type': type(Exception).__name__,
                                 'message': "1. Unexpected error:" + Exception.args[0],
                                 }

        self.conventional_structures_id = conventional_structures.id

        nonconventional_structures = self.nonconventional_structures

        if nonconventional_structures == None:
            nonconventional_structures = NonConventionalStructures()

        list_of_attributes = scenarioTemplate['nonconventional_structures']['inputs']
        list_of_values = form_data['nonconventional_structures']
        for feature_name in list_of_attributes:
            for field in list_of_attributes[feature_name]:
                if hasattr(nonconventional_structures, feature_name + '_' + field):
                    field_value = list_of_values[feature_name][field]
                    if field == 'area' and field_value == '':
                        field_value = None
                    # print(feature_name + '_' + field + ": " + str(field_value))
                    setattr(nonconventional_structures, feature_name + '_' + field, field_value)

        nonconventional_structures.save()
        self.nonconventional_structures_id = nonconventional_structures.id

        """
            new code dealing with content on the 'Structure Cost Item User Assumptions' tab 
              - combination of Structure (single) and Cost Items
            
            form_data should have a single 'structure' - the structure selected
            by the user in the drop-down list

        """
        list_of_cost_items = []

        # if the user has not selected anything from the Structure Costs drop-down then there is none of this data
        structure_code = None
        if 'user_assumptions' in form_data['cost_items']:

            list_of_cost_items = scenarioTemplate['cost_items']['fields']

            structure_code = form_data['cost_items']['user_assumptions']['structure'];

            list_of_values = form_data['cost_items']['user_assumptions']['data'];

        # have to run through all the cost_items to delete any that are not found
        structure_obj = None
        for cost_item in list_of_cost_items:

            form_values = None

            cost_item_assumptions_obj = CostItemUserAssumptions.objects.filter(scenario__id=self.id,
                                                                               structure__code=structure_code,
                                                                                costitem__code=cost_item).first()

            # remove the values if they are all ''
            input_empty = False
            if cost_item in list_of_values:
                form_values = list_of_values[cost_item]
                # set empty string to null

                if form_values['a_area'] == '':
                    form_values['a_area'] = None
                if form_values['z_depth'] == '':
                    form_values['z_depth'] = None
                if form_values['d_density'] == '':
                    form_values['d_density'] = None
                # if form_values['r_ratio'] is '':
                #     form_values['r_ratio'] = None
                if form_values['n_number'] == '':
                    form_values['n_number'] = None

                if form_values['checked'] == False \
                    and form_values['a_area'] is None \
                        and form_values['z_depth'] is None \
                        and form_values['d_density'] is None \
                        and form_values['n_number'] is None:
                    input_empty = True

                # 2019-09-10 delete if they uncheck and discard any input
                if form_values['checked'] is False:
                    input_empty = True

            if cost_item_assumptions_obj is not None:
                if cost_item not in list_of_values or input_empty is True:
                    # print("delete structure: {} cost_item: {}".format(structure_code, cost_item))
                    cost_item_assumptions_obj.delete()

                    continue
                elif cost_item_assumptions_obj.checked != form_values['checked'] or \
                    cost_item_assumptions_obj.a_area != form_values['a_area'] or \
                        cost_item_assumptions_obj.z_depth != form_values['z_depth'] or \
                        cost_item_assumptions_obj.d_density != form_values['d_density'] or \
                        cost_item_assumptions_obj.n_number != form_values['n_number']:

                    # print("update structure: {} cost_item: {}".format(structure_code, cost_item))
                    cost_item_assumptions_obj.checked = form_values['checked']

                    cost_item_assumptions_obj.a_area = form_values['a_area']
                    cost_item_assumptions_obj.z_depth = form_values['z_depth']
                    cost_item_assumptions_obj.d_density = form_values['d_density']
                    cost_item_assumptions_obj.n_number = form_values['n_number']

                    cost_item_assumptions_obj.save()

                    '''
                        TODO: add calculation here
                    '''
                    form_values['construction_cost_factor_equation'] = '=mc2'
                    form_values['cost_V1'] = '$99.99'

                else:
                    pass

            elif form_values is not None and input_empty is False:
                if structure_obj is None:
                    structure_obj = Structures.objects.get(code=structure_code)

                cost_item_obj = CostItem.objects.get(code = cost_item)
                # print("create structure: {} cost_item: {}".format(structure_code, cost_item))
                c = CostItemUserAssumptions(
                    scenario = self,
                    structure = structure_obj,
                    costitem = cost_item_obj,

                    checked=form_values['checked'],

                    a_area = form_values['a_area'],
                    z_depth = form_values['z_depth'],
                    d_density = form_values['d_density'],
                    n_number = form_values['n_number'],
                )
                c.save()

                '''
                    TODO: add calculation here
                '''
                form_values['construction_cost_factor_equation'] = '=mc2'
                form_values['cost_V1'] = '$99.99'

        """
        
            this manages the section of Cost Item Unit Costs
            
        """
        cost_items = form_data['cost_items']['unit_costs']

        # cost_items = list_of_values['user_costs']
        for cost_item, form_costs in cost_items.items():

            list_of_attributes = ['cost_source', 'replacement_life', 'o_and_m_pct']

            if form_costs['replacement_life'] == 'None':
                form_costs['replacement_life'] = None

            # if len(form_costs['o_and_m_pct']) > 0:
            #     form_costs['o_and_m_pct'] = Decimal(form_costs['o_and_m_pct'])
            if form_costs['cost_source'] != 'user':
                form_costs['user_input_cost'] = None
                form_costs['base_year'] = None


            user_costs_obj = CostItemUserCosts.objects.filter(scenario__id=self.id,
                                                                   costitem__code=cost_item).first()

            default_costs_obj = CostItemDefaultCosts.objects.filter(costitem__code=cost_item).first()

            is_default = 1
            change_count = 0

            db_record_exists = False
            if user_costs_obj is not None:
                db_record_exists = True

            # process checking for user changing 'cost_source'
            cost_source = form_costs['cost_source']
            if cost_source == 'user':
                list_of_attributes.extend(['user_input_cost','base_year'])
                # if str(user_costs_obj.user_input_cost) != str(form_costs['user_input_cost']   )

            """
            Note: yes, this is terrible.  I can't tell if it is bad and complex, or 
            the system is really this complex
            
            --The rules are--
            if everything is blank, 
                if exists in db, delete
                else if not exist
                    continue
            else
                if exists in db
                    if changed 
                        update
                    else
                        continue
                else
                    create
            
            """
            for field in list_of_attributes:

                db_field_value = -1
                default_field_value = -1

                # submitted form value
                form_value = form_costs[field]

                # existing db user value
                if hasattr(user_costs_obj, field):
                    db_field_value = getattr(user_costs_obj, field, None)
                    # special test for Money fields to compare just the amount
                    if isinstance(db_field_value, Money):
                        db_field_value = str(db_field_value.amount)
                    elif field == 'cost_source':
                        if db_record_exists == True and form_value != 'rsmeans' and form_value != db_field_value:
                            is_default -= 1
                            change_count += 1
                            """
                                don't do any more processing on cost_source
                            """
                            continue
                elif field == 'cost_source':
                    continue

                # default value
                if cost_source != 'user' and hasattr(default_costs_obj, field):
                    default_field_value = getattr(default_costs_obj, field, None)
                elif cost_source == 'user' and field != 'cost_source':
                    if field == 'user_input_cost' or field == 'base_year':
                        default_field_value = -1
                    else:
                        default_field_value = getattr(default_costs_obj, field, None)


                if db_field_value != -1 and default_field_value != -1 \
                        and str(db_field_value) != str(default_field_value):
                    # store the data
                    is_default -= 1
                if db_field_value != -1 and str(db_field_value) != str(form_value):
                    # the user changed the value from what they set earlier
                    change_count += 1
                    if default_field_value != -1 and str(form_value) == str(default_field_value):
                        pass # is_default = True
                    else:
                        is_default -= 1

                if db_field_value == -1 and default_field_value != -1 \
                    and str(form_value) != str(default_field_value):
                    # the user changed the value from the default
                    is_default -= 1
                    change_count += 1
                elif db_field_value == -1 and default_field_value == -1 \
                    and str(form_value) != '':
                    # there is a value (this is for user_input_cost and base_year)
                    is_default -= 1
                    change_count += 1

                print_str = "cost_item: {}; field: {}; form_value: {}, " + \
                      "db_user_value: {}; default_value: {}; is_default: {}; change_count: {}"

                if change_count > 0 and True is False:
                    print(print_str.format(
                                            cost_item,
                                            field,
                                            form_value,
                                            db_field_value,
                                            default_field_value,
                                            is_default,
                                            change_count,
                                          )
                    )
                # if is_default != 1 and change_count > 0:
                #     break


            # dont store copies that are just the default
            if is_default == 1 and db_record_exists is True:
                # print("delete cost_item from db {}".format(cost_item))
                user_costs_obj.delete()



            if is_default != 1 and change_count > 0:
                if user_costs_obj != None:
                    # print("update cost_item {}".format(cost_item))
                    user_costs_obj.cost_source = form_costs['cost_source']
                    user_costs_obj.user_input_cost = form_costs['user_input_cost']
                    user_costs_obj.base_year = form_costs['base_year']
                    user_costs_obj.replacement_life = form_costs['replacement_life']
                    user_costs_obj.o_and_m_pct = form_costs['o_and_m_pct']

                    if user_costs_obj.cost_source != 'user':
                        user_costs_obj.user_input_cost = None
                        user_costs_obj.base_year = None

                    user_costs_obj.save()

                    string_template = "updated cost_item {}. cost_source:'{}',replacement_life:'{}',o_and_m_pct:'{}'"
                    # print(string_template.format(cost_item,
                    #                              user_costs_obj.cost_source,
                    #                              user_costs_obj.replacement_life,
                    #                              user_costs_obj.o_and_m_pct))
                else:
                    costitem = CostItem.objects.filter(code=cost_item).first()

                    # print("create cost_item {}".format(cost_item))
                    c = CostItemUserCosts(
                        scenario=self,
                        costitem = costitem,

                        cost_source = form_costs['cost_source'],
                        user_input_cost=form_costs['user_input_cost'],
                        base_year=form_costs['base_year'],
                        replacement_life=form_costs['replacement_life'],
                        o_and_m_pct=form_costs['o_and_m_pct'],
                    )
                    c.save()
                    string_template = "created cost_item {}. cost_source:'{}',replacement_life:'{}',o_and_m_pct:'{}'"
                    # print(string_template.format(cost_item,
                    #                              c.cost_source,
                    #                              c.replacement_life,
                    #                              c.o_and_m_pct))



        return

    """

        generate the cost from database content

    """

    def get_costs(self):

        # this is what serializers are supposed to do, but I don't understand how
        cost_items_dict = {}
        cost_items = CostItem.objects.all()
        for cost_item in cost_items:
            cost_items_dict[cost_item.code] = {'code': cost_item.code,
                                               'name': cost_item.name,
                                               'units': cost_item.units}

        cost_item_default_equations = CostItemDefaultEquations.objects.all()
        for obj in cost_item_default_equations:
            costitem_code = obj.costitem.code
            cost_items_dict[costitem_code]['equation'] = obj.equation_tx

        result = {}

        structures = Structures.objects.all().order_by('sort_nu')

        cost_item_default_costs = CostItemDefaultCosts.objects.all()

        cost_item_user_costs = CostItemUserCosts.objects.filter(scenario=self)

        # testing using RelatedManager .all()
        # cost_item_user_costs = self.cost_item_user_costs.all()

        # build up the costs dictionaries
        # first add in the cost_item_user_costs

        costs = {}

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

            if not costitem_code in costs:
                costs[costitem_code] = {'cost_source': cost_source,
                                        'unit_cost': unit_cost,
                                        'units': cost_items_dict[costitem_code]['units'],
                                        'replacement_life': cost_item_user_costs_obj.replacement_life,
                                        'o_and_m_pct': cost_item_user_costs_obj.o_and_m_pct,
                                       }
            else:
                if cost_source == 'user':
                    costs[costitem_code]['unit_cost'] = unit_cost
                    costs[costitem_code]['units'] = cost_items_dict[costitem_code]['units']

                costs[costitem_code]['cost_source'] = cost_source

        # then add in the default costs to update the non 'user' (cost_source) costs
        for cost_item_default_costs_obj in cost_item_default_costs:
            costitem_code = cost_item_default_costs_obj.costitem.code
            if costitem_code in costs:
                if costs[costitem_code]['cost_source'] != 'user':
                    cost_source = costs[costitem_code]['cost_source']
                    # the user selected or entered data in assumptions tab, but not in cost tab
                    if cost_source == 'TBD1':
                        costs[costitem_code]['cost_source'] = 'rsmeans'
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

                    costs[costitem_code]['unit_cost'] = unit_cost
                    costs[costitem_code]['units'] = cost_items_dict[costitem_code]['units']
            else:
                costs[costitem_code] = {'cost_source': 'rsmeans',
                                        'unit_cost': cost_item_default_costs_obj.rsmeans_va.amount,
                                        'units': cost_items_dict[costitem_code]['units'],
                                        'o_and_m_pct': cost_item_default_costs_obj.o_and_m_pct,
                                        'replacement_life': cost_item_default_costs_obj.replacement_life,
                                       }


        conventional_structures = self.conventional_structures
        nonconventional_structures = self.nonconventional_structures

        # prepare the cost item user assumptions - which are per structure per cost item
        cost_item_user_assumptions = self.cost_item_user_assumptions.all()

        user_assumptions = {}
        for user_assumption in cost_item_user_assumptions:
            if user_assumption.structure.code not in user_assumptions:
                user_assumptions[user_assumption.structure.code] = {}
            user_assumptions[user_assumption.structure.code][user_assumption.costitem.code] = user_assumption

        # if the user has not made any edits to the default user assumptions, you need to get the
        # assumptions from that model
        cost_item_default_assumptions = CostItemDefaultFactors.objects.all()
        for default_assumption in cost_item_default_assumptions:
            if default_assumption.structure.code not in user_assumptions:
                # the defaults are by definition checked
                default_assumption.checked = True
                user_assumptions[default_assumption.structure.code] = {}
                user_assumptions[default_assumption.structure.code][default_assumption.costitem.code] = default_assumption
            #added to try and fix single only cost item on all but first result structure
            elif default_assumption.costitem.code not in user_assumptions[default_assumption.structure.code]:
                default_assumption.checked = True
                user_assumptions[default_assumption.structure.code][default_assumption.costitem.code] = default_assumption
        result['nonconventional'] = {'sum_value': 0, 'structures': {}}
        result['conventional'] = {'sum_value': 0, 'structures': {} }

        # this is used to compute 'Total PV of Annual O&M Costs' O_and_M costs, Present Value
        study_life = self.study_life

        # dictionary (should be a set) to record which cost items are used
        # in the final results.  later used to remove cost item unit costs if they are not used
        cost_items_seen = set()

        # these are 'Scenario' level values set on the 'Project-Scenario Description' page
        planning_and_design_factor = int(self.planning_and_design_factor)
        study_life = int(self.study_life)
        discount_rate = float(self.discount_rate)

        for structure in structures:

            structure_code = structure.code
            is_checked = False
            sum_value = 0

            # if conventional_structures is None and nonconventional_structures is None:
            #     continue

            if structure.classification == 'conventional':
                if hasattr(conventional_structures, structure_code + '_checkbox'):
                    is_checked = getattr(conventional_structures, structure_code + '_checkbox')
                if hasattr(conventional_structures, structure_code + '_area'):
                    structure.area = getattr(conventional_structures, structure_code + '_area')
            else:
                if hasattr(nonconventional_structures, structure_code + '_checkbox'):
                    is_checked = getattr(nonconventional_structures, structure_code + '_checkbox')
                if hasattr(nonconventional_structures, structure_code + '_area'):
                    structure.area = getattr(nonconventional_structures, structure_code + '_area')

            if is_checked == False:
                continue

            if not structure_code in user_assumptions:
                continue


            # cost_item_user_assumptions = CostItemUserAssumptions.objects.filter(scenario=self, structure=structure, checked=True)

            cost_results = {}

            for costitem_code in user_assumptions[structure_code]: # cost_item_user_assumptions:

                cost_item = user_assumptions[structure_code][costitem_code]

                if not cost_item.checked is True:
                    continue

                # record that you have seen this
                cost_items_seen.add(costitem_code)

                cost_results[costitem_code] = {}

                assumptions = {
                    'units': cost_items_dict[costitem_code]['units'],
                    'name': cost_items_dict[costitem_code]['name'],
                    # 'factor_assumption_tx': cost_item.factor_assumption_tx,
                    'a_area': cost_item.a_area,
                    'z_depth': cost_item.z_depth,
                    'd_density': cost_item.d_density,
                    'n_number': cost_item.n_number,

                }

                # this is the default for these fields
                default = str(9)


                # this is dealing with blank factors ...
                if assumptions['a_area'] in ["", None]:
                    assumptions['a_area'] = default
                if assumptions['z_depth'] in ["", None]:
                    assumptions['z_depth'] = default
                if assumptions['d_density'] in ["", None]:
                    assumptions['d_density'] = default

                # 2019-09-10 set default to 0 so user has to specify number
                if assumptions['n_number'] in ["", None]:
                    assumptions['n_number'] = "0"

                cost_results[costitem_code]['assumptions'] = assumptions

                cost_results[costitem_code]['costs'] = costs[costitem_code]

                results = {}

                structure_units = structure.units
                cost_item_units = cost_items_dict[costitem_code]['units']
                unit_conversion = 1
                if structure_units != cost_item_units:
                    unit_conversion = get_unit_conversion(structure_units, cost_item_units)

                results['unit_conversion'] = unit_conversion

                equation = cost_items_dict[costitem_code]['equation']

                # TODO: figure out where to put this
                # equation = equation + '*' + 'unit_conversion'

                equation = equation.replace('=', '')
                equation = equation.replace('x', '(' + str(structure.area) + '*' + str(unit_conversion) + ')')
                # equation = equation.replace('unit_conversion', str(unit_conversion))
                equation = equation.replace('area', assumptions['a_area'])
                equation = equation.replace('depth', assumptions['z_depth'])
                equation = equation.replace('density', assumptions['d_density'])
                equation = equation.replace('number', assumptions['n_number'])
                equation = equation.replace('$', str(costs[costitem_code]['unit_cost']))

                results['equation_calc'] = equation

                cost_results[costitem_code]['results'] = results

                try:
                    cost_amount = eval(equation)
                    cost_amount = round(cost_amount, 2)
                    sum_value += cost_amount
                    results['value'] = '${:,.2f}'.format(cost_amount)
                    results['value_unformatted'] = cost_amount
                except:
                    cost_amount = equation
                    results['value'] = cost_amount

            result[structure.classification]['sum_value'] += sum_value
            result[structure.classification]['structures'][structure_code] = {'structure':
                                          {
                                            'code': structure.code,
                                            'classification': structure.classification,
                                            'sort_nu': structure.sort_nu,
                                            'name': structure.name,
                                            'area': structure.area,
                                            'units': structure.units,
                                            'units_html': structure.units_html,
                                            'sum_value': '${:,.2f}'.format(sum_value)
                                          },
                                        'cost_data': cost_results
                                    }

        total_construction_cost = 0
        for classification in result:
            result[classification]['sum_value'] = round(result[classification]['sum_value'], 2)
            total_construction_cost += result[classification]['sum_value']

        """
             NOW - this is the calculation from post-construction costs (started on this 2019-11-12)

             I think the way to do it is to find all 'data' that where checked == true
             and then replace all the components of the equation as strings and then eval it

        """
        total_o_and_m_cost = 0
        total_replacement_cost = 0


        """
            these are 'Structure' level values for each 'Cost Item' add the costs for each cost item
        """
        structure_life_cycle_costs = {}
        for classification in result:

            structure_life_cycle_costs[classification] = {
                'meta': {
                    'name':  ('Conventional' if classification == 'conventional' else 'Non-Conventional') + \
                                ' (GSI) Structures',
                },
                'costs': {
                    'sum': 0,
                    'sum_formatted': '',
                    'o_and_m_sum': 0,
                    'o_and_m_sum_formatted': '',
                    'replacement_sum': 0,
                    'replacement_sum_formatted': '',
                }
            }

            for structure_code in result[classification]['structures']:
                if not 'structures' in structure_life_cycle_costs[classification]:
                    structure_life_cycle_costs[classification]['structures'] = {}



                # this has useful labels and size of structures
                structure_data = result[classification]['structures'][structure_code]

                structure_life_cycle_costs[classification]['structures'][structure_code] = {
                    'meta': {
                        'name': structure_data['structure']['name'],
                        'units': structure_data['structure']['units'],
                        'area': structure_data['structure']['area'],
                    },
                    'costs': {
                        'sum': 0,
                        'sum_formatted': '',
                        'o_and_m_sum': 0,
                        'o_and_m_sum_formatted': '',
                        'replacement_sum': 0,
                        'replacement_sum_formatted': '',
                    }
                }

                for costitem_code in result[classification]['structures'][structure_code]['cost_data']:

                    costs_sum = 0

                    if not 'cost_items' in structure_life_cycle_costs[classification]['structures'][structure_code]:
                        structure_life_cycle_costs[classification]['structures'][structure_code]['cost_items'] = {}

                    structure_life_cycle_costs[classification]['structures'][structure_code]['cost_items'][costitem_code] = {'costs': {}}

                    # this has useful labels and size of structures
                    cost_item_data = result[classification]['structures'][structure_code]['cost_data'][costitem_code]

                    construction_cost = cost_item_data['results']['value_unformatted']
                    planning_and_design_costs = round(construction_cost * planning_and_design_factor * 0.01, 2)

                    replacement_life = cost_item_data['costs']['replacement_life']
                    o_and_m_pct = cost_item_data['costs']['o_and_m_pct']

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
                    # =(construction_cost/(1+(discount_rate/100))^i)
                    value_of_first_replacement = 0
                    replacement_years = []
                    replacement_costs = 0

                    if number_of_replacements > 0:
                        for i in range(replacement_life, study_life + 1, replacement_life):
                            replacement_years.append(i)
                            replacement_cost = round(construction_cost / (1 + (discount_rate / 100)) ** i, 2)
                            replacement_costs += replacement_cost
                            # replacements.append(replacement_cost)
                            if value_of_first_replacement == 0:
                                value_of_first_replacement = replacement_costs

                    # if number_of_replacements == 1:
                    #     replacement_years.append(replacement_life)
                    #     replacement_costs = round((construction_cost / (1 + (discount_rate / 100)) ** replacement_life), 2)
                    #     value_of_first_replacement = replacement_costs
                    # elif number_of_replacements > 0:
                    #     for i in range(int(study_life / int(number_of_replacements)), study_life + 1, int(study_life / int(number_of_replacements))):
                    #         replacement_years.append(i)
                    #         replacement_cost = round(construction_cost / (1 + (discount_rate / 100)) ** i, 2)
                    #         replacement_costs += replacement_cost
                    #         # replacements.append(replacement_cost)
                    #         if value_of_first_replacement == 0:
                    #             value_of_first_replacement = replacement_costs

                    o_and_m_costs = round(o_and_m_costs, 2)
                    replacement_costs = round(replacement_costs, 2)

                    total_o_and_m_cost += o_and_m_costs
                    total_replacement_cost += replacement_costs

                    costs_sum += o_and_m_costs + replacement_costs

                    # add to structure costs
                    structure_life_cycle_costs[classification]['structures'][structure_code]['costs']['sum'] += costs_sum
                    structure_life_cycle_costs[classification]['structures'][structure_code]['costs']['sum_formatted'] = \
                        '${:,.2f}'.format(structure_life_cycle_costs[classification]['structures'][structure_code]['costs']['sum'])
                    structure_life_cycle_costs[classification]['structures'][structure_code]['costs']['o_and_m_sum'] += o_and_m_costs
                    structure_life_cycle_costs[classification]['structures'][structure_code]['costs']['o_and_m_sum_formatted'] = \
                        '${:,.2f}'.format(structure_life_cycle_costs[classification]['structures'][structure_code]['costs']['o_and_m_sum'])

                    structure_life_cycle_costs[classification]['structures'][structure_code]['costs']['replacement_sum'] += replacement_costs
                    structure_life_cycle_costs[classification]['structures'][structure_code]['costs']['replacement_sum_formatted'] = \
                        '${:,.2f}'.format(structure_life_cycle_costs[classification]['structures'][structure_code]['costs']['replacement_sum'])
                    # add to classifiction costs
                    structure_life_cycle_costs[classification]['costs']['o_and_m_sum'] += o_and_m_costs
                    structure_life_cycle_costs[classification]['costs']['o_and_m_sum_formatted'] = \
                        '${:,g}'.format(structure_life_cycle_costs[classification]['costs']['o_and_m_sum'])

                    structure_life_cycle_costs[classification]['costs']['replacement_sum'] += replacement_costs
                    structure_life_cycle_costs[classification]['costs']['replacement_sum_formatted'] = \
                        '${:,g}'.format(structure_life_cycle_costs[classification]['costs']['replacement_sum'])

                    structure_life_cycle_costs[classification]['costs']['sum'] += costs_sum
                    structure_life_cycle_costs[classification]['costs']['sum_formatted'] = \
                        '${:,.2f}'.format(structure_life_cycle_costs[classification]['costs']['sum'])

                    structure_life_cycle_costs[classification]['structures'][structure_code]['cost_items'][costitem_code] = {
                        'meta': {
                            'name': cost_item_data['assumptions']['name'],
                            'units': cost_item_data['assumptions']['units'],
                        },
                        'costs': {
                            'construction': construction_cost,
                            'construction_formatted': '${:,.2f}'.format(construction_cost),
                            'planning_and_design': planning_and_design_costs,
                            'planning_and_design_formatted': '${:,.2f}'.format(planning_and_design_costs),
                            'o_and_m': round(o_and_m_costs, 2),
                            'o_and_m_formatted': '${:,.2f}'.format(o_and_m_costs),
                            'first_replacement': value_of_first_replacement,
                            'replacement': round(replacement_costs, 2),
                            'replacement_formatted': '${:,.2f}'.format(replacement_costs),
                            'replacement_years': replacement_years,
                        }
                    }

        #TODO sum o_and_m
        #TODO sum replacement

        project_life_cycle_costs = {'construction': total_construction_cost,
                                    'planning_and_design': total_construction_cost * (planning_and_design_factor / 100),
                                    'O_and_M': total_o_and_m_cost,
                                    'replacement': total_replacement_cost,
                                    }

        total = 0
        for cost in project_life_cycle_costs:
            total += project_life_cycle_costs[cost]
        project_life_cycle_costs['total'] = total

        result['project_life_cycle_costs'] = project_life_cycle_costs
        result['structure_life_cycle_costs'] = structure_life_cycle_costs

        return result

#
# this stores the 'scenario' values for the costitem costs.
# each row is attached to one CostItem for one Scenario
#
#
class CostItemUserCosts(models.Model):
    scenario = models.ForeignKey(Scenario, related_name="cost_item_user_costs", on_delete=models.CASCADE, default=None, blank=False, null=False)
    costitem = models.ForeignKey(CostItem, on_delete=models.CASCADE, default=None, blank=False, null=False)

    COST_SOURCE_VALUES = ('rsmeans', 'db_25_pct', 'db_50_pct', 'db_75_pct')
    COST_SOURCE_TEXTS = ('Eng. Est.', 'DB - 25%', 'DB - 50%', 'DB - 75%')
    COST_SOURCE_CHOICES = zip(COST_SOURCE_VALUES, COST_SOURCE_TEXTS)

    # content of dropdown list
    cost_source = models.CharField("Source of user_input_cost", choices=COST_SOURCE_CHOICES,
                                   unique=False, max_length=24,
                                   default=None, blank=False,null=False)
    #
    user_input_cost = MoneyField('User supplied unit cost', decimal_places=2, max_digits=11,
                                default_currency='USD', blank=True, null=True)
    base_year = models.PositiveIntegerField(default=1990, validators=[MinValueValidator(1990),
                                                       MaxValueValidator(2090)
                                                       ], blank=True, null=True)
    replacement_life = models.PositiveIntegerField("Replacement Life ('R')",
                                                   default=40,validators=[MinValueValidator(5),
                                                       MaxValueValidator(100)
                                                       ], blank=True, null=True)

    #
    o_and_m_pct = models.PositiveIntegerField("Ongoing Operations and Maintenance Factor (%)",
                                              default=0,
                                              validators=[MinValueValidator(0),
                                                          MaxValueValidator(100)
                                                          ],
                                              blank=True, null=True)

    first_year_maintenance = MoneyField('User supplied First Year Maintenance Cost', decimal_places=2, max_digits=11,
                                default_currency='USD', blank=True, null=True)

    def __str__(self):
        return self.scenario.scenario_title + " -- " + self.costitem.code + " -- " + self.cost_source

    class Meta:
        verbose_name_plural = "Cost Item User Costs"
        unique_together = (("scenario", "costitem"))

'''

    This is connected to the Structure Costs page
    and stores data by scenario/structure/costitem
    
    the 'user' cost assumptions are stored in CostItemUserAssumptions 

'''

class CostItemUserAssumptions(models.Model):
    scenario = models.ForeignKey(Scenario, related_name="cost_item_user_assumptions", on_delete=models.CASCADE, default=None, blank=False, null=False)
    structure = models.ForeignKey(Structures, on_delete=models.DO_NOTHING, default=None, blank=False, null=False)
    costitem = models.ForeignKey(CostItem, on_delete=models.DO_NOTHING, default=None, blank=False, null=False)

    checked = models.BooleanField("Checked in UI", default=None, null=True)

    a_area = models.CharField("Area (a)", max_length=10, default=None, blank=True, null=True)
    z_depth = models.CharField("Depth (z)", max_length=10, default=None, blank=True, null=True)
    d_density = models.CharField("Density (d)", max_length=10, default=None, blank=True, null=True)
    r_ratio = models.CharField("Ratio (r)", max_length=10, default=None, blank=True, null=True)
    n_number = models.CharField("Count (n)", max_length=10, default=None, blank=True, null=True)

    def __str__(self):
        return str(self.scenario.id) + " -- " + self.structure.code + " -- " + self.costitem.code

    class Meta:
        verbose_name_plural = "Structure Cost Item User Assumptions"
        unique_together = (("scenario", 'structure', "costitem"))
