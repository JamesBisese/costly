//TODO - what does this mean????
// this is populated one time via an ajax call
// it has triggering logic for various elements
var _scenario_template = null;

/********************************
*
* Initialize document
*
* all URLs are defined with variables ending in '_url'
* all ajax calls are to URLs defined in the javascript file urls.js which is
*  responsible for toggling the correct url between development and production installations
*
 */

/* for Mozilla */
if (document.addEventListener) {
    document.addEventListener("DOMContentLoaded", init, null);
}

window.onload = init;

function init() {
    // quit if this function has already been called
    if (arguments.callee.done) {
        return;
    }
    // flag this function so we don't do the same thing twice
    arguments.callee.done = true;

    // set field restrictions (i.e. numbers only) on fields
    setAllFieldInputFilters();
    var scenario_id = null;

    var inputDom = document.getElementById('ui_' + 'scenario_id');

    if (inputDom){
        scenario_id = inputDom.value;
    }

    var url = '';

    // if there is a scenario_id (this is opened as an update) use the API url
    if (scenario_id !== null && scenario_id != '')
    {
        url = SETTINGS.URLS.scenario_api.replace('<int:pk>', scenario_id);
    }
    else // create a new scenario and load with the default data
    {
        url = SETTINGS.URLS.scenario_default;
    }

    $.ajax(url, {
        contentType : 'application/json; charset=utf-8',
        type : 'GET',
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: function (data) {
            // uses the data in the JSON object to populate the UI when the scenario is first opened
            populateUI(data);

            initializeForm();
        },
        error: function(data) {
            showError(data);
        }
    });

    //document.getElementById("uploadFile").addEventListener("change", loadJSON, false);
}


/**********************************************************
*
* Populates the UI with the values in the JSON object
*
*
*/
function populateUI(siteData) {

    if (! siteData) return;



    function updateField(field_dict)
    {
        //TODO: make it safe if the field isn't found
        for (key in field_dict){
            value = field_dict[key];

            var update_field = document.getElementById('ui_' + key);
            if (update_field) {
                update_field.value = value;
            }
        }
    }

    function updateStructures(field_dict)
    {
        var checkbox_value;

        //TODO:
        for (var field_name in field_dict){
            var field_object = field_dict[field_name];

            if ('checkbox' in field_object){
                checkbox_value = field_object['checkbox'];
            }

            // each one has a checkbox_, and one or more _area, _length, _diameter)
            for (var propt in field_object){
                var subfield_name = propt;
                var value_name = field_object[propt];

                if (subfield_name == 'checkbox'){
                    var buttonDom = document.getElementById('checkbox_' + field_name);
                    if (buttonDom){
                        buttonDom.checked = value_name;
                    }
                }
                else {
                    var inputDom = document.getElementById('ui_' + field_name + '_' + subfield_name);
                    if (inputDom){
                        inputDom.value = value_name;
                        if (checkbox_value !== true)
                        {
                            inputDom.disabled = true;
                            inputDom.style.textDecoration = 'line-through';
                        }
                        else
                        {
                            inputDom.disabled = false;
                            inputDom.style.textDecoration = 'none';
                        }
                    }
                }
            }
        }
    }
    /*
    *
    * this populates fields in the Cost Item / Unit Costs tab
    *
    *
     */
    function populateCosts(field_dict)
    {
        for (var i in field_dict){
            var field_object = field_dict[i];

            // each one has one or more 'area', 'unit_cost', 'replacement_life', 'first_year'
            cost_item_code = field_object['costitem_code'];
            field_list = ['user_input_cost',
                            'base_year',
                            'replacement_life',
                            'o_and_m_pct'];
            var inputDom = document.getElementById('ui_' + cost_item_code + '_' + 'cost_source');
            if (inputDom){
                inputDom.value = field_object['cost_source'];
            }

            for (var j in field_list){
                var subfield_name = field_list[j];
                var value_name = field_object[subfield_name];

                var inputDom = document.getElementById('ui_' + cost_item_code + '_' + subfield_name);
                if (inputDom){
                    inputDom.value = value_name;
                }
            }
            var inputs = ['user_input_cost', 'base_year'];

            inputs.forEach(function(input_name) {
                var elementObj = document.getElementById('ui_' + cost_item_code + '_' + input_name);
                if (elementObj){
                    if (field_object['cost_source'] != 'user') {
                            elementObj.disabled = true;
                            elementObj.style.textDecoration = 'line-through';
                    }
                    else {
                        elementObj.disabled = false;
                        elementObj.style.textDecoration = 'none';
                    }
                }
            })
        }

    }



    //okay - this is crazy - but CREATE and UPDATE have different versions of siteData
    // CREATE uses the siteTemplate and UPDATE uses the API correctly

    if ('siteData' in siteData) {
        siteData = siteData['siteData'];
    }

    if ('location' in siteData)
    {
        updateField(siteData['location']);
    }
    else if ('embedded_scenario' in siteData)
    {
        updateField(siteData['embedded_scenario']);
    }

    var inputDom = document.getElementById('scenario_name');
    if (inputDom){
        updateProjectTitle(siteData);
    }

    updateStructures(siteData['areal_features']);

    updateStructures(siteData['conventional_structures']);

    updateStructures(siteData['nonconventional_structures']);

    //NOTE: Structure Costs are loaded as an partial HTML document
    //TODO: replace that function with normal loading

    populateCosts(siteData['cost_item_user_costs'])

    //TODO - the rest
}

/*
* this populates fields in the Structure/Cost Item Costs page
*
*
*/
function populateStructureEquations(data){

    //TODO
    var structure_name = data.structure.name;
    if (data.structure.area == null){
        data.structure.area = 0;
    }
    var area = data.structure.area;

    //list of all cost items for this structure
    var cost_items = data.data;

    var field_list = ['unit_cost',


                        'a_area',
                        'z_depth',
                        'd_density',
                        'n_number',

                        'equation',
                        'equation_value',
        ];

    var ui_field_list = ['user_input_cost_READONLY',

                        'a_area',
                        'z_depth',
                        'd_density',
                        'n_number',

                        'equation',
                        'cost_V1'

        ]

    var factor_field_list = [
                        'a_area',
                        'z_depth',
                        'd_density',
                        'n_number',
        ];
    var factor_equation_list = [
                        'area',
                        'depth',
                        'density',
                        'number',
        ];

    // set the field that shows what is selected and the area of
    var inputDom = document.getElementById('ui_structure_name_2');
    if (inputDom){
         inputDom.textContent = data.structure.name;
    }
    var inputDom = document.getElementById('ui_structure_area_2');
    if (inputDom){
         inputDom.value = data.structure.area.toLocaleString();
    }
    var inputDom = document.getElementById('ui_structure_units_2');
    if (inputDom){
         inputDom.innerHTML = data.structure.units;
    }

    // clear out the old input
    for (var cost_item in cost_items) {
        var inputDom = document.getElementById('checkbox_' + cost_item);
        if (inputDom){
             inputDom.checked = false;
        }
        for (var i in ui_field_list) {
            var ui_field_name = ui_field_list[i];

            var inputDom = document.getElementById('ui_' + cost_item + '_' + ui_field_name);
            if (inputDom){
                inputDom.value = '';
            }
        }
    }

    // load in the new values
    for (var cost_item in cost_items){
        var cost_item_data = cost_items[cost_item];
        // get the boolean for if it is checked or not
        var cost_item_checked = cost_item_data['checked'];
        // first set the checkbox
        var inputDom = document.getElementById('checkbox_' + cost_item);
        if (inputDom){
             inputDom.checked = cost_item_checked;
        }

        //hide the factor field if that factor is not in the equation
        var equation = cost_item_data['equation'];
        for (var f in factor_field_list)
        {
            var field_name = factor_field_list[f];
            var equation_factor_tx = factor_equation_list[f];
            var inputDom = document.getElementById('ui_' + cost_item + '_' + field_name);

            // hide or show depending on if the field is in the equation
            if (inputDom) {
                //boolean
                var show_input = equation.indexOf(equation_factor_tx) > 0;

                inputDom.style.display = show_input ? '' : 'none';
                inputDom.disabled = cost_item_checked ? false : true;
                inputDom.style.textDecoration = cost_item_checked ? '' : 'line-through';
            }

        }

        // now the 4 factor fields
        for (var i in field_list)
        {
            var field_name = field_list[i];

            var field_value = '';
            if (field_name in cost_item_data)
            {
                // this is the value put into the UI
                field_value = cost_item_data[field_name];
            }

            var ui_field_name = ui_field_list[i];

            var inputDom = document.getElementById('ui_' + cost_item + '_' + ui_field_name);
            if (inputDom){
                inputDom.value = field_value;

                if (field_name == 'equation'){
                    var title =  cost_item_data['equation_calc'];
                    if (title == undefined){
                        title = cost_item_data['equation'];
                    }
                    else {
                        title = '=' + title;
                    }
                    var text = document.createTextNode(field_value);
                    while (inputDom.firstChild) {
                      inputDom.removeChild(inputDom.firstChild);
                    }
                    // text.title = title;
                    inputDom.title = title;
                    inputDom.appendChild(text);
                }
                else if (field_name == 'equation_value'){

                    var text = document.createTextNode(field_value);
                    while (inputDom.firstChild) {
                      inputDom.removeChild(inputDom.firstChild);
                    }
                    inputDom.appendChild(text);

                }
                else if (field_name == 'unit_cost'){

                    var text = document.createTextNode(cost_item_data['unit_cost_formatted']);
                    while (inputDom.firstChild) {
                      inputDom.removeChild(inputDom.firstChild);
                    }
                    inputDom.appendChild(text);

                }
            }
        }

    }

    return;
}

// this runs after all widgets have had their data loaded
function initializeForm()
{
    validateProjectAreaAndArealFeatures(); // toggle disabled inputs, that are then not used in calculation

    var structure_select = document.getElementById('ui_structure_select');

    if (structure_select.length >= 1) {
        structure_select.selectedIndex = 1;
        loadStructureCosts();
    }


}

/*******************
*
* Insert the results (data) in the Results pane
*
*
*
 */
function updateResultsPane(data){

    var DivElement = document.getElementById('result-box');

    var contentTX = contentTX = JSON.stringify(data, null, 4);
    if(data.hasOwnProperty('DT_RowId')) // first loaded
    {
        contentTX = '<pre>' + JSON.stringify(data, null, 4) + '</pre>';
        // contentTX = 'TBD';
    }
    else if(data.hasOwnProperty('html_result')) // first loaded
    {
        contentTX = data['html_result'];
        // contentTX = 'TBD - return formatted via another ajax?? or just have the routine fiture that out';
    }
    else if(data.hasOwnProperty('error'))
    {
        contentTX = "There is an error in one of the tabs so the results cannot be computed";
    }
    else
    {
        contentTX = JSON.stringify(data, null, 4);
    }

    DivElement.innerHTML = contentTX;

}
function updateProjectTitle(siteData){
    var inputDom = document.getElementById('scenario_name');

    if (inputDom){
        var project_title = 'PROJECT TITLE';
        var scenario_title = 'SCENARIO TITLE';
        if(siteData.hasOwnProperty('project')) // first loaded
        {
            if (siteData['project'] !== undefined) {
                if (siteData['project']['project_title'] !== undefined) {
                    project_title = siteData['project']['project_title'];
                }
            }
            if (siteData['embedded_scenario'] !== undefined) {
                if (siteData['embedded_scenario']['scenario_title'] !== undefined) {
                    scenario_title = siteData['embedded_scenario']['scenario_title'];
                }
            }
            inputDom.innerHTML = project_title + ' -- ' + scenario_title;
        }
    }
}
function updateStructureCostDropDown(siteData){

    function compileStructureList(structures, prefix) {
        //
        var labels = structures['labels'];

        for (var structure in structures){

            if (structure == 'labels'){
                continue;
            }

            var structure_obj = structures[structure];

            if(structure == 'curb_and_gutter'){ // this one doesn't need an area
                structure_obj['area'] = undefined;
            }

            if (structure_obj['checkbox'] == true &&
                structure_obj['area'] != '' &&
                structure_obj['area'] != 0)
            {
                structure_list.push({ value: structure,
                                        text: prefix + ' - ' + labels[structure]});
            }
        }
    }

    var structure_select = document.getElementById('ui_structure_select');
    selected_value = structure_select.value;
    //zed
    structure_list = [];

    compileStructureList(siteData['nonconventional_structures'], 'Non-Conventional');
    compileStructureList(siteData['conventional_structures'], 'Conventional');

    //TODO: add them to the drop-down list
    structure_select.options.length = 0;
    for (var i = 0; i < structure_list.length; i++) {
        var o = document.createElement("option");
        o.value = structure_list[i].value;
        o.text = structure_list[i].text;
        structure_select.appendChild(o);
    }
    structure_select.value = selected_value;

    var structure_cost_tableDom = document.getElementById('structure_costs_table');
    structure_cost_tableDom.style.display = (structure_list.length > 0) ? '' : 'none';
}


/*

    enforce rule that the sum of all the Areal Features is not greater than the Total Project Area

 */
function validateProjectAreaAndArealFeatures() {
    //
    var sum_area_field = 'project_area';

    var sum_area = document.getElementById('ui_' + sum_area_field).value;

    var sum_areal_features = 0.0;
    var sum_pervious_impervious_area = 0.0;

    var scenario_template = scenarioTemplateJSON();
    var areal_features_fields = scenario_template['siteData']['areal_features']['fields'];

    for (var i in areal_features_fields){
        var areal_feature_name = areal_features_fields[i];
        var areal_feature_areaDom = document.getElementById('ui_' + areal_feature_name + '_area');
        var areal_feature_checkboxDom = document.getElementById('checkbox_' + areal_feature_name);

        var areal_feature_area = areal_feature_areaDom.value;
        var areal_feature_checked_bol = areal_feature_checkboxDom.checked;
        if (areal_feature_areaDom.disabled == false
            && areal_feature_checked_bol == true
            && areal_feature_area
            && parseFloat(areal_feature_area) !== NaN)
        {
            sum_areal_features += parseFloat(areal_feature_area);
        }
    }
    /*
    *  Handle validation check that the sum of all areal features does not exceed project area
    *
    *
     */
    var errorDom = document.getElementById('areal_features_validation_error');

    var sumAreaDom = document.getElementById('ui_sum_areal_features_area');
    var sumAreaPercentDom = document.getElementById('ui_sum_areal_features_area_percent');
    if(sum_areal_features) {
        sumAreaDom.value = sum_areal_features;
        if(sum_area && parseFloat(sum_area) !== NaN)
        {
            sumAreaPercentDom.value = parseFloat(100 * sum_areal_features / sum_area).toFixed(2) ;
        }
    }

    var errors = null;
    // if ( sum_area && parseFloat(sum_area) !== NaN && sum_areal_features > sum_area) {
    //     errors = {'message':'The sum of all the enabled areal features is '
    //         + sum_areal_features.toString() + ' which is greater than the size of the project area.'
    //         + ' Calculations are disabled until this error is corrected.'};
    // }
    // showErrorsById('areal_features_validation_error', errors);

    /*
    *  Handle validation check that the sum of pervious and impervious areas do not exceed project area
    *
    *
     */
    errorDom = document.getElementById('pervious_validation_error');
    var pervious_area_featureDom = document.getElementById('ui_pervious_area');
    var impervious_area_featureDom = document.getElementById('ui_impervious_area');

    var pervious_area = pervious_area_featureDom.value;
    var impervious_area = impervious_area_featureDom.value;

    if(! isNaN(parseFloat(pervious_area))) {
        sum_pervious_impervious_area = parseFloat(pervious_area);
    }
    if(! isNaN(parseFloat(impervious_area))) {
        sum_pervious_impervious_area += parseFloat(impervious_area);
    }

    sumAreaDom = document.getElementById('ui_sum_pervious_area');
    sumAreaPercentDom = document.getElementById('ui_sum_pervious_area_percent');

    if(sum_pervious_impervious_area) {
        sumAreaDom.value = sum_pervious_impervious_area;
        if(sum_area && parseFloat(sum_area) !== NaN)
        {
            sumAreaPercentDom.value = parseFloat(100 * sum_pervious_impervious_area / sum_area).toFixed(2) ;
        }
    }
    else {
        sumAreaDom.value = '';
        sumAreaPercentDom.value = '';
    }

    var errors2 = null;
    if ( sum_area && parseFloat(sum_area) !== NaN && sum_pervious_impervious_area > sum_area) {
        errors2 = {'message':'The sum of the pervious and impervious areas is '
            + sum_pervious_impervious_area.toString() + ' which is greater than the size of the project area.'
            + ' Calculations are disabled until this error is corrected.'};
    }
    showErrorsById('pervious_validation_error', errors2);

    return (errors == null && errors2 == null);
}


/*******************************
*
*  Communication functions to submit and get data
*
*
*
*
 */

function getHTTPObject() {
    var xmlhttp;

    if (!xmlhttp && typeof XMLHttpRequest != 'undefined') {
        try {
            xmlhttp = new XMLHttpRequest();
        } catch (e) {
            xmlhttp = false;
        }
    }
    return xmlhttp;
}

var http = getHTTPObject(); // We create the HTTP Object

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}


/*

    Get a template for all the scenario stuff.  It is used to set input filters, and toggle disable/enable things.

 */
function scenarioTemplateJSON() {

    if (_scenario_template == null)
    {
        var url = SETTINGS.URLS.scenario_template;
        // var scenario_template;
        $.ajax(url, {
            contentType : 'application/json; charset=utf-8',
            type : 'GET',
            async: false,
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            },
            success: function (data) {
                _scenario_template = data;
            },
            error: function(data) {
                showError(data);
            }
        });
    }

   return JSON.parse(JSON.stringify(_scenario_template));
}

// alters certain values based on other fields' values to prevent math problems
// this just looks at the specific form field supplied and checks that it is not violating any rules
// i.e. if you change the area for a given areal feature that the total for all of them is greater than the project area
// Note: you can force this using validateForm({id: 'ui_FIELD_TO_TRIGGER'});

function recalculateCosts(formField){
    loadStructureCosts(formField);
    return true;
}

function validateForm(formField) {

    if (! formField) {
        return;
    }

    var scenario_template = scenarioTemplateJSON();

    var valid_bol = true;

    field_id = formField.id;
    field_nm = field_id.replace('ui_','');



    // test that all the areal feature areas don't sum up to more than project area
    if (field_nm == 'project_area' ){
        valid_bol = validateProjectAreaAndArealFeatures();
        if (valid_bol === false) { return false };
    }
    var areal_features_fields = scenario_template['siteData']['areal_features']['fields'];

    for (var i in areal_features_fields){
        var areal_feature_name = areal_features_fields[i];

        if (field_nm == areal_feature_name + '_area'){
            valid_bol = validateProjectAreaAndArealFeatures();
            if (valid_bol === false) { return false };
        }
    }

    // the project type setting affects which of the areal features are disabled
    if (field_nm == 'project_type') {

        valid_bol = validateProjectAreaAndArealFeatures(); // toggle disabled inputs, that are then not used in calculation
        if (valid_bol === false) { return false };
    }


    // the project type setting affects which of the areal features are disabled
    if (field_nm == 'impervious_area' || field_nm == 'pervious_area') {
        valid_bol = validateProjectAreaAndArealFeatures();
        if (valid_bol === false) { return false };
    }

    // this is the drop-down on the Structure Costs page
    if (field_nm == 'structure_select') {
        var fields = scenario_template['siteData']['cost_items']['fields'];
        fields.forEach(function(field_nm) {

            var inputFieldDom = document.getElementById('checkbox_' + field_nm);
            var inputFieldChecked = inputFieldDom.checked;

            //TODO: this is some extra logic to always show any row that has
            // non-blank data.  questionable functionality
            var inputs = ['conversion_factor','factor_assumption_tx','sizing_factor_k','sizing_factor_n','construction_cost_factor_equation'];
            inputs.forEach(function(input_name) {
                var elementObj = document.getElementById('ui_' + field_nm + '_' + input_name);
                if (elementObj && elementObj.value){
                    inputFieldChecked = true;
                }
            })
            // end questionable functionality

            var trDom = document.getElementById('tr_' + field_nm);

            if (inputFieldDom != null && trDom != null) {

                if (inputFieldChecked !== true) {

                    trDom.style.display = 'none';
                }
                else {
                    trDom.style.display =  '';
                }
            }
            else {
                alert("unable to find input field dom for 'checkbox_" + field_nm)
            }

        });

    }
    if (field_nm == 'toggle_structure_cost_items') {
        var toggleDom = document.getElementById(field_nm);
        var checked = toggleDom.checked;

        var fields = scenario_template['siteData']['cost_items']['fields'];
        fields.forEach(function(field_nm) {

            var inputFieldDom = document.getElementById('checkbox_' + field_nm);
            var inputFieldChecked = inputFieldDom.checked;

            //TODO: this is some extra logic to always show any row that has
            // non-blank data.  questionable functionality
            var inputs = ['factor_assumption_tx',
                            'sizing_factor_k',
                            'sizing_factor_n'];
            inputs.forEach(function(input_name) {
                var elementObj = document.getElementById('ui_' + field_nm + '_' + input_name);
                if (elementObj && elementObj.value){
                    inputFieldChecked = true;
                }
            })
            // end questionable functionality

            var trDom = document.getElementById('tr_' + field_nm);

            if (inputFieldDom != null && trDom != null && toggleDom != null) {
                if (checked == true) {

                    trDom.style.display = '';
                }
                else if (checked == false && inputFieldChecked == false){
                    trDom.style.display = 'none';
                }
                else if (inputFieldChecked == true) {
                    trDom.style.display =  '';
                }
            }

        });
    }

    /*
        For the Cost Item Unit Costs - if the user selects 'User' from the drop down list, then enable User Input and Year
        If they select a different item, then clear both those fields.

     */
    if (field_id.replace('_cost_source', '') != field_id) {
        var field_nm = field_id.replace('_cost_source', '').replace('ui_', '');
        var inputFieldDom = document.getElementById(field_id);
        var inputFieldValue = inputFieldDom.value;
        var inputs = ['user_input_cost', 'base_year'];

        inputs.forEach(function(input_name) {
            var elementObj = document.getElementById('ui_' + field_nm + '_' + input_name);
            if (elementObj){
                if (inputFieldValue != 'user') {
                        elementObj.disabled = true;
                        elementObj.style.textDecoration = 'line-through';
                }
                else {
                    elementObj.disabled = false;
                    elementObj.style.textDecoration = 'none';
                }
            }
        })
    }


    var suffix = ['area'];

    // this is a checkbox field - they are attached to area, length, and diameter fields TBD documentation
    if (field_nm == field_id && field_id.replace('checkbox_', '') != field_id) {
        field_nm = field_id.replace('checkbox_','') ;

        var cost_items_fields = scenario_template['siteData']['cost_items']['fields'];
        // if (cost_items_fields.includes(field_nm)) {
        if ($.inArray(field_nm, cost_items_fields)) {
            var suffix = ['a_area', 'z_depth', 'd_density', 'n_number'];

            var inputFieldDom = document.getElementById('checkbox_' + field_nm);
            var inputFieldChecked = inputFieldDom.checked;

            //TODO: this is some extra logic to always show any row that has
            // non-blank data.  questionable functionality
            var inputs = ['conversion_factor',
                            'factor_assumption_tx',
                            'sizing_factor_k',
                            'sizing_factor_n',
                            'construction_cost_factor_equation'];
            inputs.forEach(function(input_name) {
                var elementObj = document.getElementById('ui_' + field_nm + '_' + input_name);
                if (elementObj && elementObj.value){
                    inputFieldChecked = true;
                }
            })
            // end questionable functionality
            var showAllCostItemsDom = document.getElementById('toggle_structure_cost_items');
            var showAllChecked = showAllCostItemsDom.checked;

            var trDom = document.getElementById('tr_' + field_nm);
            if (inputFieldDom != null && trDom != null) {
                if (showAllChecked == false && inputFieldChecked !== true) {

                    trDom.style.display = 'none';
                }
                else {
                    trDom.style.display =  '';
                }
            }
        }

        // this toggles the Areal Input (area) input boxes
        suffix = ['area', 'a_area', 'z_depth', 'd_density', 'n_number'];
        for (i in suffix) {
            var inputFieldDom = document.getElementById('ui_' + field_nm + '_' + suffix[i]);
            if (inputFieldDom != null) {
                if (formField.checked !== true) {
                    inputFieldDom.disabled = true;
                    inputFieldDom.style.textDecoration = 'line-through';
                }
                else {
                    inputFieldDom.disabled = false;
                    inputFieldDom.style.textDecoration = 'none';
                }
            }
        }


        valid_bol = validateProjectAreaAndArealFeatures();
        if (valid_bol === false) { return false };
    }

    /*
    *
    * wonky, but we want to force the number 1 in these fields if they are set blank by the user
    * the field ids are ui_{structure.code}_{partial_field_nm}
     */
    function isNullOrEmpty(str){
        return !str||!str.trim();
    }

    var partial_field_nms = ['a_area', 'z_depth', 'd_density', 'n_number'];
    for (i in partial_field_nms){
        var partial_field_nm = partial_field_nms[i];
        if (field_id.indexOf(partial_field_nm) > 0)
        {
            var inputFieldDom = document.getElementById(field_id);
            if (inputFieldDom != null){
                var inputFieldValue = inputFieldDom.value;
                if (isNullOrEmpty(inputFieldValue))
                {
                    // set the field value to 1
                    inputFieldDom.value = (partial_field_nm == 'n_number') ? 0 : 1;
                }
            }
        }

    }
    return true;

}

function showErrorsById(domID, error)
{
    var errorDom = document.getElementById(domID);

    if (errorDom) {
        if (error == null) {
            errorDom.style.display = 'none';
        }
        else {
            errorDom.innerHTML = error.message;
            errorDom.style.display = 'block';
        }
    }
}

function showError(data) {
    var DivElement = document.getElementById('result-box');
    DivElement.innerHTML = JSON.stringify(data, null, 4);
}

function isArray(obj) {
    return obj.constructor == Array;
}




/* on each key-stroke, run a calculation each time there is an edit in a field */
function returnCalc(formField) {

    // var evt = formField || window.Event;
    // if (evt.keyCode == 13)
    // {
    //     runCalculate(formField);
    //     return false;
    // }

    if (window.event && window.event.keyCode == 13) {
        runCalculate(formField);
        return false;
    }
}
/* run a calculation each time there is an edit in a field */
function runCalculate(formField) {

    var is_valid = validateForm(formField);

    if (is_valid === false) {
        updateResultsPane({'error': 'form is not valid'});
        return false;
    }
    else {
        // this is where the data is sent to the server and when it returns it is loaded into the Results tab
        saveDB(formField);
    }

}


// Use an ajax call to get data in JSON format and then refresh the data
// generate a URL and use ajax to get the content of the StructureCosts table
// URL example
//   /scenario/8/structure_costs/green_roof?format=html
function loadStructureCosts(formFeature) {

    var scenario_id;
    var structureCode;

    var inputDom = document.getElementById('ui_' + 'scenario_id');

    if (inputDom){
        scenario_id = inputDom.value;
    }

    var field_id = 'ui_structure_select'; // formFeature.id;
    var field_nm = field_id.replace('ui_','');

    // the project type setting affects which of the areal features are disabled
    if (field_nm == 'structure_select') {
        // get what the value was and store it for saving the thing
        // get what the new selected value is
        var inputDom = document.getElementById('ui_' + field_nm);
        var structureCode = inputDom.value;
    }

    if (structureCode == '')
    {
        return;
    }

    var structureCostTableDom = document.getElementById('structure_costs_table');

    if (! (scenario_id && structureCode)) {
        if (structureCode == '')
        {
            //structureCostTableDom.innerHTML = 'Select from drop-down list 22Z';
        }
        // return;
    }

    var url = SETTINGS.URLS.scenario_structure_cost.replace('<int:pk>', scenario_id);
    url = url.replace('<str:structure_code>', structureCode);
    //TODO fix this
    url = url.replace('format=html', 'format=json');

   $.ajax(url, {
        //data : JSON.stringify(json),
        contentType : 'application/json; charset=utf-8',
        type : 'GET',
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
            // set the field that shows what is selected and the area of
            var inputDom = document.getElementById('ui_structure_name_2');
            if (inputDom){
                 inputDom.textContent = 'Fetching ...';
            }
            var inputDom = document.getElementById('ui_structure_area_2');
            if (inputDom){ inputDom.value = ''; }
            var inputDom = document.getElementById('ui_structure_units_2');
            if (inputDom){ inputDom.innerHTML = ''; }
        },
        success: function (data) {

            //TADA - replaced loading using HTML with loading via JSON
            populateStructureEquations(data);

            validateForm(formFeature);

            validateForm({id: 'ui_toggle_structure_cost_items'})
        },
        error: function(data) {
            showError(data);
        }
    });
}

function structureCostItemHelp(cost_item_code){
    var base_url = SETTINGS.URLS.scenario_structure_help;
    var url = base_url + '/' + cost_item_code + '/?format=html';

   $.ajax(url, {
        //data : JSON.stringify(json),
        contentType : 'application/json; charset=utf-8',
        type : 'GET',
        async: false, // wait for the response
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: function (data) {
            //alert(JSON.stringify(data));
            return data;

        },
        error: function(data) {
            return "unable to get structure cost item help for " + cost_item_code;
        }
    });
}

/*

    Reads the fields from the HTML document and writes (loads) them into a
   'scenarioData' structure (see the top of this file)

*/
function compileScenarioData() {

    var scenario_template = scenarioTemplateJSON();

    function compile(field_dict){
        field_array = field_dict['fields'];

        field_array.forEach(function(element){
            var elementObj = document.getElementById('ui_' + element);
            if (! elementObj)
            {
                field_dict[element] = 'NOT FOUND for element ' + element;
            }
            else
            {
                field_dict[element] = elementObj.value;
            }

        });
        delete field_dict['fields'];
    }

    function compileStructureCosts(structure, field_dict) {

        //what structure are they showing in the dropdown list
        var structure_name = document.getElementById('ui_structure_select').value;

        // if they haven't selected a structure from the list, return
        if (structure_name == ''){
            return;
        }

        field_array = field_dict['fields'];

        delete field_dict['fields'];

        // rebuild field_dict
        // field_dict['structure'] = structure;

        //store data in 'user_assumptions'
        field_dict['user_assumptions'] = {
                        'structure': structure,
                        'data': {}
                        };


        //what structure are they showing in the dropdown list
        var structure_name = document.getElementById('ui_structure_select').value;

        field_array.forEach(function(cost_item){

            var inputs = [

                'a_area',
                'z_depth',
                'd_density',
                'n_number',

            ];

            // don't return data if the checkbox is not checked
            var elementObj = document.getElementById('checkbox_' + cost_item);

            if (elementObj)
            {
                if (! field_dict['user_assumptions']['data'][cost_item])
                {
                    field_dict['user_assumptions']['data'][cost_item] = {'checked': elementObj.checked};
                }
                var non_null_count = 0;
                inputs.forEach(function(input_name) {

                    var elementObj = document.getElementById('ui_' + cost_item + '_' + input_name);

                    if (! elementObj)
                    {
                        field_dict['user_assumptions']['data'][cost_item][input_name] = 'NOT FOUND ui_' + cost_item + '_' + input_name;
                    }
                    else
                    {
                        var form_value = elementObj.value;
                        if (form_value == '') {
                            form_value = null
                        }
                        else{
                            non_null_count += 1;
                        }
                        field_dict['user_assumptions']['data'][cost_item][input_name] = form_value;
                    }

                })
                if (field_dict['user_assumptions']['data'][cost_item] == false
                    && non_null_count == 0)
                {
                    delete(field_dict['user_assumptions']['data'][cost_item]);
                }
            }



            //TODO figure out exactly what to do here.  if a user removes all data
            // from an item, this has to send that information to the model to remove the item...
            // or does it. the model can look at all the options and remove any 'missing' ones.
            // remove if there is really no data
            // var fd = field_dict['user_assumptions'][cost_item];
            // if (fd['checkbox'] == false
            //     && fd['sizing_factor_k'] == ''
            //     && fd['factor_assumption_tx'] == '')
            // {
            //     delete field_dict['user_assumptions'][cost_item];
            // }

        })
    }

    function compileCosts(cost_item_list, field_dict) {
        field_array = cost_item_list;

        //delete field_dict['fields'];

        // rebuild field_dict
        //field_dict['structure'] = structure;
        field_dict['unit_costs'] = {};

        field_array.forEach(function(element_name){
            var inputs = ['cost_source',
                'user_input_cost',
                'base_year',
                'replacement_life',
                'o_and_m_pct'];

            if (! field_dict['unit_costs'][element_name])
            {
                field_dict['unit_costs'][element_name] = {};
            }
            inputs.forEach(function(input_name) {
                //this triggers using 2 other fields
                if (input_name == 'unit_costZZZZ') {
                    var elementObj = document.getElementById('ui_' + element_name + '_' + input_name);
                    if (!elementObj) {
                        field_dict['unit_costs'][element_name]['checkbox'] = 'NOT FOUND 2 for element ' + element_name + '_' + input_name;
                    } else {
                        field_dict['unit_costs'][element_name]['checkbox'] = elementObj.checked;
                    }
                }
                else {
                    var elementObj = document.getElementById('ui_' + element_name + '_' + input_name);
                    if (! elementObj)
                    {
                        field_dict['unit_costs'][element_name][input_name] = 'NOT FOUND 2 for element ' + element_name;
                    }
                    else
                    {
                        var form_value = elementObj.value;
                        if (form_value == '') { form_value = null }
                        field_dict['unit_costs'][element_name][input_name] = form_value;
                    }
                }
            })
        })
    }

    function compileStructure(field_dict){
        field_array = field_dict['fields'];
        input_dict = field_dict['inputs'];

        field_array.forEach(function(element_name){
            var inputs = input_dict[element_name];
            if (! field_dict[element_name])
            {
                field_dict[element_name] = {};
            }
            inputs.forEach(function(input_name){

                if (input_name == 'checkbox'){
                    var elementObj = document.getElementById('checkbox_' + element_name);
                    if (! elementObj)
                    {
                        field_dict[element_name]['checkbox'] = 'NOT FOUND for element ' + element_name;
                    }
                    else
                    {
                        field_dict[element_name]['checkbox'] = elementObj.checked;
                    }
                }
                else {
                    var elementObj = document.getElementById('ui_' + element_name + '_' + input_name);
                    if (! elementObj)
                    {
                        field_dict[element_name][input_name] = 'NOT FOUND for element ' + element_name;
                    }
                    else
                    {
                        field_dict[element_name][input_name] = elementObj.value;
                    }
                }
            });
        });
        delete field_dict['fields'];
        delete field_dict['inputs'];
    }

    function compileID(field_dict, element_name)
    {
        var elementObj = document.getElementById('ui_' + element_name);
        if (! elementObj)
        {
            field_dict[element_name] = 'NOT FOUND for element ' + element_name;
        }
        else
        {
            field_dict[element_name] = elementObj.value;
        }
    }



    compileID(scenario_template, 'scenario_id');
    compileID(scenario_template, 'project_id');

    //TODO: rename this scenario_info or similar
    compile(scenario_template['siteData']['embedded_scenario']);

    compileStructure(scenario_template['siteData']['areal_features']);

    delete scenario_template['siteData']['areal_features']['toggles'];


    compileStructure(scenario_template['siteData']['conventional_structures']);

    compileStructure(scenario_template['siteData']['nonconventional_structures']);

    // this is the drop-down on the Structure Costs page
    var selectedStructureObj = document.getElementById('ui_structure_select');
    var selectedStructure = selectedStructureObj.value;

    var cost_item_list = scenario_template['siteData']['cost_items']['fields'];
    // change this to compileStructureCosts
    compileStructureCosts(selectedStructure, scenario_template['siteData']['cost_items']);

    compileCosts(cost_item_list, scenario_template['siteData']['cost_items']);

    return scenario_template;
}

// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


/*
*
* POST a copy of all the form data to the server and get back a updated scenario in JSON format
*
*
*
 */

//jab - this saves a JSON copy of all the values in the HTML document
function saveDB(action) {

    var scenarioData = compileScenarioData();

    var csrftoken = getCookie('csrftoken');

    var json = JSON.stringify(scenarioData);

    var url = SETTINGS.URLS.scenario_save;
    $.ajax(url, {
        data : JSON.stringify(json),
        contentType : 'application/json; charset=utf-8',
        type : 'POST',
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: function (data) {
            //alert(JSON.stringify(data));

            if ('uiMessage' in data)
            {
                //This was used when CREATE sucked
                // if ('redirect_required' in data['uiMessage'])
                // {
                //     //replaced with just plugging in the value into the DOM
                //     var url = data['uiMessage']['redirect_required']['redirect_to'];
                //     window.location.replace(url);
                //     // var inputDom = document.getElementById('ui_' + 'scenario_id');
                //     //
                //     // if (inputDom){
                //     //     inputDom.value = data['uiMessage']['redirect_required']['scenario_id'];
                //     // }
                //
                // }
            }

            // this is really weak error handling
            var errors;
            var scenario_title_errors;
            if ('Error' in data)
            {
                if ('error_dom_id' in data['Error'] && data['Error']['error_dom_id'] == 'scenario_title_validation_error')
                {
                    scenario_title_errors = data['Error'];
                }
                else if ('message' in data['Error'])
                {
                    errors = data['Error'];
                }
            }

            // this hides the errors if there is none
            showErrorsById('general_validation_error', errors);
            showErrorsById('scenario_title_validation_error', scenario_title_errors);

            updateResultsPane(data); // loads a snippet of HTML delivered in the data array
            updateProjectTitle(data['siteData']);

            updateStructureCostDropDown(data['siteData']);
        },
        error: function(data) {
            showError(data);
        }
    });
}

/*
* Save a copy of all the data in a JSON file on disc via the 'Save JSON' button in the cost tool
*
*
*
 */
function saveJSON(action) {

    var scenarioData = compileScenarioData();

    process_sid = 'raleighCostTool'; // document.getElementById('s').value;

    var json = JSON.stringify(scenarioData, null, 4);
    var jsonFileText = new Blob([json],
    {
        type: "application/json;charset=utf-8;"
    });

    saveAs(jsonFileText, process_sid + ".json");

}

/*
* Read a JSON file from disc via the 'Load JSON' button in the cost tool
*
*
*
 */
function loadJSON(e) {
    var files = e.target.files;
    var reader = new FileReader();

    reader.onload = function () {
        var parsed;
        var loaded_data;
        try {
            loaded_data = JSON.parse(this.result);
            // remove the scenario_id since it is from the uploaded JSON, and not the scenario being edited
            if ('scenario_id' in loaded_data) {
                delete loaded_data['scenario_id'];
            }
            // add something to remind the user that this is entirely loaded from JSON
            if ('scenario_title' in loaded_data['siteData']['embedded_scenario']) {
                loaded_data['siteData']['scenario_title']['embedded_scenario'] += ' (LOADED)';
            }

            populateUI(loaded_data['siteData']);

        } catch (ex) {
            alert('ex when trying to load JSON file = ' + ex);
        }
    }

    reader.readAsText(files[0]);
}


/**************************************************************
*
*  UI things to
*    Restricts input for the given textbox according to the given inputFilter.
*
*
*
*/

function setInputFilter(textbox, inputFilter) {
    if (textbox) {
        textbox.inputFilter = inputFilter;
        ["input",
            "keydown",
            "keyup",
            "mousedown",
            "mouseup",
            "select",
            "contextmenu"].forEach(function (event) {
            textbox.addEventListener(event, function () {
                filterInput(textbox);
            });
        });
        filterInput(textbox);
    }
}

// Implements input filtering for the given textbox.
function filterInput(textbox)
{
  if (!textbox.hasOwnProperty("oldValue") || textbox.inputFilter(textbox.value))
  {
    textbox.oldValue = textbox.value;
    textbox.oldSelectionStart = textbox.selectionStart;
    textbox.oldSelectionEnd = textbox.selectionEnd;
  }
  else
  {
    textbox.value = textbox.oldValue;
    textbox.setSelectionRange(textbox.oldSelectionStart, textbox.oldSelectionEnd);
  }
}

function setAllFieldInputFilters()
{
    function setFieldInputFilter(field){

        switch (field) {
          case (field.match(/(_pct|_factor)$/) || {}).input:
            setInputFilter(document.getElementById('ui_' + field), function (value) {
                if (/^\d{0,2}\.\d{0,2}$/.test(value)) { return true };
                if (/^(100|\d{0,2})$/.test(value)) { return true };
                return false;
            });
            break;
          case (field.match(/_depth$/) || {}).input:
            setInputFilter(document.getElementById('ui_' + field), function (value) {
                return (/^\d{0,5}\.?\d{0,2}$/.test(value));
            });
            break;
          case (field.match(/_sizing_factor_/) || {}).input:
            setInputFilter(document.getElementById('ui_' + field), function (value) {
                return (/^\d{0,2}\.?\d{0,2}$/.test(value));
            });
            break;
          case (field.match(/_porosity$/) || {}).input:
            setInputFilter(document.getElementById('ui_' + field), function (value) {
                return (/^(0|[0]?\.?\d{0,2})$/.test(value));
            });
            break;
          case (field.match(/(_area|_acres)$/) || {}).input:
            setInputFilter(document.getElementById('ui_' + field), function (value) {
                return /^\d{0,6}\.?\d{0,3}$/.test(value);
            });
            break;
          case (field.match(/(_cost|_   |_first_year|_cost_per_ft2)$/) || {}).input:
            setInputFilter(document.getElementById('ui_' + field), function (value) {
                return /^\d{0,6}\.?\d{0,2}$/.test(value);
            });
            break;

          case (field.match(/_volume$/) || {}).input:
            setInputFilter(document.getElementById('ui_' + field), function (value) {
                return (/^\d{0,5}\.?\d{0,3}$/.test(value));
            });
            break;
          case (field.match(/(_length|_width|_diameter|_rate)$/) || {}).input:
            setInputFilter(document.getElementById('ui_' + field), function (value) {
                return (/^\d{0,5}\.?\d{0,3}$/.test(value));
            });
            break;
          case (field.match(/(_qty|_count)$/) || {}).input:
            setInputFilter(document.getElementById('ui_' + field), function (value) {
                if (/^\d{0,5}$/.test(value)) { return true };
                return false;
            });
            break;
          case (field.match(/(_base_year)$/) || {}).input:
            setInputFilter(document.getElementById('ui_' + field), function (value) {
                if (/^\d{1,4}$/.test(value)) {
                    // if (len(value) == 4 & value >= 1000 & (value < 1990 || value >= 2020)) {
                    //     return false;
                    // }
                    if (value <= 2020) {
                        return true;
                    }
                    return false;
                };
                return false;
            });
            break;
          case (field.match(/(_year|_life)$/) || {}).input:
            setInputFilter(document.getElementById('ui_' + field), function (value) {
                if (/^\d{0,4}$/.test(value)) {
                    if (value <= 100) {
                        return true;
                    }
                    return false;
                };
                return false;
            });
            break;
          default:
            // console.log("Didn't match '" + field + "'");
            break;
        }
    };

    function set_structures_input_filter(structures){
        for (var structure in structures) {
            // each Areal Feature has a button
            var domElement = document.getElementById('checkbox_' + structure);
            if (! domElement){
                alert("There is no Structure button: 'checkbox_" + structure + "'");
            }
            else {
                // Adds 'Check this to enable input for this areal feature'
               domElement.title = open_structure_checkbox_title(structure);
            }

            var fields = structures[structure];
            fields.forEach(function(field) {
                if (field != 'checkbox'){
                    setFieldInputFilter(structure + '_' + field);
                }


            });
        };
    }

    function set_costitem_unit_costs_input_filter(costitems){
        costitems.forEach(function(costitem)
         {
            var fields = ['user_input_cost', 'base_year', 'replacement_life', 'o_and_m_pct'];
            fields.forEach(function(field) {
               setFieldInputFilter(costitem + '_' + field);
            });
        });
    }

    function set_structure_costs_input_filter(costitems){
        costitems.forEach(function(costitem)
         {
            var fields = ['sizing_factor_k', 'sizing_factor_n'];
            fields.forEach(function(field) {
               setFieldInputFilter(costitem + '_' + field);
            });
        });
    }

    /*
    *
    *  this uses the scenario template just to set input filters
    *
    *
     */

    var scenario_template = scenarioTemplateJSON();

    var scenario_fields = scenario_template['siteData']['embedded_scenario']['fields'];

    scenario_fields.forEach(function(field) {
        setFieldInputFilter(field);
    });

    // Set up the button and input text-box popup help text and input filter for each Areal Features
    var areal_features_fields = scenario_template['siteData']['areal_features']['fields'];

    for (var i in areal_features_fields) {
        var name = areal_features_fields[i];

        // each Areal Feature has a button
        var domElement = document.getElementById('checkbox_' + name);
        if (! domElement){
            alert("There is no Areal Feature button: 'checkbox_" + name + "'");
        }
        else {
            // Adds 'Check this to enable input for this areal feature'
           domElement.title = open_af_button_title(name);
        }

        // and a text-box called 'ui_' name
        domElement = document.getElementById('ui_' + name + '_area'); //TODO
        if (! domElement){
            alert("There is no Areal Feature text-box: 'ui_" + name + "'");
        }
        else {
           // 2019-09-11 removed since this is just boilerplate
            // domElement.title = open_af_input_title(name);
           // set the input filter to a float
            setInputFilter(domElement, function (value) {
                return (/^\d{0,5}\.?\d{0,2}$/.test(value));
            });
        }
    }

    set_structures_input_filter(scenario_template['siteData']['conventional_structures']['inputs']);

    set_structures_input_filter(scenario_template['siteData']['nonconventional_structures']['inputs']);

    //structure costs
    set_structure_costs_input_filter(scenario_template['siteData']['cost_items']['fields']);

    // cost item unit costs
    set_costitem_unit_costs_input_filter(scenario_template['siteData']['cost_items']['fields']);


}

