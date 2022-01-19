TEMPLATE_SCENARIO = {
    "scenario_id": "",
    'source': "TEMPLATE_SCENARIO",
    "siteData": {
        "version": "1.3",
        "project": {
            "fields": [
                "project_title",
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
        }
    }
}
