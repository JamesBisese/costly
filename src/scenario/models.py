import logging

from django.db import models, IntegrityError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from djmoney.models.fields import MoneyField
from djmoney.money import Money
from .decorators import sql_query_debugger

from .scenario_frameworks import TEMPLATE_SCENARIO


User = get_user_model()

logger = logging.getLogger('developer')

def get_unit_conversion(structure_units, cost_item_units):
    """
        convert units between Structure Units and Cost Item units
        i.e. ft2 and square yards, ft2 and AC

    """
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


"""
    this starts with all the 1-1 and 1-many models that are included in the scenario
"""
class ArealFeatureLookup(models.Model):
    """

        this is a look-up/meta-data table of Areal Features. (which are handled exactly like Structures and ScenarioStructures)

    """
    code = models.CharField(unique=True, max_length=100, default=None, blank=False, null=False)
    name = models.CharField(unique=True, max_length=100, default=None, blank=False, null=False)
    sort_nu = models.PositiveIntegerField("Sort Number", default=0, blank=True, null=True)
    units = models.CharField(unique=False, max_length=12, default=None, blank=False, null=False)
    units_html = models.CharField(unique=False, max_length=25, default=None, blank=False, null=False)
    help_text = models.CharField(unique=False, max_length=1000, default="TBD", blank=False, null=False)

    def __str__(self):
        return self.code + ' - ' + self.name

    class Meta:
        verbose_name_plural = "Areal Features"
        ordering = ['sort_nu', ]

# DEPRECIATED.
# class ArealFeatures(models.Model):
#     """
#
#         this is a set of tuples - each tuple has a checkbox and an area
#
#         Note: the id field is scenario.id
#
#         TODO: label the fields as necessary.
#
#         TODO: refactor the name from ArealFeatures to ScenarioArealFeatures
#         TODO: make a new model ArealFeatures or ArealFeaturesLookup to store the list of areal features
#
#     """
#     stormwater_management_feature_area = models.IntegerField("Stormwater Management Feature Area", default=0,
#                                                              blank=True, null=True)
#     stormwater_management_feature_checkbox = models.BooleanField("Stormwater Management Feature Checked", default=False,
#                                                                  blank=True, null=True)
#     amenity_plaza_area = models.IntegerField("Amenity Areas/Urban Plaza Area", default=0,
#                                              blank=True, null=True)
#     amenity_plaza_checkbox = models.BooleanField("Amenity Areas/Urban Plaza Checked", default=False,
#                                                  blank=True, null=True)
#     protective_yard_area = models.IntegerField("Protective Yards Area", default=0,
#                                                blank=True, null=True)
#     protective_yard_checkbox = models.BooleanField("Protective Yards Checked", default=False,
#                                                    blank=True, null=True)
#
#     parking_island_checkbox = models.BooleanField(" Checked", default=False, blank=True, null=True)
#     parking_island_area = models.IntegerField(" Area", default=0, blank=True, null=True)
#     building_checkbox = models.BooleanField(" Checked", default=False, blank=True, null=True)
#     building_area = models.IntegerField(" Area", default=0, blank=True, null=True)
#     drive_thru_facility_checkbox = models.BooleanField(" Checked", default=False, blank=True, null=True)
#     drive_thru_facility_area = models.IntegerField(" Area", default=0, blank=True, null=True)
#     landscape_checkbox = models.BooleanField(" Checked", default=False, blank=True, null=True)
#     landscape_area = models.IntegerField(" Area", default=0, blank=True, null=True)
#     sidewalk_checkbox = models.BooleanField(" Checked", default=False, blank=True, null=True)
#     sidewalk_area = models.IntegerField(" Area", default=0, blank=True, null=True)
#     street_checkbox = models.BooleanField(" Checked", default=False, blank=True, null=True)
#     street_area = models.IntegerField(" Area", default=0, blank=True, null=True)
#     median_checkbox = models.BooleanField(" Checked", default=False, blank=True, null=True)
#     median_area = models.IntegerField(" Area", default=0, blank=True, null=True)
#     parking_lot_checkbox = models.BooleanField(" Checked", default=False, blank=True, null=True)
#     parking_lot_area = models.IntegerField(" Area", default=0, blank=True, null=True)
#     driveway_and_alley_checkbox = models.BooleanField(" Checked", default=False, blank=True, null=True)
#     driveway_and_alley_area = models.IntegerField(" Area", default=0, blank=True, null=True)


class Structures(models.Model):
    """

        this is a look-up/meta-data table of Structures.

    """
    CLASSIFICATION_VALUES = ('conventional', 'nonconventional')
    CLASSIFICATION_TEXTS = ('Conventional', 'Non-Conventional')
    CLASSIFICATION_CHOICES = zip(CLASSIFICATION_VALUES, CLASSIFICATION_TEXTS)

    code = models.CharField(unique=True, max_length=100, default=None, blank=False, null=False)
    name = models.CharField(unique=True, max_length=100, default=None, blank=False, null=False)
    classification = models.CharField(unique=False, choices=CLASSIFICATION_CHOICES, max_length=15, default=None,
                                      blank=False, null=False)
    sort_nu = models.PositiveIntegerField("Sort Number", default=0, blank=True, null=True)
    units = models.CharField(unique=False, max_length=12, default=None, blank=False, null=False)
    units_html = models.CharField(unique=False, max_length=25, default=None, blank=False, null=False)
    help_text = models.CharField(unique=False, max_length=1000, default="TBD", blank=False, null=False)

    def __str__(self):
        return self.classification + ' - ' + self.name

    def save(self, *args, **kwargs):
        # mylist = ['up', 'down', 'strange', 'charm', ....]
        if self.classification in self.CLASSIFICATION_VALUES:
            super(Structures, self).save(*args, **kwargs)
        else:
            raise IntegrityError("Structures.classification only one of the following values: " + ', '.join(self.CLASSIFICATION_VALUES))

    class Meta:
        verbose_name_plural = "Structures"
        ordering = ['sort_nu', ]

# DEPRECIATED.
# class ConventionalStructures(models.Model):
#     """
#
#         this is a data table of ConventionalStructures
#
#         note: the id for each row in this table is the scenario.id
#
#         note: this is being DEPRECIATED to be replaced by ScenarioStructure
#
#     """
#     stormwater_wetland_checkbox = models.BooleanField("Stormwater Wetland Checked", default=False, blank=True,
#                                                       null=True)
#     stormwater_wetland_area = models.IntegerField("Stormwater Wetland Area", default=0, blank=True, null=True)
#     stormwater_wetland_first_year_costs = MoneyField("1st year maintenance costs",
#                                                      decimal_places=2, max_digits=11, default=0, default_currency='USD',
#                                                      blank=True, null=True)
#
#     pond_checkbox = models.BooleanField(default=False, blank=True, null=True)
#     pond_area = models.IntegerField(default=0, blank=True, null=True)
#     rooftop_checkbox = models.BooleanField(default=False, blank=True, null=True)
#     rooftop_area = models.IntegerField(default=0, blank=True, null=True)
#     lawn_checkbox = models.BooleanField(default=False, blank=True, null=True)
#     lawn_area = models.IntegerField(default=0, blank=True, null=True)
#     landscaping_checkbox = models.BooleanField(default=False, blank=True, null=True)
#     landscaping_area = models.IntegerField(default=0, blank=True, null=True)
#     trench_checkbox = models.BooleanField(default=False, blank=True, null=True)
#     trench_area = models.IntegerField(default=0, blank=True, null=True)
#     concrete_checkbox = models.BooleanField(default=False, blank=True, null=True)
#     concrete_area = models.IntegerField(default=0, blank=True, null=True)
#     asphalt_checkbox = models.BooleanField(default=False, blank=True, null=True)
#     asphalt_area = models.IntegerField(default=0, blank=True, null=True)
#     curb_and_gutter_checkbox = models.BooleanField(default=False, blank=True, null=True)
#     curb_and_gutter_area = models.IntegerField(default=0, blank=True, null=True)
#
# # DEPRECIATED.
# class NonConventionalStructures(models.Model):
#     """
#
#         this is a OneToOne data table of scenario.NonConventionalStructures
#
#         note: the id for each row in this table is the scenario.id
#
#         note: this is being DEPRECIATED to be replaced by ScenarioStructures
#
#     """
#     swale_area = models.IntegerField("Swale Area", default=0, blank=True, null=True)
#     swale_checkbox = models.BooleanField("Swale Checked", default=False, blank=True, null=True)
#     rain_harvesting_device_checkbox = models.BooleanField(default=False, blank=True, null=True)
#     rain_harvesting_device_area = models.IntegerField(default=0, blank=True, null=True)
#     bioretention_cell_checkbox = models.BooleanField(default=False, blank=True, null=True)
#     bioretention_cell_area = models.IntegerField(default=0, blank=True, null=True)
#     filter_strip_checkbox = models.BooleanField(default=False, blank=True, null=True)
#     filter_strip_area = models.IntegerField(default=0, blank=True, null=True)
#     green_roof_checkbox = models.BooleanField(default=False, blank=True, null=True)
#     green_roof_area = models.IntegerField(default=0, blank=True, null=True)
#     planter_box_checkbox = models.BooleanField(default=False, blank=True, null=True)
#     planter_box_area = models.IntegerField(default=0, blank=True, null=True)
#     porous_pavement_checkbox = models.BooleanField(default=False, blank=True, null=True)
#     porous_pavement_area = models.IntegerField(default=0, blank=True, null=True)
#

class CostItem(models.Model):
    """

        this is a look-up/meta-data table of Cost Item (CostItem, CostItems)

    """
    code = models.CharField(unique=True, max_length=50, default=None, blank=False, null=False)
    name = models.CharField(unique=True, max_length=50, default=None, blank=False, null=False)
    sort_nu = models.PositiveIntegerField("Sort Number", default=0, blank=True, null=True)
    units = models.CharField(unique=False, max_length=12, default=None, blank=False, null=False)
    help_text = models.CharField(unique=False, max_length=1000, default="TBD", blank=False, null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Cost Items"
        ordering = ['sort_nu', ]


class CostItemDefaultCosts(models.Model):
    """

        this is a look-up table of the 'default' costs associated with each Cost Items

        the 'user' costs are stored in StructureCostItemUserCosts which is defined after Scenario model

    """
    costitem = models.ForeignKey(CostItem, on_delete=models.CASCADE, default=None, blank=False, null=False)

    # region new storage
    cost_type = models.CharField("Cost Estimate Type", max_length=50, default='Engineer Estimate', blank=False, null=False)
    value_numeric = MoneyField('Unit Cost ($)', decimal_places=2, max_digits=11,
                               default_currency='USD', blank=False, null=False)
    valid_start_date_tx = models.CharField("Year (revision)", max_length=20, default='2022', blank=False, null=False)

    created_date = models.DateTimeField('Created Date', null=True, auto_now_add=True)
    modified_date = models.DateTimeField('Modified Date', auto_now=True)
    # endregion new storage

    # region old storage
    rsmeans_va = MoneyField('RSMeans unit cost', decimal_places=2, max_digits=11,
                            default_currency='USD', blank=True, null=True)
    db_25pct_va = MoneyField('DB 25-percentile unit cost', decimal_places=2, max_digits=11,
                             default_currency='USD', blank=True, null=True)
    db_50pct_va = MoneyField('DB Average unit cost', decimal_places=2, max_digits=11,
                             default_currency='USD',
                             blank=True, null=True)
    db_75pct_va = MoneyField('DB 75-percentile unit cost', decimal_places=2, max_digits=11,
                             default_currency='USD', blank=True, null=True)
    # endregion old storage

    def __str__(self):
        return self.costitem.name + " -- " + self.cost_type + " -- " + \
               self.valid_start_date_tx + " -- " + str(self.value_numeric.amount)

    class Meta:
        verbose_name_plural = "Cost Item Default Costs"
        ordering = ['costitem__sort_nu', '-valid_start_date_tx']
        # new storage
        unique_together = ('costitem', 'cost_type', 'valid_start_date_tx')


class CostItemDefaultEquations(models.Model):
    """
        Cost Item Default Equations

        look-up table of the 'default' costs equations and factors for each Cost Items
        AND NOT connected to a specific structure

        Loaded from CSV file CostItemDefaultEquations
    """
    costitem = models.OneToOneField(CostItem, unique=True, on_delete=models.CASCADE, default=None, blank=False,
                                    null=False)

    equation_tx = models.CharField("Equation", max_length=150, default=None, blank=True, null=True)

    replacement_life = models.PositiveIntegerField(default=40,
                                                   validators=[MinValueValidator(0),
                                                               MaxValueValidator(100)
                                                               ],
                                                   blank=False, null=False)

    o_and_m_pct = models.PositiveIntegerField(default=0,
                                              validators=[MinValueValidator(0),
                                                          MaxValueValidator(100)
                                                          ],
                                              blank=False, null=False)

    # this is not used.  always ste as 'The cost of ' + cost_item.name + ' is computed using ...'
    help_text = models.CharField(unique=False, max_length=1000, default="Help Text", blank=False, null=False)

    def __str__(self):
        return self.costitem.code + " -- " + self.equation_tx

    def save(self, *args, **kwargs):
        if self.o_and_m_pct is not None:
            if self.o_and_m_pct >= 0 and self.o_and_m_pct <= 100:
                super(CostItemDefaultEquations, self).save(*args, **kwargs)
        else:
            raise IntegrityError("CostItemDefaultEquations.o_and_m_pct has to be between 0 and 100")

    class Meta:
        verbose_name_plural = "Cost Item Default Equations"
        ordering = ['costitem__sort_nu', ]


class StructureCostItemDefaultFactors(models.Model):
    """
        look-up table of the 'default' costs factors with each Structure/Cost Items tuple

        the 'user' cost assumptions are stored in StructureCostItemUserFactors which is defined after Scenario model
    """
    structure = models.ForeignKey(Structures, on_delete=models.CASCADE, default=None, blank=False, null=False)
    costitem = models.ForeignKey(CostItem, on_delete=models.CASCADE, default=None, blank=False, null=False)

    a_area = models.CharField("Area (a)", max_length=10, default=None, blank=True, null=True)
    z_depth = models.CharField("Depth (z)", max_length=10, default=None, blank=True, null=True)
    d_density = models.CharField("Density (d)", max_length=10, default=None, blank=True, null=True)
    n_number = models.CharField("Count (n)", max_length=10, default=None, blank=True, null=True)

    def __str__(self):
        return self.structure.code + " -- " + self.costitem.code

    class Meta:
        verbose_name_plural = "Structure Cost Item Default Factors"
        unique_together = ('structure', "costitem")
        ordering = ['costitem__sort_nu', ]


class Project(models.Model):
    """

    User owns 0 or more Project(s).  Project has 0 or more Scenario(s).

    """
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

    project_title = models.CharField('Project Title', unique=False, max_length=200, default=None, blank=False,
                                     null=False)

    project_ownership = models.CharField('Project Organizer', choices=OWNERSHIP_TYPE_CHOICES, max_length=15, blank=True,
                                         null=True)
    project_location = models.CharField('Location of the project', max_length=150, default=None, blank=True, null=True)

    project_type = models.CharField('Project Type', choices=PROJECT_TYPE_CHOICES, max_length=25, blank=True, null=True)
    project_purchase_information = models.CharField('Purchase Information', choices=PURCHASE_TYPE_CHOICES,
                                                    max_length=15, default=None, blank=True, null=True)
    priority_watershed = models.CharField('Priority Watershed', choices=WATERSHED_CHOICES, max_length=15, default=None,
                                          blank=True, null=True)

    # todo: should be IntegerField
    project_area = models.CharField('Total Project Area (square feet)', max_length=15, default=None, blank=False,
                                    null=False)
    land_unit_cost = MoneyField('Cost per square foot of Project site',
                                decimal_places=2, max_digits=11, default=1,
                                default_currency='USD', blank=False, null=False)

    create_date = models.DateTimeField('Create Date', auto_now_add=True)
    modified_date = models.DateTimeField('Modified Date', auto_now=True)

    def __str__(self):
        return self.project_title

    class Meta:
        verbose_name_plural = "Projects"
        unique_together = ("user", "project_title")


def get_TEMPLATE_SCENARIO():
    """
        TODO: replace this with building the JSON object using model content

    """
    raw_ts = TEMPLATE_SCENARIO

    areal_features = ArealFeatureLookup.objects.all().order_by('sort_nu').values()
    fields = []
    inputs = {}
    for areal_feature in areal_features:
        fields.append(areal_feature['code'])
        inputs[areal_feature['code']] = ['checkbox', 'area']
    raw_ts['siteData']['areal_features'] = {}
    raw_ts['siteData']['areal_features']['fields'] = fields
    raw_ts['siteData']['areal_features']['inputs'] = inputs

    structures = Structures.objects.all().order_by('sort_nu').values()
    fields = []
    labels = {}
    inputs = {}

    for structure in structures:
        if structure['classification'] == 'conventional':
            fields.append(structure['code'])
            labels[structure['code']] = structure['name']
            inputs[structure['code']] = ['checkbox', 'area']
    raw_ts['siteData']['conventional_structures'] = {}
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
    raw_ts['siteData']['nonconventional_structures'] = {}
    raw_ts['siteData']['nonconventional_structures']['fields'] = fields
    raw_ts['siteData']['nonconventional_structures']['labels'] = labels
    raw_ts['siteData']['nonconventional_structures']['inputs'] = inputs

    cost_items = CostItem.objects.all().order_by('sort_nu').values()
    fields = []
    for cost_item in cost_items:
        fields.append(cost_item['code'])
    raw_ts['siteData']['cost_items'] = {}
    raw_ts['siteData']['cost_items']['fields'] = fields

    return raw_ts


class Scenario(models.Model):
    """

    a Scenario is attached to a single Project.

    """
    # this is a template used in Javascript to figure out how to manage the UI
    # it is stored in a module 'scenario_frameworks' just because it is big and ugly
    templateScenario = None

    try:
        templateScenario = get_TEMPLATE_SCENARIO()
    except:
        pass

    NUTRIENT_REQ_VALUES = ('with_buy_down', 'without_buy_down', 'unknown')
    NUTRIENT_REQ_TEXTS = ('With Nutrient Buy Down', 'Without Nutrient Buy Down', 'Unknown')
    NUTRIENT_CHOICES = zip(NUTRIENT_REQ_VALUES, NUTRIENT_REQ_TEXTS)

    REGS_REQ_VALUES = ('yes', 'no', 'unknown')
    REGS_REQ_TEXTS = ('Yes', 'No', 'unknown')
    REGS_CHOICES = zip(REGS_REQ_VALUES, REGS_REQ_TEXTS)
    REGS_CHOICES2 = zip(REGS_REQ_VALUES, REGS_REQ_TEXTS)

    project = models.ForeignKey(Project, on_delete=models.CASCADE, default=None, blank=False, null=False)

    scenario_title = models.CharField('Scenario Name', unique=False, max_length=200, default=None, blank=False,
                                      null=False)
    scenario_date = models.DateField('Scenario Date', auto_now_add=False, default=None, blank=True, null=True)

    pervious_area = models.IntegerField(default=0, blank=True, null=True)

    impervious_area = models.IntegerField(default=0, blank=True, null=True)

    nutrient_req_met = models.CharField('Level of nutrient requirements met', choices=NUTRIENT_CHOICES, max_length=25,
                                        default='unknown', blank=True, null=True)
    captures_90pct_storm = models.CharField('Site captures the 90th percentile storm volume', choices=REGS_CHOICES,
                                            max_length=25, default='unknown', blank=True, null=True)
    meets_peakflow_req = models.CharField('Site meets peak flow requirements', choices=REGS_CHOICES2, max_length=25,
                                          default='unknown', blank=True, null=True)

    planning_and_design_factor = models.DecimalField("Planning and Design Factor (Multiplier)",
                                                        max_digits=12, decimal_places=2,
                                                        default=20.0, blank=True, null=True)
    study_life = models.IntegerField("Study Life(years)", default=40, blank=True, null=True)
    discount_rate = models.FloatField("Discount Rate(DISC)", default=2.875, blank=True, null=True)

    counter = models.IntegerField('Integer Counter', default=0, blank=False, null=False)

    create_date = models.DateTimeField('Create Date', auto_now_add=True)
    modified_date = models.DateTimeField('Modified Date', auto_now=True)

    def __str__(self):
        return self.project.project_title + " -- " + self.scenario_title

    class Meta:
        verbose_name_plural = "Scenarios"
        unique_together = ("project", "scenario_title")

    def process_related_data(self, form_data, active_tab='FOOBAR'):
        """

            process all the scenario related data (structures, costs, assumptions, etc.)

        """
        scenarioTemplate = Scenario.templateScenario['siteData']

        """ process the elements on the Project-Scenario Description tab """
        if active_tab == 'project_information':
            list_of_attributes = scenarioTemplate['embedded_scenario']['fields']
            list_of_values = form_data['embedded_scenario']

            for field in list_of_attributes:
                if hasattr(self, field):
                    val = list_of_values[field]

                    val = None if val == '' else val
                    setattr(self, field, val)

            list_of_values = form_data['areal_features']
            areal_features = ArealFeatureLookup.objects.all().order_by('sort_nu')

            for areal_feature in areal_features:
                if areal_feature.code in list_of_values:
                    area_value = list_of_values[areal_feature.code]['area'] or None
                    is_checked = list_of_values[areal_feature.code]['checkbox'] or False

                    self.process_areal_feature(areal_feature, area_value, is_checked)

        """ process the elements on the Structures tab """
        if active_tab == 'structures':
            classification_values = ('conventional', 'nonconventional')

            for classification in classification_values:
                list_of_values = form_data[classification + '_structures']
                structures = Structures.objects\
                    .only('id', 'code', 'name', 'classification')\
                    .filter(classification=classification).order_by('sort_nu')

                scenario_structures = ScenarioStructure.objects\
                    .select_related('structure')\
                    .filter(scenario=self, structure__classification=classification)

                for structure in structures:
                    if structure.code in list_of_values:
                        area_value = list_of_values[structure.code]['area'] or None
                        is_checked = list_of_values[structure.code]['checkbox'] or False

                        self.process_scenario_structure(structure, scenario_structures, area_value, is_checked)

        if active_tab == 'costitems':
            self.process_cost_item_unit_costs(form_data['cost_items']['unit_costs'])

        if active_tab == 'structure_costs':
            self.process_strucure_costitem_user_factors(form_data['cost_items']['user_assumptions'],
                                                        scenarioTemplate['cost_items']['fields'])

        return


    def process_areal_feature(self, areal_feature, area_value, is_checked):
        """
        This is the 'new' storage for ScenarioArealFeature data - which is per-scenario data.
        It stores non-empty (value is not blank OR checkbox is checked)

        :param areal_feature:
        :param area_value:
        :param is_checked:
        :return:
        """
        if area_value == None and is_checked is False:
            # DELETE
            if ScenarioArealFeature.objects.filter(scenario=self, areal_feature=areal_feature).exists():
                c = ScenarioArealFeature.objects.get(scenario=self, areal_feature=areal_feature)
                c.delete()

        elif area_value is not None or is_checked is True:
            # CREATE
            if not ScenarioArealFeature.objects.filter(scenario=self, areal_feature=areal_feature).exists():
                c = ScenarioArealFeature.objects.create(scenario=self, areal_feature=areal_feature,
                                                     area=area_value, is_checked=is_checked)
                c.save()
            else:
                # UPDATE
                c = ScenarioArealFeature.objects.get(scenario=self, areal_feature=areal_feature)
                changed_fields = set()

                if c.area != area_value:
                    setattr(c, 'area', area_value)
                    changed_fields.add('area')

                if c.is_checked != is_checked:
                    setattr(c, 'is_checked', is_checked)
                    changed_fields.add('is_checked')

                if len(changed_fields) > 0:
                    c.save()

    def process_scenario_structure(self, structure, scenario_structures, area_value, is_checked):
        """
        This is the 'new' storage for ScenarioStructure data - which is per-scenario data.
        It stores non-empty (value is not blank AND checkbox is checked)

        :param structure:
        :param area_value:
        :param is_checked:
        :return:
        """

        scenario_structures_objs = [x for x in scenario_structures if x.structure.code == structure.code]

        if scenario_structures_objs is not None and len(scenario_structures_objs) > 0:
            scenario_structures_obj = scenario_structures_objs[0]
        else:
            scenario_structures_obj = None

        if area_value is None and is_checked is False:
            # DELETE
            if scenario_structures_obj is not None:
                scenario_structures_obj.delete()

        elif area_value is not None or is_checked is True:
            # CREATE
            if scenario_structures_obj is None:
                c = ScenarioStructure.objects.create(scenario=self, structure=structure,
                                                     area=area_value, is_checked=is_checked)
                c.save()
            else:
                # UPDATE
                c = scenario_structures_obj
                changed_fields = set()

                if not (c.area is None and area_value is None):
                    if c.area is not None and area_value is None:
                        setattr(c, 'area', None)
                        changed_fields.add('area')
                    else:
                        area_value_int = None
                        try:
                            area_value_int = int(area_value)
                        except:
                            pass

                        if area_value_int is not None and c.area is None or (int(c.area) != area_value_int):
                            setattr(c, 'area', area_value)
                            changed_fields.add('area')

                if c.is_checked != is_checked:
                    setattr(c, 'is_checked', is_checked)
                    changed_fields.add('is_checked')

                if len(changed_fields) > 0:
                    c.save(update_fields=list(changed_fields))


    def process_strucure_costitem_user_factors(self, user_assumptions, cost_items):
        """
            process the content of the 'Structure Cost Item User Factors' tab
              - combination of Structure (single) and Cost Items

            user_assumptions should have a single 'structure' - the structure selected
            by the user in the drop-down list

        """
        # if the user has not selected anything from the Structure Costs drop-down then there is none of this data
        structure_code = None
        list_of_values = None
        if user_assumptions is not None:
            structure_code = user_assumptions['structure']
            list_of_values = user_assumptions['data']

        # have to run through all the cost_items to delete any that are not found
        structure_obj = None
        structure_cost_item_user_factors = StructureCostItemUserFactors.objects\
            .select_related('scenario', 'scenario__project', 'costitem', 'structure')\
            .filter(scenario_id=self.id, structure__code=structure_code)

        for cost_item in cost_items:
            cost_item_assumptions_objs = [x for x in structure_cost_item_user_factors if x.costitem.code == cost_item]
            if cost_item_assumptions_objs is not None and len(cost_item_assumptions_objs) > 0:
                cost_item_assumptions_obj = cost_item_assumptions_objs[0]
            else:
                cost_item_assumptions_obj = None

            # remove the values if they are all ''
            input_empty = False
            form_values = None
            if cost_item in list_of_values:
                form_values = list_of_values[cost_item]
                # set empty string to null

                if form_values['a_area'] == '':
                    form_values['a_area'] = None
                if form_values['z_depth'] == '':
                    form_values['z_depth'] = None
                if form_values['d_density'] == '':
                    form_values['d_density'] = None
                if form_values['n_number'] == '':
                    form_values['n_number'] = None

                if form_values['checked'] is False \
                        and form_values['a_area'] is None \
                        and form_values['z_depth'] is None \
                        and form_values['d_density'] is None \
                        and form_values['n_number'] is None:
                    input_empty = True

                # 2019-09-10 delete if they uncheck and discard any input
                # if form_values['checked'] is False:
                #     input_empty = True

            if cost_item_assumptions_obj is not None:
                if cost_item not in list_of_values or input_empty is True:
                    # DELETE
                    # cost_item_assumptions_obj.delete()

                    continue
                elif cost_item_assumptions_obj.checked != form_values['checked'] or \
                        cost_item_assumptions_obj.a_area != form_values['a_area'] or \
                        cost_item_assumptions_obj.z_depth != form_values['z_depth'] or \
                        cost_item_assumptions_obj.d_density != form_values['d_density'] or \
                        cost_item_assumptions_obj.n_number != form_values['n_number']:

                    # UPDATE
                    cost_item_assumptions_obj.checked = form_values['checked']

                    cost_item_assumptions_obj.a_area = form_values['a_area']
                    cost_item_assumptions_obj.z_depth = form_values['z_depth']
                    cost_item_assumptions_obj.d_density = form_values['d_density']
                    cost_item_assumptions_obj.n_number = form_values['n_number']

                    cost_item_assumptions_obj.save()

                    """
                        TODO: add calculation here
                    """
                    form_values['construction_cost_factor_equation'] = '=mc2'
                    form_values['cost_V1'] = '$99.99'

                else:
                    pass

            elif form_values is not None and input_empty is False:
                if structure_obj is None:
                    structure_obj = Structures.objects.get(code=structure_code)

                cost_item_obj = CostItem.objects.get(code=cost_item)
                # CREATE
                c = StructureCostItemUserFactors(
                    scenario=self,
                    structure=structure_obj,
                    costitem=cost_item_obj,

                    checked=form_values['checked'],

                    a_area=form_values['a_area'],
                    z_depth=form_values['z_depth'],
                    d_density=form_values['d_density'],
                    n_number=form_values['n_number'],
                )
                c.save()


    # @sql_query_debugger
    def process_cost_item_unit_costs(self, cost_items):

        """
        
            this manages the tab 'Scenario Cost Item Unit Costs'

            the input 'cost_items' are a dictionary from the form.
            
        """
        scenario_cost_item_costs = ScenarioCostItemUserCosts.objects \
            .select_related('costitem') \
            .defer('first_year_maintenance', 'first_year_maintenance_currency',)\
            .filter(scenario_id=self.id)

        cost_item_default_costs = CostItemDefaultCosts.objects \
            .select_related('costitem') \
            .all().order_by("costitem__sort_nu")

        cost_item_default_equations = CostItemDefaultEquations.objects \
            .select_related('costitem') \
            .only('costitem__code', 'replacement_life', 'o_and_m_pct')\
            .all().order_by("costitem__sort_nu")

        for cost_item, form_costs in cost_items.items():

            user_costs_obj = None

            if form_costs['replacement_life'] == 'None':
                form_costs['replacement_life'] = None

            if form_costs['cost_source'] != 'user':
                form_costs['user_input_cost'] = None
                form_costs['base_year'] = None

            user_costs_objs = [x for x in scenario_cost_item_costs if x.costitem.code == cost_item]
            if user_costs_objs is not None and len(user_costs_objs) > 0:
                user_costs_obj = user_costs_objs[0]

            default_costs_objs = [x for x in cost_item_default_costs if x.costitem.code == cost_item]
            if default_costs_objs is not None and len(default_costs_objs) > 0:
                default_costs_obj = default_costs_objs[0]

            default_equations_objs = [x for x in cost_item_default_equations if x.costitem.code == cost_item]
            if default_equations_objs is not None and len(default_equations_objs) > 0:
                default_equations_obj = default_equations_objs[0]

            if default_costs_obj and default_equations_obj:
                default_costs_obj.replacement_life = default_equations_obj.replacement_life
                default_costs_obj.o_and_m_pct = default_equations_obj.o_and_m_pct

            cost_source = form_costs['cost_source']
            user_input_cost = None
            base_year = None

            if user_costs_obj is None:
                # CREATE
                costitem = CostItem.objects.filter(code=cost_item).first()
                if cost_source == 'user':
                    user_input_cost = form_costs['user_input_cost']
                    base_year = form_costs['base_year']

                c = ScenarioCostItemUserCosts(
                    scenario=self,
                    costitem=costitem,
                    cost_source=cost_source,
                    user_input_cost=user_input_cost,
                    base_year=base_year,
                    replacement_life=form_costs['replacement_life'],
                    o_and_m_pct=form_costs['o_and_m_pct'],
                )
                c.save()
            else:
                # UPDATE
                has_changed = 0
                if cost_source == 'user':
                    if user_costs_obj.cost_source != 'user':
                        has_changed += 1
                        user_costs_obj.cost_source = 'user'
                        user_costs_obj.user_input_cost = form_costs['user_input_cost']
                        user_costs_obj.base_year = form_costs['base_year']
                    else:
                        if user_costs_obj.user_input_cost is None:
                            if form_costs['user_input_cost'] is not None:
                                has_changed += 1
                                user_costs_obj.user_input_cost = form_costs['user_input_cost']
                        elif str(user_costs_obj.user_input_cost.amount) != form_costs['user_input_cost']:
                            has_changed += 1
                            user_costs_obj.user_input_cost = form_costs['user_input_cost']
                        if str(user_costs_obj.base_year) != form_costs['base_year']:
                            has_changed += 1
                            user_costs_obj.base_year = form_costs['base_year']
                else:
                    if user_costs_obj.cost_source == 'user':
                        has_changed += 1
                        user_costs_obj.cost_source = int(cost_source)
                    elif user_costs_obj.cost_source != str(int(cost_source)):
                        has_changed += 1
                        user_costs_obj.cost_source = int(cost_source)

                    if user_costs_obj.default_cost_id != int(cost_source):
                        has_changed += 1
                        user_costs_obj.default_cost_id = int(cost_source)

                    if user_costs_obj.user_input_cost is not None:
                        has_changed += 1
                        user_costs_obj.user_input_cost = None

                    if user_costs_obj.base_year is not None:
                        has_changed += 1
                        user_costs_obj.base_year = None

                if user_costs_obj.replacement_life != int(form_costs['replacement_life']):
                    has_changed += 1
                    user_costs_obj.replacement_life = form_costs['replacement_life']

                if user_costs_obj.o_and_m_pct != int(form_costs['o_and_m_pct']):
                    has_changed += 1
                    user_costs_obj.o_and_m_pct = form_costs['o_and_m_pct']
                if has_changed > 0:
                    user_costs_obj.save()

            #     if user_costs_obj.cost_source == 'user' and cost_source != 'user':
            #         if user_costs_obj.user_input_cost != None:
            #             has_changed += 1
            #             user_costs_obj.user_input_cost = None
            #
            #         if user_costs_obj.base_year != None:
            #             has_changed += 1
            #             user_costs_obj.base_year = None
            # if cost_source == 'user':
            #     is_default -= 1  # there is a user cost_source, so it is not 'default' (unless the user_input_cost and year are blank, and the rep_likfe and o+m are defaults
            #     list_of_attributes.extend([
            #         'base_year',
            #         'user_input_cost',
            #     ])
            # elif isinstance(int(cost_source), int):
            #     """ process the new storage """
            #     # UPDATE
            #     has_changed = 0
            #     if user_costs_obj is not None:
            #
            #
            #
            #
            #     else:
            #         # CREATE
            #         costitem = CostItem.objects.filter(code=cost_item).first()
            #
            #         # print("create cost_item {}".format(cost_item))
            #         c = ScenarioCostItemUserCosts(
            #             scenario=self,
            #             costitem=costitem,  # this sets costitem
            #             cost_source=int(cost_source),
            #             user_input_cost=None,
            #             base_year=None,
            #             replacement_life=form_costs['replacement_life'],
            #             o_and_m_pct=form_costs['o_and_m_pct'],
            #         )
            #         c.save()
            #     pass
            #
            # """
            #
            #
            # """
            # for attribute in list_of_attributes:
            #
            #     db_field_value = -1
            #     default_field_value = -1
            #
            #     # submitted form value
            #     form_value = form_costs[attribute]
            #
            #     # existing db user value
            #     if hasattr(user_costs_obj, attribute):
            #         db_field_value = getattr(user_costs_obj, attribute, None)
            #         # special test for Money fields to compare just the amount
            #         if isinstance(db_field_value, Money):
            #             db_field_value = str(db_field_value.amount)
            #         elif attribute == 'cost_source':
            #             if db_record_exists is True and form_value != db_field_value:
            #                 is_default -= 1
            #                 change_count += 1
            #                 """
            #                     don't do any more processing on cost_source
            #                 """
            #                 continue
            #             else:
            #                 pass
            #     elif attribute == 'cost_source':
            #         continue
            #
            #     # default value
            #     if cost_source != 'user' and hasattr(default_costs_obj, attribute):
            #         default_field_value = getattr(default_costs_obj, attribute, None)
            #     elif cost_source == 'user' and attribute != 'cost_source':
            #         if attribute == 'user_input_cost' or attribute == 'base_year':
            #             default_field_value = -1
            #         else:
            #             default_field_value = getattr(default_costs_obj, attribute, None)
            #
            #     if db_field_value != -1 and default_field_value != -1 \
            #             and str(db_field_value) != str(default_field_value):
            #         # store the data
            #         is_default -= 1
            #     if db_field_value != -1 and str(db_field_value) != str(form_value):
            #         # the user changed the value from what they set earlier                    change_count += 1
            #         if default_field_value != -1 and str(form_value) == str(default_field_value):
            #             is_default += 1  # the user reset a value to the default
            #         # this is the place where I am having a problem.  inserted this elif just to test things
            #         elif attribute == 'cost_source':
            #             pass
            #         else:
            #             is_default -= 1
            #
            #     if db_field_value == -1 and default_field_value != -1 \
            #             and str(form_value) != str(default_field_value):
            #         # the user changed the value from the default
            #         is_default -= 1
            #         change_count += 1
            #     elif db_field_value == -1 and default_field_value == -1 \
            #             and str(form_value) is not None:
            #         # there is a value (this is for user_input_cost and base_year)
            #         is_default -= 1
            #         change_count += 1
            #     elif db_field_value != -1 \
            #             and str(form_value) is not None \
            #             and str(form_value) != str(db_field_value):
            #         # there is a value (this is for user_input_cost and base_year)
            #         is_default -= 1
            #         change_count += 1
            #
            #     print_str = "cost_item: {}; field: {}; form_value: {}, " + \
            #                 "db_user_value: {}; default_value: {}; is_default: {}; change_count: {}"
            #
            #     if change_count > 0:
            #         logger.debug(print_str.format(
            #                                 cost_item,
            #                                 attribute,
            #                                 form_value,
            #                                 db_field_value,
            #                                 default_field_value,
            #                                 is_default,
            #                                 change_count,
            #                             )
            #                 )
            #     # if is_default != 1 and change_count > 0:
            #     #     break
            #
            # # dont store copies that are just the default
            # if is_default == 1 and db_record_exists is True:
            #     # DELETE
            #     user_costs_obj.delete()
            #
            # if is_default != 1 and change_count > 0:
            #     # UPDATE
            #     if user_costs_obj is not None:
            #         user_costs_obj.cost_source = form_costs['cost_source']
            #         user_costs_obj.user_input_cost = form_costs['user_input_cost']
            #         user_costs_obj.base_year = form_costs['base_year']
            #         user_costs_obj.replacement_life = form_costs['replacement_life']
            #         user_costs_obj.o_and_m_pct = form_costs['o_and_m_pct']
            #
            #         if user_costs_obj.cost_source != 'user':
            #             user_costs_obj.user_input_cost = None
            #             user_costs_obj.base_year = None
            #         else:
            #             pass
            #
            #         user_costs_obj.save()
            #
            #     else:
            #         # CREATE
            #         costitem = CostItem.objects.filter(code=cost_item).first()
            #
            #         # print("create cost_item {}".format(cost_item))
            #         c = ScenarioCostItemUserCosts(
            #             scenario=self,
            #             costitem=costitem,
            #             cost_source=form_costs['cost_source'],
            #             user_input_cost=form_costs['user_input_cost'],
            #             base_year=form_costs['base_year'],
            #             replacement_life=form_costs['replacement_life'],
            #             o_and_m_pct=form_costs['o_and_m_pct'],
            #         )
            #         c.save()

        return

    # @sql_query_debugger
    def get_costs(self):
        """

            generate the cost from database content

        """
        cost_items_dict = {}
        cost_items = CostItem.objects\
            .all().order_by('sort_nu')
        for cost_item in cost_items:
            cost_items_dict[cost_item.code] = {'code': cost_item.code,
                                               'name': cost_item.name,
                                               'units': cost_item.units}

        cost_item_default_equations = CostItemDefaultEquations.objects\
            .select_related('costitem')\
            .all().order_by('costitem__sort_nu')
        for obj in cost_item_default_equations:
            costitem_code = obj.costitem.code
            cost_items_dict[costitem_code]['equation'] = obj.equation_tx

        result = {}

        structures = Structures.objects\
            .all().order_by('sort_nu')

        # these are the scenario structures
        scenario_structures = ScenarioStructure.objects\
            .select_related('scenario', 'structure')\
            .filter(scenario=self, is_checked=True)

        # queryset = ScenarioCostItemUserCosts.objects\
        #     .select_related('costitem', 'scenario', 'scenario__project',
        #                     'scenario__project__user', 'scenario__project__user__profile',
        #                     'default_cost') \
        #     .only(
        #         'costitem__code', 'costitem__name', 'costitem__sort_nu', 'costitem__units',
        #         'scenario__scenario_title',
        #         'scenario__project__project_title',
        #         'scenario__project__user__name', 'scenario__project__user__organization_tx',
        #         'scenario__project__user__profile__user_type',
        #         'default_cost__cost_type', 'default_cost__valid_start_date_tx',
        #         'default_cost__value_numeric', 'default_cost__value_numeric_currency',
        #         'replacement_life', 'o_and_m_pct', 'user_input_cost', 'user_input_cost_currency',
        #         'base_year', 'cost_source',
        #     ) \
        #     .all().order_by("costitem__sort_nu")

        costitem_default_costs = CostItemDefaultCosts.objects \
            .select_related('costitem') \
            .only(
                'costitem__code', 'costitem__name', 'costitem__sort_nu', 'costitem__units',
                'cost_type', 'valid_start_date_tx',
                'value_numeric', 'value_numeric_currency',
            )\
            .all().order_by('costitem__sort_nu')

        scenario_cost_item_costs = ScenarioCostItemUserCosts.objects \
            .select_related('costitem',
                            'default_cost') \
            .only(
                'costitem__code', 'costitem__name', 'costitem__sort_nu', 'costitem__units',
                # 'scenario__scenario_title',
                # 'scenario__project__project_title',
                # 'scenario__project__user__name', 'scenario__project__user__organization_tx',
                # 'scenario__project__user__profile__user_type',
                'default_cost__cost_type', 'default_cost__valid_start_date_tx',
                'default_cost__value_numeric', 'default_cost__value_numeric_currency',
                'replacement_life', 'o_and_m_pct', 'user_input_cost', 'user_input_cost_currency',
                'base_year', 'cost_source',
            ) \
            .filter(scenario=self).order_by('costitem__sort_nu')

        # testing using RelatedManager .all()
        # cost_item_user_costs = self.cost_item_user_costs.all()

        # build up the costs dictionaries
        # first add in the cost_item_user_costs

        costs = {}

        for scenario_cost_item_costs_obj in scenario_cost_item_costs:
            costitem_code = scenario_cost_item_costs_obj.costitem.code
            unit_cost = None
            if scenario_cost_item_costs_obj.user_input_cost is not None:
                # note: this is a Money field
                unit_cost = scenario_cost_item_costs_obj.user_input_cost.amount
            elif scenario_cost_item_costs_obj.default_cost is not None:
                unit_cost = scenario_cost_item_costs_obj.default_cost.value_numeric.amount

            cost_source = scenario_cost_item_costs_obj.cost_source
            if cost_source == 'user':
                if scenario_cost_item_costs_obj.user_input_cost is not None:
                    # note: this is a Money field
                    unit_cost = scenario_cost_item_costs_obj.user_input_cost.amount

            if costitem_code not in costs:
                costs[costitem_code] = {'cost_source': cost_source,
                                        'unit_cost': unit_cost,
                                        'units': cost_items_dict[costitem_code]['units'],
                                        'replacement_life': scenario_cost_item_costs_obj.replacement_life,
                                        'o_and_m_pct': scenario_cost_item_costs_obj.o_and_m_pct,
                                        }
            else:
                if cost_source == 'user':
                    costs[costitem_code]['unit_cost'] = unit_cost
                    costs[costitem_code]['units'] = cost_items_dict[costitem_code]['units']

                costs[costitem_code]['cost_source'] = cost_source

        # then add in the default costs to update the non 'user' (cost_source) costs
        for costitem_default_cost in costitem_default_costs:
            costitem_code = costitem_default_cost.costitem.code

            default_equations_objs = [x for x in cost_item_default_equations if x.costitem.code == costitem_code]
            if default_equations_objs is not None and len(default_equations_objs) > 0:
                default_equations_obj = default_equations_objs[0]

                costitem_default_cost.replacement_life = default_equations_obj.replacement_life
                costitem_default_cost.o_and_m_pct = default_equations_obj.o_and_m_pct
            else:
                costitem_default_cost.replacement_life = -77
                costitem_default_cost.o_and_m_pct = -76

            if costitem_code in costs:
                if costs[costitem_code]['cost_source'] != 'user':
                    # cost_source = costs[costitem_code]['cost_source']

                    unit_cost = None
                    if costs[costitem_code]['unit_cost'] is not None:
                        unit_cost = costs[costitem_code]['unit_cost']

                    costs[costitem_code]['unit_cost'] = unit_cost
                    costs[costitem_code]['units'] = cost_items_dict[costitem_code]['units']
            else:
                costs[costitem_code] = {'cost_source': str(costitem_default_cost.id),
                                        'unit_cost': costitem_default_cost.value_numeric.amount,
                                        'units': cost_items_dict[costitem_code]['units'],
                                        'o_and_m_pct': costitem_default_cost.o_and_m_pct,
                                        'replacement_life': costitem_default_cost.replacement_life,
                                        }

        # prepare the cost item user assumptions - which are per structure per cost item
        costitem_user_factors = self.cost_item_user_assumptions\
            .select_related('costitem', 'structure')\
            .all().order_by('costitem__sort_nu')

        user_assumptions = {}
        for user_factor in costitem_user_factors:
            if user_factor.structure.code not in user_assumptions:
                user_assumptions[user_factor.structure.code] = {}
            user_assumptions[user_factor.structure.code][user_factor.costitem.code] = user_factor

        # if the user has not made any edits to the default user assumptions, you need to get the
        # assumptions from that model
        costitem_default_factors = StructureCostItemDefaultFactors.objects \
            .select_related('costitem', 'structure') \
            .all()
        for default_factor in costitem_default_factors:
            if default_factor.structure.code not in user_assumptions:
                # the defaults are by definition checked
                default_factor.checked = True
                user_assumptions[default_factor.structure.code] = {}
                user_assumptions[default_factor.structure.code][
                    default_factor.costitem.code] = default_factor
            # added to try and fix single only cost item on all but first result structure
            elif default_factor.costitem.code not in user_assumptions[default_factor.structure.code]:
                default_factor.checked = True
                user_assumptions[default_factor.structure.code][
                    default_factor.costitem.code] = default_factor
        result['nonconventional'] = {'sum_value': 0, 'structures': {}}
        result['conventional'] = {'sum_value': 0, 'structures': {}}

        # this is used to compute 'Total PV of Annual O&M Costs' o_and_m costs, Present Value
        study_life = self.study_life

        # dictionary (should be a set) to record which cost items are used
        # in the final results.  later used to remove cost item unit costs if they are not used
        cost_items_seen = set()

        # these are 'Scenario' level values set on the 'Project-Scenario Description' page
        planning_and_design_factor = int(self.planning_and_design_factor) if self.planning_and_design_factor else 0
        study_life = int(self.study_life) if self.study_life else 0
        discount_rate = float(self.discount_rate) if self.discount_rate else 0

        for scenario_structure in scenario_structures:
            structure = None
            # is_checked = scenario_structure.is_checked
            area_value = scenario_structure.area

            for s in structures:
                if s == scenario_structure.structure:
                    structure = s
                    continue

            structure.area = area_value

            structure_code = structure.code

            sum_value = 0

            if structure_code not in user_assumptions:
                continue

            cost_results = {}

            for costitem_code in user_assumptions[structure_code]:

                cost_item = user_assumptions[structure_code][costitem_code]

                if cost_item.checked is not True:
                    continue

                # record that you have seen this
                cost_items_seen.add(costitem_code)

                cost_results[costitem_code] = {}

                assumptions = {
                    'units': cost_items_dict[costitem_code]['units'],
                    'name': cost_items_dict[costitem_code]['name'],
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
                results['equation'] = equation

                equation = equation.replace('=', '')
                equation = equation.replace('x', '(' + str(structure.area) + '*' + str(unit_conversion) + ')')
                equation = equation.replace('area', assumptions['a_area'])
                equation = equation.replace('depth', assumptions['z_depth'])
                equation = equation.replace('density', assumptions['d_density'])
                equation = equation.replace('number', assumptions['n_number'])
                equation = equation.replace('$', str(costs[costitem_code]['unit_cost']))

                results['equation_calc'] = equation

                cost_results[costitem_code]['results'] = results

                try:
                    cost_amount = eval(equation)
                    cost_amount = round(cost_amount, 0)
                    sum_value += cost_amount
                    results['value'] = '{:,.0f}'.format(cost_amount)
                    results['value_unformatted'] = cost_amount
                except:
                    cost_amount = equation
                    results['value'] = cost_amount
                    results['value_unformatted'] = 0  # added to try and fix unhandled key error

                results['equation'] = results['equation'].replace('area', 'a')
                results['equation'] = results['equation'].replace('depth', 'z')
                results['equation'] = results['equation'].replace('density', 'd')
                results['equation'] = results['equation'].replace('number', '#')
                if 'a' not in results['equation']:
                    assumptions['a_area'] = ''
                if 'z' not in results['equation']:
                    assumptions['z_depth'] = ''
                if 'd' not in results['equation']:
                    assumptions['d_density'] = ''
                if '#' not in results['equation']:
                    assumptions['n_number'] = ''

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
                    'sum_value': '${:,.0f}'.format(round(sum_value, 0))
                },
                'cost_data': cost_results
            }

        total_construction_cost = 0
        for classification in result:
            result[classification]['sum_value'] = round(result[classification]['sum_value'], 0)
            total_construction_cost += result[classification]['sum_value']

        """
             make calculation from post-construction costs

             I think the way to do it is to find all 'data' that where checked == true
             and then replace all the components of the equation as strings and then eval it
        """
        total_o_and_m_cost = 0
        total_replacement_cost = 0

        """
            these are 'Structure' level values for each 'Cost Item' add the costs for each cost item
        """
        project_life_cycle_costs = {'total': {},
                                    'conventional': {},
                                    'nonconventional': {},
                                    }
        structure_life_cycle_costs = {}
        for classification in result:

            project_life_cycle_costs[classification] = {
                'meta': {
                    'name': ('Conventional' if classification == 'conventional' else 'Non-Conventional (GSI)')
                },
                'costs': {
                    'sum': 0,
                    'construction': 0,
                    'planning_and_design': 0,
                    'o_and_m': 0,
                    'replacement': 0,
                }
            }

            structure_life_cycle_costs[classification] = {
                'meta': {
                    'name': ('Conventional' if classification == 'conventional' else 'Non-Conventional') +
                            ' (GSI) Structures',
                },
                'costs': {
                    'sum': 0,
                    'construction': 0,
                    'planning_and_design': 0,
                    'o_and_m_sum': 0,
                    'replacement_sum': 0,
                },
                'structures': {}
            }

            for structure_code in result[classification]['structures']:
                # if 'structures' not in structure_life_cycle_costs[classification]:
                #     structure_life_cycle_costs[classification]['structures'] = {}

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
                        'o_and_m_sum': 0,
                        'replacement_sum': 0,
                    }
                }

                for costitem_code in result[classification]['structures'][structure_code]['cost_data']:

                    costs_sum = 0

                    if 'cost_items' not in structure_life_cycle_costs[classification]['structures'][structure_code]:
                        structure_life_cycle_costs[classification]['structures'][structure_code]['cost_items'] = {}

                    structure_life_cycle_costs[classification]['structures'][structure_code]['cost_items'][
                        costitem_code] = {'costs': {}}

                    # this has useful labels and size of structures
                    cost_item_data = result[classification]['structures'][structure_code]['cost_data'][costitem_code]

                    construction_cost = cost_item_data['results']['value_unformatted']
                    planning_and_design_costs = round(construction_cost * planning_and_design_factor * 0.01, 0)

                    # TODO - figure out why these 2 values are being added to Project Life Cycle costs twice
                    costs_sum += construction_cost + planning_and_design_costs

                    replacement_life = cost_item_data['costs']['replacement_life']
                    o_and_m_pct = cost_item_data['costs']['o_and_m_pct']

                    # =(G$116*(G$115/100))/(1+($D$13/100))^$C120
                    # = (construction_cost * (o_and_m_pct/100)) / (1 + (discount_rate/100))^i
                    o_and_m_costs = 0
                    if o_and_m_pct != 0:
                        for i in range(1, study_life + 1, 1):
                            o_and_m_costs += (construction_cost * (o_and_m_pct / 100)) / (
                                    1 + (discount_rate / 100)) ** i

                    number_of_replacements = 0
                    if replacement_life != 0 and study_life > replacement_life:
                        number_of_replacements = int(round(study_life / replacement_life, 0))

                    value_of_first_replacement = 0
                    replacement_years = []
                    replacement_costs = 0

                    if number_of_replacements > 0:
                        for i in range(replacement_life, study_life + 1, replacement_life):
                            replacement_years.append(i)
                            replacement_cost = round(construction_cost / (1 + (discount_rate / 100)) ** i, 0)
                            replacement_costs += replacement_cost
                            if value_of_first_replacement == 0:
                                value_of_first_replacement = replacement_costs

                    o_and_m_costs = round(o_and_m_costs, 0)
                    replacement_costs = round(replacement_costs, 0)

                    total_o_and_m_cost += o_and_m_costs
                    total_replacement_cost += replacement_costs

                    costs_sum += o_and_m_costs + replacement_costs

                    # add to structure costs
                    project_costs = project_life_cycle_costs[classification]['costs']
                    classification_costs = structure_life_cycle_costs[classification]['costs']

                    structure_costs = structure_life_cycle_costs[classification]['structures'][structure_code]['costs']

                    structure_costs['sum'] += costs_sum
                    structure_costs['o_and_m_sum'] += o_and_m_costs
                    structure_costs['replacement_sum'] += replacement_costs

                    # add to classification costs
                    project_costs['construction'] += construction_cost
                    project_costs['planning_and_design'] += planning_and_design_costs

                    classification_costs['construction'] += construction_cost
                    classification_costs['planning_and_design'] += planning_and_design_costs

                    project_costs['o_and_m'] += o_and_m_costs
                    classification_costs['o_and_m_sum'] += o_and_m_costs

                    project_costs['replacement'] += replacement_costs
                    classification_costs['replacement_sum'] += replacement_costs

                    """
                        this is awful.  sorry.
                    """
                    project_costs['sum'] += costs_sum

                    classification_costs['sum'] += costs_sum

                    structure_life_cycle_costs[classification]['structures'][structure_code]['cost_items'][
                        costitem_code] = {
                        'meta': {
                            'name': cost_item_data['assumptions']['name'],
                            'units': cost_item_data['assumptions']['units'],
                        },
                        'costs': {
                            'construction': construction_cost,
                            'planning_and_design': planning_and_design_costs,
                            'o_and_m': round(o_and_m_costs, 0),
                            'replacement': round(replacement_costs, 0),
                            'first_replacement': value_of_first_replacement,
                            'replacement_years': replacement_years,
                        }
                    }

        project_life_cycle_costs['total'] = {
            'construction': total_construction_cost,
            'planning_and_design': round(total_construction_cost * (planning_and_design_factor / 100), 0),
            'o_and_m': total_o_and_m_cost,
            'replacement': total_replacement_cost,
        }

        total = 0
        for cost in project_life_cycle_costs['total']:
            total += project_life_cycle_costs['total'][cost]
        project_life_cycle_costs['total']['sum'] = total

        result['project_life_cycle_costs'] = project_life_cycle_costs
        result['structure_life_cycle_costs'] = structure_life_cycle_costs

        return result


class ScenarioCostItemUserCosts(models.Model):
    """

     this stores the 'scenario' values for the costitem costs.
     each row is attached to one CostItem for one Scenario

    """
    scenario = models.ForeignKey(Scenario, related_name="cost_item_user_costs",
                                 on_delete=models.CASCADE, default=None, blank=False, null=False)
    costitem = models.ForeignKey(CostItem,
                                 on_delete=models.CASCADE, default=None, blank=False, null=False)

    # region new storage
    """ if this is null, then there is a 'User' input cost, 
    else it is one of the default costs created by an administrator 
    
    TODO this should be costitem_default_cost
    """
    default_cost = models.ForeignKey(CostItemDefaultCosts, on_delete=models.DO_NOTHING,
                                     default=None, blank=True, null=True)

    created_date = models.DateTimeField('Create Date', null=True, auto_now_add=True)
    modified_date = models.DateTimeField('Modified Date', auto_now=True)
    # endregion new storage

    # region old storage
    COST_SOURCE_VALUES = ('rsmeans', 'db_25_pct', 'db_50_pct', 'db_75_pct')
    COST_SOURCE_TEXTS = ('Eng. Est.', 'DB - 25%', 'DB - 50%', 'DB - 75%')
    COST_SOURCE_CHOICES = zip(COST_SOURCE_VALUES, COST_SOURCE_TEXTS)

    cost_source = models.CharField("Source of user_input_cost", choices=COST_SOURCE_CHOICES,
                                   unique=False, max_length=24,
                                   default=None, blank=False, null=False)
    # endregion old storage


    base_year = models.PositiveIntegerField(validators=[MinValueValidator(2018),
                                                                      MaxValueValidator(2090)
                                                                      ], blank=True, null=True)
    user_input_cost = MoneyField('User supplied unit cost', decimal_places=2, max_digits=11,
                                 default_currency='USD', blank=True, null=True)


    replacement_life = models.PositiveIntegerField("Replacement Life ('R')",
                                                   default=40, validators=[MinValueValidator(0),
                                                                           MaxValueValidator(100)
                                                                           ], blank=True, null=True)
    o_and_m_pct = models.PositiveIntegerField("Ongoing Operations and Maintenance Factor (%)",
                                              default=0,
                                              validators=[MinValueValidator(0),
                                                          MaxValueValidator(100)
                                                          ],
                                              blank=True, null=True)

    # DEPRECIATED - this is not used in the UI/UX or anywhere else
    first_year_maintenance = MoneyField('User supplied First Year Maintenance Cost', decimal_places=2, max_digits=11,
                                        default_currency='USD', blank=True, null=True)

    def __str__(self):
        return self.scenario.scenario_title + " -- " + self.costitem.code + " -- " + self.cost_source

    class Meta:
        verbose_name_plural = "Scenario Cost Item User Costs"
        unique_together = ("scenario", "costitem")


class ScenarioArealFeature(models.Model):
    """
        2022-01-13 - this is the new storage for the users Areal Feature information

        this is a User Data Table of what Areal Feature Area and on/off values are selected for
        each Scenario

    """
    scenario = models.ForeignKey(Scenario, related_name="scenario_areal_feature", on_delete=models.CASCADE,
                                 default=None, blank=False, null=False)
    areal_feature = models.ForeignKey(ArealFeatureLookup, on_delete=models.CASCADE,
                                  default=None, blank=False, null=False)

    area = models.IntegerField("Area", default=0, blank=True, null=True)
    is_checked = models.BooleanField("Is Checked", default=False, blank=True, null=True)

    def __str__(self):
        return self.scenario.scenario_title + ' - ' + self.areal_feature.name

    class Meta:
        verbose_name_plural = "Scenario Areal Features"
        unique_together = ("scenario", 'areal_feature',)


class ScenarioStructure(models.Model):
    """
        2022-01-11 - this is a proposed storage mechanism for the users structure information
           that is currently stored in  ConventionalStructures and NonConventionalStructures
           This is being considered because the 2 existing tables have hardwired contents
           and there is no way anyone could easily expand or alter what are considered Structures
           in the future.

           If this works, then the 2 tables ConventionalStructures and NonConventionalStructures will
           be removed.

        this is a User Data Table of what Structure Area and on/off values are selected for
        each Scenario

    """
    scenario = models.ForeignKey(Scenario, related_name="scenario_structure", on_delete=models.CASCADE,
                                 default=None, blank=False, null=False)
    structure = models.ForeignKey(Structures, on_delete=models.CASCADE,
                                  default=None, blank=False, null=False)

    area = models.IntegerField("Area", default=0, blank=True, null=True)
    is_checked = models.BooleanField("Is Checked", default=False, blank=True, null=True)

    def __str__(self):
        return self.scenario.scenario_title + ' - ' + self.structure.name

    class Meta:
        verbose_name_plural = "Scenario Structures"
        unique_together = ("scenario", 'structure',)


class StructureCostItemUserFactors(models.Model):
    """
        This is connected to the Structure Costs page
        and stores data by (project/)scenario/structure/costitem

        the 'user' factors are stored here

        This might be called ScenarioStructureCostItemUserFactors
    """
    scenario = models.ForeignKey(Scenario, related_name="cost_item_user_assumptions", on_delete=models.CASCADE,
                                 default=None, blank=False, null=False)
    structure = models.ForeignKey(Structures, on_delete=models.CASCADE, default=None, blank=False, null=False)
    costitem = models.ForeignKey(CostItem, on_delete=models.CASCADE, default=None, blank=False, null=False)

    checked = models.BooleanField("Is Checked", default=None, null=True)

    a_area = models.CharField("Area (a)", max_length=10, default=None, blank=True, null=True)
    z_depth = models.CharField("Depth (z)", max_length=10, default=None, blank=True, null=True)
    d_density = models.CharField("Density (d)", max_length=10, default=None, blank=True, null=True)
    n_number = models.CharField("Count (n)", max_length=10, default=None, blank=True, null=True)

    def __str__(self):
        return str(self.scenario.scenario_title) + " -- " + self.structure.name + " -- " + self.costitem.name

    class Meta:
        verbose_name = "Scenario Structure Cost Item User Factors"
        verbose_name_plural = "Scenario Structure Cost Item User Factors"
        unique_together = ("scenario", 'structure', "costitem")

