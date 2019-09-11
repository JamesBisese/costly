TEMPLATE_SCENARIO = {
    "scenario_id": "",
    'source': "TEMPLATE_SCENARIO",
    "siteData": {
        "version": "1.1",

        "project": {
            "fields": [
                "project_title",
                # "scenario_title",
                "project_type",
                "project_ownership",
                'project_location',
                'project_purchase_information',
                'priority_watershed',
                "project_area",
                "land_unit_cost"
            ]
        },
        "embedded_scenario": {
            "fields": [
                "scenario_title",
                "nutrient_req_met",
                "captures_90pct_storm",
                "meets_peakflow_req",
                "pervious_area",
                "impervious_area",
                "planning_and_design_factor",
                "study_life",
                "discount_rate",
            ]
        },
        "areal_features": {
            "fields": [
                'stormwater_management_feature',
                'amenity_plaza',
                'protective_yard',
                'parking_island',
                'building',
                'drive_thru_facility',
                'landscape',
                'sidewalk',
                'street',
                'median',
                'parking_lot',
                'driveway_and_alley',
            ],
            "labels": {
                'stormwater_management_feature': 'Stormwater Management Feature',
                'amenity_plaza': 'Amenity Plaza',
                'protective_yard': 'Protective Yard',
                'parking_island': 'Parking Island',
                'building': 'Building',
                'drive_thru_facility': 'Drive-Thru Facility',
                'landscape': 'Miscellaneous Landscaping/Open Space',
                'sidewalk': 'Sidewalk',
                'street': 'Street',
                'median': 'Median',
                'parking_lot': 'Parking Lot',
                'driveway_and_alley': 'Driveway and Alley',
            },
            "toggles": [
                {'name': 'stormwater_management_feature', 'is_parcel': True, 'is_row': True, 'is_public': True,'is_private': True},
                {'name': 'amenity_plaza', 'is_parcel': True, 'is_row': False, 'is_public': True, 'is_private': True},
                {'name': 'protective_yard', 'is_parcel': True, 'is_row': True, 'is_public': True, 'is_private': True},
                {'name': 'parking_island', 'is_parcel': True, 'is_row': False, 'is_public': True, 'is_private': True},
                {'name': 'building', 'is_parcel': True, 'is_row': False, 'is_public': True, 'is_private': True},
                {'name': 'drive_thru_facility', 'is_parcel': True, 'is_row': False, 'is_public': True, 'is_private': True},
                {'name': 'landscape', 'is_parcel': False, 'is_row': True, 'is_public': True, 'is_private': True},
                {'name': 'sidewalk', 'is_parcel': True, 'is_row': True, 'is_public': True, 'is_private': True},
                {'name': 'street', 'is_parcel': False, 'is_row': True, 'is_public': True, 'is_private': True},
                {'name': 'median', 'is_parcel': False, 'is_row': True, 'is_public': True, 'is_private': True},
                {'name': 'parking_lot', 'is_parcel': True, 'is_row': False, 'is_public': True, 'is_private': True},
                {'name': 'driveway_and_alley', 'is_parcel': True, 'is_row': True, 'is_public': True, 'is_private': True}
            ],
            "inputs": {
                "stormwater_management_feature": ['checkbox', 'area'],
                'amenity_plaza': ['checkbox', 'area'],
                'protective_yard': ['checkbox', 'area'],
                'parking_island': ['checkbox', 'area'],
                'building': ['checkbox', 'area'],
                'drive_thru_facility': ['checkbox', 'area'],
                'landscape': ['checkbox', 'area'],
                'sidewalk': ['checkbox', 'area'],
                'street': ['checkbox', 'area'],
                'median': ['checkbox', 'area'],
                'parking_lot': ['checkbox', 'area'],
                'driveway_and_alley': ['checkbox', 'area']
            }
        },
        "conventional_structures": {
            "fields": [
                "stormwater_wetland",
                'pond',
                'rooftop',
                'asphalt',
                'concrete',
                'lawn',
                'landscaping',
                'trench',
                'curb_and_gutter',
            ],
            "labels": {
                'stormwater_wetland': 'Stormwater Wetland',
                'pond': 'Wet/Dry Pond',
                'rooftop': 'Rooftop',
                'asphalt': 'Asphalt Pavement',
                'concrete': 'Concrete Paving Surfaces',
                'lawn': 'Lawn, Shrubs, and Tree plantings',
                'landscaping': 'Managed Open Space',
                'trench': 'Infiltration Trench',
                'curb_and_gutter': "Curb and Gutter",
            },
            "inputs": {
                "stormwater_wetland": ['checkbox', 'area'],
                'pond': ['checkbox', 'area'],
                'rooftop': ['checkbox', 'area'],
                'asphalt': ['checkbox', 'area'],
                'concrete': ['checkbox', 'area'],
                'lawn': ['checkbox', 'area'],
                'landscaping': ['checkbox', 'area'],
                'trench': ['checkbox', 'area'],
                'curb_and_gutter': ['checkbox', 'area'],
            }
        },
        "nonconventional_structures": {
            "fields": [
                'swale',
                'rain_harvesting_device',
                'bioretention_cell',
                'filter_strip',
                'green_roof',
                'planter_box',
                'porous_pavement'
            ],
            "labels": {
                'swale': 'Swale',
                'rain_harvesting_device': 'Rain Harvesting Device',
                'bioretention_cell': 'Bioretention Cell',
                'filter_strip': 'Filter Strip',
                'green_roof': 'Green Roof',
                'planter_box': 'Planter Box',
                'porous_pavement': 'Permeable Pavement',
            },
            "inputs": {
                'swale': ['checkbox', 'area'],
                'rain_harvesting_device': ['checkbox', 'area'],
                'bioretention_cell': ['checkbox', 'area'],
                'filter_strip': ['checkbox', 'area'],
                'green_roof': ['checkbox', 'area'],
                'planter_box': ['checkbox', 'area'],
                'porous_pavement': ['checkbox', 'area']
            }
        },
        "cost_items": {
            "fields": []

        }

    }
}


# when a user CREATES a new scenario, this is loaded
DEFAULT_SCENARIO = {
    # there is another key 'scenario_id' not included in the default
    'zany_thing': "called right about now",
    "siteData": {
        "version": "1.1",
        "location": {
            'please': 'remove this stupid thng',
            "project_title": "Test Load Project Title",
            "scenario_title": "Test Load Scenario Title",
            "project_type": "parcel",
            "project_ownership": "public",
            "project_area": "12008",
            "land_unit_cost": "108",


            'project_location': '10123 W Cherokee Dr.',
            'project_purchase_information': 'to_be_purchased',
            'priority_watershed': 'no',


            'nutrient_req_met': 'without_buy_down',
            'captures_90pct_storm': 'yes',
            'meets_peakflow_req': 'no',

            "planning_and_design_factor": '20',
            "study_life": '40',
            "discount_rate": '2.875',
        },
        "project": {
            "project_title": "Test Load Project Title",
            "scenario_title": "Test Load Scenario Title",
            "project_type": "parcel",
            "project_ownership": "public",
            "project_area": "12008",
            "land_unit_cost": "108",

            'project_location': '10123 W Cherokee Dr.',
            'project_purchase_information': 'to_be_purchased',
            'priority_watershed': 'no',
        },
        "embedded_scenario": {
            "scenario_title": "Test Load Scenario Title",

            'nutrient_req_met': 'without_buy_down',
            'captures_90pct_storm': 'yes',
            'meets_peakflow_req': 'no',

            'pervious_area': 0,
            'impervious_area': 0,
        },
        "areal_features": {
            "stormwater_management_feature": {
                "checkbox": True,
                "area": 1000
            },
            "amenity_plaza": {
                "checkbox": True,
                "area": 1001
            },
            "protective_yard": {
                "checkbox": True,
                "area": 1002
            },
            "parking_island": {
                "checkbox": True,
                "area": 1003
            },
            "building": {
                "checkbox": True,
                "area": 1004
            },
            "drive_thru_facility": {
                "checkbox": True,
                "area": 1005
            },
            "landscape": {
                "checkbox": True,
                "area": 1006
            },
            "sidewalk": {
                "checkbox": True,
                "area": 1007
            },
            "street": {
                "checkbox": True,
                "area": 1008
            },
            "median": {
                "checkbox": True,
                "area": 1009
            },
            "parking_lot": {
                "checkbox": True,
                "area": 1010
            },
            "driveway_and_alley": {
                "checkbox": True,
                "area": 1011
            }
        },
        "conventional_structures": {
            "stormwater_wetland": {
                "checkbox": True,
                "area": 2000
            },
            "pond": {
                "checkbox": True,
                "area": 2001
            },
            "rooftop": {
                "checkbox": True,
                "area": 2002
            },
            # "piping": {
            #     "checkbox": True,
            #     "length": 1000,
            #     "diameter": 6
            # },
            "curb_and_gutter": {
                "checkbox": False,
                "area": 2003
            },
            "asphalt": {
                "checkbox": False,
                "area": 2003
            },
            "concrete": {
                "checkbox": True,
                "area": 2004
            },
            "lawn": {
                "checkbox": False,
                "area": ""
            },
            "landscaping": {
                "checkbox": True,
                "area": 2005
            },
            "trench": {
                "checkbox": True,
                "area": 2006
            }
        },
        "nonconventional_structures": {
            "swale": {
                "checkbox": True,
                "area": 3000
            },
            "rain_harvesting_device": {
                "checkbox": True,
                "area": 3001
            },
            "bioretention_cell": {
                "checkbox": True,
                "area": 3002
            },
            "filter_strip": {
                "checkbox": True,
                "area": 3003
            },
            "green_roof": {
                "checkbox": False,
                "area": 3004
            },
            "planter_box": {
                "checkbox": True,
                "area": 3005
            },
            "porous_pavement": {
                "checkbox": True,
                "area": 3006
            }
        }
    }
}