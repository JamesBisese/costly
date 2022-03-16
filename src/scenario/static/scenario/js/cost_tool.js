/*jshint esversion: 6 */
/*jshint strict:false */
/*globals $:false */

//TODO - what does this mean????
// this is populated one time via an ajax call
// it has triggering logic for various elements

var _scenario_template = null;
var URLS = null; // this gets set via another javascript file sourced before this file
var csrftoken = null;
/********************************
*
* Initialize document
*
* all URLs are defined with variables ending in '_url'
* all ajax calls are to URLs defined in the javascript file urls.js which is
*  responsible for toggling the correct url between development and production installations
*
 */


$(document).ready(function()
{
    URLS = SETTINGS.URLS;

    csrftoken = getCookie('csrftoken');

    // store a cookie to return to the active tab when users open/reopen the web application
    $("#tab_box").tabs({
        "activate": function (event, ui) {
            let id = ui.newPanel[0].id;
            setCookie('tab', id, 365);
        }
    });

    /*
    *
    *  populate the results tab if the user is opening the tool right onto the results tab.
    *
     */
    let id = getCookie('tab');
    if (id !== '')
    {
        var index = $('#tab_box a[href="#' + id + '"]').parent().index();
        $("#tab_box").tabs("option", "active", index );

        if (id === "input-result")
        {
            populateResultsTab();
        }
    }

    // set field restrictions (i.e. numbers only) on fields
    setAllFieldInputFilters();
    let scenario_id = null;

    // this got lost in an edit and stopped everything from working
    //start
    let inputDom = document.getElementById('ui_' + 'scenario_id');

    if (inputDom){
        scenario_id = inputDom.value;
    }
    //end

    var url = null;

    // if there is a scenario_id (this is opened as an update) use the API url
    if (scenario_id !== null && scenario_id !== '')
    {
        url = URLS.scenario_api.replace('<int:pk>', scenario_id);
    }
    else // create a new scenario and load with the default data
    {
        url = URLS.scenario_default;
    }


    // reset the drop-down of Strucures when the user clicks the Structure/Cost Item User Factors tab
    let testTarget = document.getElementById("structure_costs_tab");
    if(testTarget !== undefined){
        testTarget.addEventListener("click", loadStructureCosts, false);
    }

    // populate the Results when the user clicks that tab
    testTarget = document.getElementById("input_result_tab");
    if(testTarget !== undefined){
        testTarget.addEventListener("click", populateResultsTab, false);
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
            document.getElementById("network_indicator").style.display = "none";
            document.getElementById("cost_tool-loader").style.display = "none";
            document.getElementById("calculate").style.animation = "fade_in_show 0.75s";
            document.getElementById("calculate").style.display = "block";
        },
        error: function(data) {
            showError(data);
        }
    });


});


function populateStructureAreaTable() {
    let scenarioData = compileScenarioData();
    let data = {};
    let structureCode = '';

    var field_id = 'ui_structure_select'; // formFeature.id;
    var field_nm = field_id.replace('ui_','');

    // the project type setting affects which of the areal features are disabled
    if (field_nm === 'structure_select') {
        // get what the value was and store it for saving the thing
        // get what the new selected value is
        let inputDom = document.getElementById('ui_' + field_nm);
        structureCode = inputDom.value;
        if (structureCode in scenarioData.siteData.nonconventional_structures){
            data = scenarioData.siteData.nonconventional_structures[structureCode];
            data.area = Number(data.area);
            data.name = scenarioData.siteData.nonconventional_structures.labels[structureCode];
            data.units = 'SF';
        }
        else if (structureCode in scenarioData.siteData.conventional_structures){
            data = scenarioData.siteData.conventional_structures[structureCode];
            data.area = Number(data.area);
            data.name = scenarioData.siteData.conventional_structures.labels[structureCode];
            data.units = 'SF';
        }
    }

    // set the field that shows what is selected and the area of
    let inputDom = document.getElementById('ui_structure_name_2');
    if (inputDom){
         inputDom.textContent = data.name;
    }
    inputDom = document.getElementById('ui_structure_area_2');
    if (inputDom){
         inputDom.value = data.area.toLocaleString();
    }
    inputDom = document.getElementById('ui_structure_units_2');
    if (inputDom){
         inputDom.innerHTML = data.units;
    }
}

/**********************************************************
*
* Populates the UI with the values in the JSON object
*
*
*/
function populateUI(siteData) {

    if (! siteData) {
        return;
    }

    function updateField(field_dict)
    {
        // make it safe if the field isn't found
        for (var key in field_dict) {
            if (field_dict.hasOwnProperty(key))
            {
                let value = field_dict[key];
                var update_field = document.getElementById('ui_' + key);
                if (update_field) {
                    update_field.value = value;
                }
            }
        }
    }

    function updateArealFeatures(features)
    {
        features.forEach((data) => {
            let checkboxDom = document.getElementById('checkbox_' + data.areal_feature_code);
            if (checkboxDom) {
                checkboxDom.checked = data.is_checked;
            }
            let areaInputDom = document.getElementById('ui_' + data.areal_feature_code + '_area');
            if (areaInputDom) {
                areaInputDom.value = data.area;
                if (data.is_checked !== true) {
                    areaInputDom.disabled = true;
                    areaInputDom.style.textDecoration = 'line-through';
                } else {
                    areaInputDom.disabled = false;
                    areaInputDom.style.textDecoration = 'none';
                }
            }
        });
    }

    function updateStructures(structures)
    {
        structures.forEach((data) => {
            let checkboxDom = document.getElementById('checkbox_' + data.structure_code);
            if (checkboxDom) {
                checkboxDom.checked = data.is_checked;
            }
            let areaInputDom = document.getElementById('ui_' + data.structure_code + '_area');
            if (areaInputDom) {
                areaInputDom.value = data.area;
                if (data.is_checked !== true) {
                    areaInputDom.disabled = true;
                    areaInputDom.style.textDecoration = 'line-through';
                } else {
                    areaInputDom.disabled = false;
                    areaInputDom.style.textDecoration = 'none';
                }
            }
        });
    }

    function populateCostItemUnitCosts(field_dict)
    {
        /*
            add in all the data in the Cost Item Unit Costs tab

         */
        for (var i in field_dict){
            if (field_dict.hasOwnProperty(i)) {
                let field_object = field_dict[i];

                // each one has one or more 'area', 'unit_cost', 'replacement_life', 'first_year'
                var cost_item_code = field_object.costitem_code;
                let field_list = [
                    'user_input_cost',
                    'base_year',
                    'replacement_life',
                    'o_and_m_pct'
                ];
                let inputDom = document.getElementById('ui_' + cost_item_code + '_' + 'cost_source');
                if (inputDom) {
                    // this is for migration to the new storage
                    if (field_object.cost_source === 'rsmeans')
                    {
                        inputDom.options[1].selected = true;
                    }
                    else
                    {
                        inputDom.value = field_object.cost_source;
                    }

                }

                for (var j in field_list) {
                    if (field_list.hasOwnProperty(j)) {
                        var subfield_name = field_list[j];
                        var value_name = field_object[subfield_name];

                        let inputDom2 = document.getElementById('ui_' + cost_item_code + '_' + subfield_name);
                        if (inputDom2) {
                            inputDom2.value = value_name;
                        }
                    }
                }
                var inputs = ['user_input_cost', 'base_year'];

                inputs.forEach(function (input_name) {
                    let elementObj = document.getElementById('ui_' + cost_item_code + '_' + input_name);
                    if (elementObj) {
                        if (field_object.cost_source !== 'user') {
                            elementObj.disabled = true;
                            elementObj.style.textDecoration = 'line-through';
                        } else {
                            elementObj.disabled = false;
                            elementObj.style.textDecoration = 'none';
                        }
                    }
                });
            }
        }
    }


    //Note: yes - this is crazy bad - but CREATE and UPDATE have different versions of siteData
    // CREATE uses the siteTemplate and UPDATE uses the API correctly

    if ('siteData' in siteData) {
        siteData = siteData.siteData;
    }

    if ('location' in siteData)
    {
        updateField(siteData.location);
    }
    else if ('embedded_scenario' in siteData)
    {
        updateField(siteData.embedded_scenario);
    }

    let inputDom = document.getElementById('scenario_name');
    if (inputDom){
        updateProjectTitle(siteData);
    }

    // updateArealFeatures(siteData.areal_features);

    // this is the new version to go with 2 tables ConventionalStructures and NonConventionalStructures
    // updateArealFeatures(siteData.conventional_structures);
    // updateArealFeatures(siteData.nonconventional_structures);

    // this is the new version to go with ScenarioStructure

    updateArealFeatures(siteData.a_features);

    updateStructures(siteData.nc_structures);
    updateStructures(siteData.c_structures);

    populateCostItemUnitCosts(siteData.cost_item_user_costs);

    //NOTE: Structure Costs are loaded as an partial HTML document
    //TODO: replace that function with normal loading
}


function populateStructureEquations(data){
/*
* this populates fields in the Structure Cost Item User Factors page
*
*
*/
    //TODO
    // var structure_name = data.structure.name;
    if (data.structure.area === null){
        data.structure.area = 0;
    }
    // var area = data.structure.area;

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

        ];

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
    let inputDom = document.getElementById('ui_structure_name_2');
    if (inputDom){
         inputDom.textContent = data.structure.name;
    }
    inputDom = document.getElementById('ui_structure_area_2');
    if (inputDom){
         inputDom.value = data.structure.area.toLocaleString();
    }
    inputDom = document.getElementById('ui_structure_units_2');
    if (inputDom){
         inputDom.innerHTML = data.structure.units;
    }

    // clear out the old input
    for (let cost_item in cost_items) {
        if (cost_items.hasOwnProperty(cost_item)) {
            var inputDom3 = document.getElementById('checkbox_' + cost_item);
            if (inputDom3) {
                inputDom3.checked = false;
            }
            for (let i in ui_field_list) {
                if (ui_field_list.hasOwnProperty(i)) {
                    var ui_field_name = ui_field_list[i];

                    var inputDom4 = document.getElementById('ui_' + cost_item + '_' + ui_field_name);
                    if (inputDom4) {
                        inputDom4.value = '';
                    }
                }
            }
        }
    }

    // load in the new values
    for (let cost_item in cost_items){
        if (cost_items.hasOwnProperty(cost_item)) {
            var cost_item_data = cost_items[cost_item];
            // get the boolean for if it is checked or not
            var cost_item_checked = cost_item_data.checked;
            // first set the checkbox
            let inputDom = document.getElementById('checkbox_' + cost_item);
            if (inputDom) {
                inputDom.checked = cost_item_checked;
            }

            //hide the factor field if that factor is not in the equation
            var equation = cost_item_data.equation;
            for (let f in factor_field_list) {
                if (factor_field_list.hasOwnProperty(f)) {
                    var field_name = factor_field_list[f];
                    var equation_factor_tx = factor_equation_list[f];
                    let inputDom6 = document.getElementById('ui_' + cost_item + '_' + field_name);

                    // hide or show depending on if the field is in the equation
                    if (inputDom6) {
                        //boolean
                        var show_input = equation.indexOf(equation_factor_tx) > 0;

                        inputDom6.style.display = show_input ? '' : 'none';
                        inputDom6.disabled = cost_item_checked ? false : true;
                        inputDom6.style.textDecoration = cost_item_checked ? '' : 'line-through';
                    }
                }
            }

            // now the 4 factor fields
            for (var i in field_list) {
                if (field_list.hasOwnProperty(i)) {
                    let field_name = field_list[i];

                    var field_value = '';
                    if (field_name in cost_item_data) {
                        // this is the value put into the UI
                        field_value = cost_item_data[field_name];
                    }

                    let ui_field_name = ui_field_list[i];

                    let inputDom = document.getElementById('ui_' + cost_item + '_' + ui_field_name);
                    if (inputDom) {
                        inputDom.value = field_value;

                        if (field_name === 'equation') {
                            var title = cost_item_data.equation_calc;
                            if (title === undefined) {
                                title = cost_item_data.equation;
                            } else {
                                title = '=' + title;
                            }
                            var text = document.createTextNode(field_value);

                            while (inputDom.firstChild) {
                                inputDom.removeChild(inputDom.firstChild);
                            }
                            // text.title = title;
                            inputDom.title = title;
                            inputDom.appendChild(text);
                        } else if (field_name === 'equation_value') {

                            let dollar_div = document.createElement('div');
                            dollar_div.className = 'dollar';
                            dollar_div.style.paddingLeft = '3px';

                            dollar_div.innerText = '$';

                            let text = document.createTextNode(field_value);
                            while (inputDom.firstChild) {
                                inputDom.removeChild(inputDom.firstChild);
                            }
                            inputDom.appendChild(dollar_div);
                            inputDom.appendChild(text);

                        } else if (field_name === 'unit_cost') {

                            let dollar_div = document.createElement('div');
                            // dollar_div.className = 'dollar';
                            // dollar_div.innerText = '$';
                            // dollar_div.style.paddingLeft = '3px';
                            // dollar_div.style.display = 'inline';
                            let text = document.createTextNode(cost_item_data.cost_data.cost_type + " " + cost_item_data.cost_data.valid_start_date_tx +
                                " - " + Number(cost_item_data.cost_data.value_numeric).toFixed(2));
                            while (inputDom.firstChild) {
                                inputDom.removeChild(inputDom.firstChild);
                            }
                            // inputDom.appendChild(dollar_div);
                            inputDom.appendChild(text);
                        }
                    }
                }
            }
        }
    }
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

function populateResultsTab(){

    var DivElement = document.getElementById('result-box');
    DivElement.innerHTML = ""; //  "Loading ...<div style='width: 100%; display: flex;'><progress style='margin-left:auto;margin-right:auto;'></progress></div>";
    document.getElementById("network_indicator").style.display = "";
    let scenario_id;
    let inputDom = document.getElementById('ui_' + 'scenario_id');
    if (inputDom){
        scenario_id = inputDom.value;
    }

    var url = URLS.scenario_result.replace('<int:pk>', scenario_id);
    $.ajax(url, {
        contentType : 'application/json; charset=utf-8',
        type : 'GET',
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: function (data) {
            let data2 = {'html_result': data};
            // uses the data in the JSON object to populate the UI when the scenario is first opened
            updateResultsPane(data2);
        },
        error: function(data) {
            updateResultsPane(data);
        }
    });
}

/*******************
*
* Insert the results (data) in the Results pane
*
*
*
 */
function updateResultsPane(data){

    var div = document.getElementById('result-box');

    let contentTX;

    if(data.hasOwnProperty('html_result')) // first loaded
    {
        contentTX = data.html_result;
    }
    else if(data.hasOwnProperty('error'))
    {
        contentTX = "There is an error in one of the tabs so the results cannot be computed";
    }
    else
    {
        contentTX = "There is an error somewhere and the results cannot be computed";
    }

    // wait 700 milliseconds just because it looks better - less flashy
    setTimeout(function() { div.innerHTML = contentTX;}, 0);
    document.getElementById("network_indicator").style.display = "none";

}

function updateProjectTitle(siteData){
    /* load the project - scenario title that is shown above the tabs */
    var inputDom = document.getElementById('scenario_name');

    if (inputDom){
        let project_title = 'PROJECT TITLE';
        let scenario_title = 'SCENARIO TITLE';
        if(siteData.hasOwnProperty('project')) // first loaded
        {
            if (siteData.project !== undefined) {
                if (siteData.project.project_title !== undefined) {
                    project_title = siteData.project.project_title;
                }
            }
            if (siteData.hasOwnProperty('embedded_scenario') !== undefined) {
                if (siteData.embedded_scenario.scenario_title !== undefined) {
                    scenario_title = siteData.embedded_scenario.scenario_title;
                }
            }
            inputDom.innerHTML = project_title + ' -- ' + scenario_title;
        }
    }
}


function updateStructureCostDropDown(siteData){
    /*
    this populates the drop-down on the Structure/Cost Item Users Factors


     */
    function compileStructureList(structures, prefix) {
        //
        var labels = structures.labels;

        for (var structure in structures){
            if (structures.hasOwnProperty(structure))
            {
                if (structure === 'labels'){
                    continue;
                }

                var structure_obj = structures[structure];

                if(structure === 'curb_and_gutter'){ // this one doesn't need an area
                    structure_obj.area = undefined;
                }

                if (structure_obj.checkbox === true &&
                    structure_obj.area !== '' &&
                    structure_obj.area !== 0)
                {
                    structure_list.push({ value: structure, text: prefix + ' - ' + labels[structure]});
                }
            }

        }
    }

    let structure_select = document.getElementById('ui_structure_select');
    let selected_value = structure_select.value;
    //zed
    let structure_list = [];

    compileStructureList(siteData.nonconventional_structures, 'Non-Conventional');
    compileStructureList(siteData.conventional_structures, 'Conventional');

    //
    structure_select.options.length = 0;
    for (let i = 0; i < structure_list.length; i++) {
        const o = document.createElement("option");
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
    let sum_area_field = 'project_area';

    let sum_area = document.getElementById('ui_' + sum_area_field).value;

    let sum_areal_features = 0.0;
    let sum_pervious_impervious_area = 0.0;

    const scenario_template = scenarioTemplateJSON();
    let areal_features_fields = scenario_template.siteData.areal_features.fields;

    for (let i in areal_features_fields){
        if (areal_features_fields.hasOwnProperty(i)) {
            let areal_feature_name = areal_features_fields[i];
            let areal_feature_areaDom = document.getElementById('ui_' + areal_feature_name + '_area');
            let areal_feature_checkboxDom = document.getElementById('checkbox_' + areal_feature_name);

            let areal_feature_area = areal_feature_areaDom.value;
            let areal_feature_checked_bol = areal_feature_checkboxDom.checked;
            if (areal_feature_areaDom.disabled === false &&
                areal_feature_checked_bol === true &&
                areal_feature_area &&
                !isNaN(parseFloat(areal_feature_area))) {
                sum_areal_features += parseFloat(areal_feature_area);
            }
        }
    }
    /*
    *  Handle validation check that the sum of all areal features does not exceed project area
    *
    *
     */
    var errorDom = document.getElementById('areal_features_validation_error');

    var sumAreaDom = document.getElementById('ui_sum_areal_features_area');

    if(sum_areal_features) {
        let sumAreaPercentDom = document.getElementById('ui_sum_areal_features_area_percent');
        sumAreaDom.value = sum_areal_features;
        if(sum_area && !isNaN(parseFloat(sum_area)))
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
    let sumAreaPercentDom = document.getElementById('ui_sum_pervious_area_percent');

    if(sum_pervious_impervious_area) {
        sumAreaDom.value = sum_pervious_impervious_area;
        if(sum_area && !isNaN(parseFloat(sum_area)))
        {
            sumAreaPercentDom.value = parseFloat(100 * sum_pervious_impervious_area / sum_area).toFixed(2) ;
        }
    }
    else {
        sumAreaDom.value = '';
        sumAreaPercentDom.value = '';
    }

    var errors2 = null;
    if ( sum_area && !isNaN(parseFloat(sum_area)) && sum_pervious_impervious_area > sum_area) {
        errors2 = {'message':'The sum of the pervious and impervious areas is ' +
            sum_pervious_impervious_area.toString() + ' which is greater than the size of the project area.' +
            ' Calculations are disabled until this error is corrected.'};
    }
    showErrorsById('pervious_validation_error', errors2);

    return (errors === null && errors2 === null);
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

    if (!xmlhttp && typeof XMLHttpRequest !== 'undefined') {
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

    if (_scenario_template === null)
    {
        var url = URLS.scenario_template;
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
    runCalculate(formField);
    loadStructureCosts(formField);
    return true;
}

function validateForm(formField) {

    let i;
    if (! formField) {
        return;
    }

    if (! ('id' in formField)) {
        return;
    }

    let scenario_template = scenarioTemplateJSON();

    let valid_bol = true;

    let field_id = formField.id;
    let field_nm = field_id.replace('ui_','');

    // test that all the areal feature areas don't sum up to more than project area
    if (field_nm === 'project_area' ){
        valid_bol = validateProjectAreaAndArealFeatures();
        if (valid_bol === false) { return false; }
    }
    let areal_features_fields = scenario_template.siteData.areal_features.fields;

    for (i in areal_features_fields){
        if (areal_features_fields.hasOwnProperty(i)) {
            let areal_feature_name = areal_features_fields[i];

            if (field_nm === areal_feature_name + '_area') {
                valid_bol = validateProjectAreaAndArealFeatures();
                if (valid_bol === false) {
                    return false;
                }
            }
        }
    }

    // the project type setting affects which of the areal features are disabled
    if (field_nm === 'project_type') {
        valid_bol = validateProjectAreaAndArealFeatures(); // toggle disabled inputs, that are then not used in calculation
        if (valid_bol === false) { return false; }
    }

    // the project type setting affects which of the areal features are disabled
    if (field_nm === 'impervious_area' || field_nm === 'pervious_area') {
        valid_bol = validateProjectAreaAndArealFeatures();
        if (valid_bol === false) { return false; }
    }

    // this is the drop-down on the Structure Costs page
    if (field_nm === 'structure_select') {
        let fields = scenario_template.siteData.cost_items.fields;
        fields.forEach(function(field_nm) {

            let inputFieldDom = document.getElementById('checkbox_' + field_nm);
            let inputFieldChecked = inputFieldDom.checked;

            //TODO: this is some extra logic to always show any row that has
            // non-blank data.  questionable functionality
            var inputs = ['conversion_factor','factor_assumption_tx','sizing_factor_k','sizing_factor_n','construction_cost_factor_equation'];
            inputs.forEach(function(input_name) {
                let elementObj = document.getElementById('ui_' + field_nm + '_' + input_name);
                if (elementObj && elementObj.value){
                    inputFieldChecked = true;
                }
            });
            // end questionable functionality

            let trDom = document.getElementById('tr_' + field_nm);

            if (inputFieldDom !== null && trDom !== null) {

                if (inputFieldChecked !== true) {

                    trDom.style.display = 'none';
                }
                else {
                    trDom.style.display =  '';
                }
            }
            else {
                window.alert("unable to find input field dom for 'checkbox_" + field_nm);
            }

        });

    }
    if (field_nm === 'toggle_structure_cost_items') {
        let toggleDom = document.getElementById(field_nm);
        let checked = toggleDom.checked;

        let fields = scenario_template.siteData.cost_items.fields;
        fields.forEach(function(field_nm) {

            let inputFieldDom = document.getElementById('checkbox_' + field_nm);
            let inputFieldChecked = inputFieldDom.checked;

            //TODO: this is some extra logic to always show any row that has
            // non-blank data.  questionable functionality
            let inputs = ['factor_assumption_tx',
                            'sizing_factor_k',
                            'sizing_factor_n'];
            inputs.forEach(function(input_name) {
                let elementObj = document.getElementById('ui_' + field_nm + '_' + input_name);
                if (elementObj && elementObj.value){
                    inputFieldChecked = true;
                }
            });
            // end questionable functionality

            let trDom = document.getElementById('tr_' + field_nm);

            if (inputFieldDom !== null && trDom !== null && toggleDom !== null) {
                if (checked === true) {
                    trDom.style.display = '';
                }
                else if (checked === false && inputFieldChecked === false){
                    trDom.style.display = 'none';
                }
                else if (inputFieldChecked === true) {
                    trDom.style.display =  '';
                }
            }
        });
    }

    /*
        For the Cost Item Unit Costs - if the user selects 'User' from the drop down list, then enable User Input and Year
        If they select a different item, then clear both those fields.

     */
    if (field_id.replace('_cost_source', '') !== field_id) {
        let field_nm = field_id.replace('_cost_source', '').replace('ui_', '');
        let inputFieldDom = document.getElementById(field_id);
        let inputFieldValue = inputFieldDom.value;
        let inputs = [
            'user_input_cost',
            'base_year'
        ];

        inputs.forEach(function(input_name) {
            var elementObj = document.getElementById('ui_' + field_nm + '_' + input_name);
            if (elementObj){
                if (inputFieldValue !== 'user') {
                        elementObj.disabled = true;
                        elementObj.style.textDecoration = 'line-through';
                }
                else {
                    elementObj.disabled = false;
                    elementObj.style.textDecoration = 'none';
                }
            }
        });
    }


    var suffix = ['area'];

    // this is a checkbox field - they are attached to area, length, and diameter fields TBD documentation
    if (field_nm === field_id && field_id.replace('checkbox_', '') !== field_id) {
        field_nm = field_id.replace('checkbox_','') ;

        var cost_items_fields = scenario_template.siteData.cost_items.fields;
        // if (cost_items_fields.includes(field_nm)) {
        if ($.inArray(field_nm, cost_items_fields)) {
            // let suffix = ['a_area', 'z_depth', 'd_density', 'n_number'];

            let inputFieldDom = document.getElementById('checkbox_' + field_nm);
            var inputFieldChecked = inputFieldDom.checked;

            //TODO: this is some extra logic to always show any row that has
            // non-blank data.  questionable functionality
            let inputs = ['conversion_factor',
                            'factor_assumption_tx',
                            'sizing_factor_k',
                            'sizing_factor_n',
                            'construction_cost_factor_equation'];
            inputs.forEach(function(input_name) {
                var elementObj = document.getElementById('ui_' + field_nm + '_' + input_name);
                if (elementObj && elementObj.value){
                    inputFieldChecked = true;
                }
            });
            // end questionable functionality
            var showAllCostItemsDom = document.getElementById('toggle_structure_cost_items');
            var showAllChecked = showAllCostItemsDom.checked;

            var trDom = document.getElementById('tr_' + field_nm);
            if (inputFieldDom !== null && trDom !== null) {
                if (showAllChecked === false && inputFieldChecked !== true) {
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
            if (suffix.hasOwnProperty(i)) {
                let inputFieldDom = document.getElementById('ui_' + field_nm + '_' + suffix[i]);
                if (inputFieldDom !== null) {
                    if (formField.checked !== true) {
                        inputFieldDom.disabled = true;
                        inputFieldDom.style.textDecoration = 'line-through';
                    } else {
                        inputFieldDom.disabled = false;
                        inputFieldDom.style.textDecoration = 'none';
                    }
                }
            }
        }


        valid_bol = validateProjectAreaAndArealFeatures();
        if (valid_bol === false) { return false; }
    }

    /*
    *
    * wonky, but we want to force the number 1 in these fields if they are set blank by the user
    * the field ids are ui_{structure.code}_{partial_field_nm}
     */
    function isNullOrEmpty(str){
        return !str||!str.trim();
    }

    var partial_field_nms = [
        'a_area',
        'z_depth',
        'd_density',
        'n_number'
    ];
    for (i in partial_field_nms){
        if (partial_field_nms.hasOwnProperty(i)) {
            var partial_field_nm = partial_field_nms[i];
            if (field_id.indexOf(partial_field_nm) > 0) {
                let inputFieldDom = document.getElementById(field_id);
                if (inputFieldDom !== null) {
                    let inputFieldValue = inputFieldDom.value;
                    if (isNullOrEmpty(inputFieldValue)) {
                        // set the field value to 1
                        inputFieldDom.value = (partial_field_nm === 'n_number') ? 0 : 1;
                    }
                }
            }
        }
    }
    return true;

}

function showErrorsById(domID, error)
{
    let errorDom = document.getElementById(domID);

    if (errorDom) {
        if (! error || error === null) {
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
    return obj.constructor === Array;
}




/* on each key-stroke, run a calculation each time there is an edit in a field */
function returnCalc(formField) {

    // var evt = formField || window.Event;
    // if (evt.keyCode == 13)
    // {
    //     runCalculate(formField);
    //     return false;
    // }

    if (window.event && window.event.keyCode === 13) {
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
    let structureCode = '';

    var inputDom = document.getElementById('ui_' + 'scenario_id');

    if (inputDom){
        scenario_id = inputDom.value;
    }

    var field_id = 'ui_structure_select'; // formFeature.id;
    var field_nm = field_id.replace('ui_','');

    // the project type setting affects which of the areal features are disabled
    if (field_nm === 'structure_select') {
        // get what the value was and store it for saving the thing
        // get what the new selected value is
        let inputDom = document.getElementById('ui_' + field_nm);
        structureCode = inputDom.value;
    }

    if (structureCode === '')
    {
        return;
    }

    // this is trying to get the costitem.code to use to update only that specific data
    let costitem_code = '';
    let form_feature_id = '';
    if (formFeature !== undefined && 'id' in formFeature)
    {
        form_feature_id = formFeature.id;

        let input_field_list = ['a_area', 'z_depth', 'd_density', 'n_number'];
        for (let i in input_field_list) {
            if (input_field_list.hasOwnProperty(i)) {
                let field_suffix = input_field_list[i];
                if (form_feature_id.endsWith('_' + field_suffix)) {
                    costitem_code = form_feature_id.replace('ui_', '').replace('_' + field_suffix, '');
                    break;
                }
            }
        }
        if (costitem_code === '')
        {
            if (form_feature_id.startsWith('checkbox_'))
            {
                costitem_code = form_feature_id.replace('checkbox_', '');
            }
        }
    }

    var url = URLS.scenario_structure_cost.replace('<int:pk>', scenario_id);
    url = url.replace('<str:structure_code>', structureCode);

    if (costitem_code !== '')
    {
        url = url + costitem_code + '/';
    }

    $.ajax(url, {
        contentType : 'application/json; charset=utf-8',
        type : 'GET',
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
            // set the field that shows what is selected and the area of
            let inputDom = document.getElementById('ui_structure_name_2');
            if (inputDom){
                 inputDom.textContent = 'Fetching ...';
            }
            inputDom = document.getElementById('ui_structure_area_2');
            if (inputDom){ inputDom.value = ''; }
            inputDom = document.getElementById('ui_structure_units_2');
            if (inputDom){ inputDom.innerHTML = ''; }
        },
        success: function (data) {
            populateStructureEquations(data);

            validateForm(formFeature);

            validateForm({id: 'ui_toggle_structure_cost_items'});
        },
        error: function(data) {
            showError(data);
        }
    });
}

function structureCostItemHelp(cost_item_code){
    var base_url = URLS.scenario_structure_help;
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
        let field_array = field_dict.fields;

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
        delete field_dict.fields;
    }

    function compileStructureCosts(structure, field_dict) {
        //what structure are they showing in the dropdown list
        var structure_name = document.getElementById('ui_structure_select').value;

        // if they haven't selected a structure from the list, return
        if (structure_name === '') {
            return;
        }

        let field_array = field_dict.fields;

        delete field_dict.fields;


        //store data in 'user_assumptions'
        field_dict.user_assumptions = {
            'structure': structure,
            'data': {}
        };

        field_array.forEach(function (cost_item) {
            var inputs = [
                'a_area',
                'z_depth',
                'd_density',
                'n_number',
            ];

            // don't return data if the checkbox is not checked
            var elementObj = document.getElementById('checkbox_' + cost_item);

            if (elementObj) {
                if (!field_dict.user_assumptions.data[cost_item]) {
                    field_dict.user_assumptions.data[cost_item] = {'checked': elementObj.checked};
                }
                var non_null_count = 0;
                inputs.forEach(function (input_name) {

                    var elementObj = document.getElementById('ui_' + cost_item + '_' + input_name);

                    if (!elementObj) {
                        field_dict.user_assumptions.data[cost_item][input_name] = 'NOT FOUND ui_' + cost_item + '_' + input_name;
                    } else {
                        var form_value = elementObj.value;
                        if (form_value === '') {
                            form_value = null;
                        } else {
                            non_null_count += 1;
                        }
                        field_dict.user_assumptions.data[cost_item][input_name] = form_value;
                    }

                });

                if (field_dict.user_assumptions.data[cost_item] === false && non_null_count === 0) {
                    delete (field_dict.user_assumptions.data[cost_item]);
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

        });
    }

    function compileCosts(cost_item_list, field_dict) {
        let field_array = cost_item_list;

        field_dict.unit_costs = {};
        field_array.forEach(function (element_name) {
            var inputs = [
                'cost_source',
                'user_input_cost',
                'base_year',
                'replacement_life',
                'o_and_m_pct'
            ];

            if (!field_dict.unit_costs[element_name]) {
                field_dict.unit_costs[element_name] = {};
            }
            inputs.forEach(function (input_name) {
                //this triggers using 2 other fields
                if (input_name === 'unit_costZZZZ') {
                    let elementObj = document.getElementById('ui_' + element_name + '_' + input_name);
                    if (!elementObj) {
                        field_dict.unit_costs[element_name].checkbox = 'NOT FOUND 2 for element ' + element_name + '_' + input_name;
                    } else {
                        field_dict.unit_costs[element_name].checkbox = elementObj.checked;
                    }
                } else {
                    let elementObj = document.getElementById('ui_' + element_name + '_' + input_name);
                    if (!elementObj) {
                        field_dict.unit_costs[element_name][input_name] = 'NOT FOUND 2 for element ' + element_name;
                    } else {
                        let form_value = elementObj.value;
                        if (form_value === '') {
                            form_value = null;
                        }
                        field_dict.unit_costs[element_name][input_name] = form_value;
                    }
                }
            });
        });
    }

    function compileStructure(field_dict) {
        let field_array = field_dict.fields;
        let input_dict = field_dict.inputs;

        field_array.forEach(function (element_name) {
            var inputs = input_dict[element_name];
            if (!field_dict[element_name]) {
                field_dict[element_name] = {};
            }
            inputs.forEach(function (input_name) {

                if (input_name === 'checkbox') {
                    let elementObj = document.getElementById('checkbox_' + element_name);
                    if (!elementObj) {
                        field_dict[element_name].checkbox = 'NOT FOUND for element ' + element_name;
                    } else {
                        field_dict[element_name].checkbox = elementObj.checked;
                    }
                } else {
                    let elementObj = document.getElementById('ui_' + element_name + '_' + input_name);
                    if (!elementObj) {
                        field_dict[element_name][input_name] = 'NOT FOUND for element ' + element_name;
                    } else {
                        field_dict[element_name][input_name] = elementObj.value;
                    }
                }
            });
        });
        delete field_dict.fields;
        delete field_dict.inputs;
    }

    function compileID(field_dict, element_name) {
        let elementObj = document.getElementById('ui_' + element_name);
        if (!elementObj) {
            field_dict[element_name] = 'NOT FOUND for element ' + element_name;
        } else {
            field_dict[element_name] = elementObj.value;
        }
    }



    compileID(scenario_template, 'scenario_id');
    compileID(scenario_template, 'project_id');

    //TODO: rename this scenario_info or similar
    compile(scenario_template.siteData.embedded_scenario);

    compileStructure(scenario_template.siteData.areal_features);

    delete scenario_template.siteData.areal_features.toggles;

    // get the data from the 'Structures' tab.  They are split into 2 bits for Conventional and Non-Conventional
    compileStructure(scenario_template.siteData.conventional_structures);

    compileStructure(scenario_template.siteData.nonconventional_structures);

    // this is the drop-down on the Structure Costs page
    var selectedStructureObj = document.getElementById('ui_structure_select');
    var selectedStructure = selectedStructureObj.value;

    var cost_item_list = scenario_template.siteData.cost_items.fields;
    // change this to compileStructureCosts
    compileStructureCosts(selectedStructure, scenario_template.siteData.cost_items);

    compileCosts(cost_item_list, scenario_template.siteData.cost_items);

    return scenario_template;
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
    let tab_id = getCookie('tab');

    document.getElementById("network_indicator").style.display = "";

    // only work on sections that are on the active_tab
    scenarioData.active_tab = tab_id;

    var json = JSON.stringify(scenarioData);

    var url = URLS.scenario_save;
    $.ajax(url, {
        data: JSON.stringify(json),
        contentType: 'application/json; charset=utf-8',
        type: 'POST',
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: function (data) {
            //alert(JSON.stringify(data));

            // if ('uiMessage' in data)
            // {
            //     //This was used when CREATE sucked
            //     // if ('redirect_required' in data['uiMessage'])
            //     // {
            //     //     //replaced with just plugging in the value into the DOM
            //     //     var url = data['uiMessage']['redirect_required']['redirect_to'];
            //     //     window.location.replace(url);
            //     //     // var inputDom = document.getElementById('ui_' + 'scenario_id');
            //     //     //
            //     //     // if (inputDom){
            //     //     //     inputDom.value = data['uiMessage']['redirect_required']['scenario_id'];
            //     //     // }
            //     //
            //     // }
            // }

            // this is really weak error handling
            var errors;
            var scenario_title_errors;
            if ('Error' in data) {
                if ('error_dom_id' in data.Error && data.Error.error_dom_id === 'scenario_title_validation_error') {
                    scenario_title_errors = data.Error;
                } else if ('message' in data.Error) {
                    errors = data.Error;
                }
            }

            // this hides the errors if there is none
            showErrorsById('general_validation_error', errors);
            showErrorsById('scenario_title_validation_error', scenario_title_errors);

            updateProjectTitle(data.siteData);
            updateStructureCostDropDown(data.siteData);
            document.getElementById("network_indicator").style.display = "none";
        },
        error: function (data) {
            showError(data);
        }
    });
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
function filterInput(textbox) {
    if (!textbox.hasOwnProperty("oldValue") || textbox.inputFilter(textbox.value)) {
        textbox.oldValue = textbox.value;
        textbox.oldSelectionStart = textbox.selectionStart;
        textbox.oldSelectionEnd = textbox.selectionEnd;
    } else {
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
                if (/^\d{0,2}\.\d{0,2}$/.test(value)) { return true; }
                if (/^(100|\d{0,2})$/.test(value)) { return true; }
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
                if (/^\d{0,5}$/.test(value)) { return true; }
                return false;
            });
            break;
          case (field.match(/(_base_year)$/) || {}).input:
            setInputFilter(document.getElementById('ui_' + field), function (value) {
                if (/^\d{1,4}$/.test(value)) {
                    // if (len(value) == 4 & value >= 1000 & (value < 1990 || value >= 2020)) {
                    //     return false;
                    // }
                    if (value <= 2030) { //timebomb set for 2030?????
                        return true;
                    }
                    return false;
                }
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
                }
                return false;
            });
            break;
          default:
            // console.log("Didn't match '" + field + "'");
            break;
        }
    }

    function set_structures_input_filter(structures){
        for (let structure in structures) {
            if (structures.hasOwnProperty(structure)) {
                // each Areal Feature has a button
                let domElement = document.getElementById('checkbox_' + structure);
                if (!domElement) {
                    window.alert("There is no Structure button: 'checkbox_" + structure + "'");
                } else {
                    // Adds 'Check this to enable input for this areal feature'
                    domElement.title = open_structure_checkbox_title(structure);
                }

                var fields = structures[structure];
                fields.forEach(function (field) {
                    if (field !== 'checkbox') {
                        setFieldInputFilter(structure + '_' + field);
                    }
                });
            }
        }
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
    *  this uses the scenario template to set input filters
    *
    *
     */

    var scenario_template = scenarioTemplateJSON();

    var scenario_fields = scenario_template.siteData.embedded_scenario.fields;

    scenario_fields.forEach(function(field) {
        setFieldInputFilter(field);
    });

    // Set up the button and input text-box popup help text and input filter for each Areal Features
    var areal_features_fields = scenario_template.siteData.areal_features.fields;

    for (var i in areal_features_fields) {
        if (areal_features_fields.hasOwnProperty(i)) {
            let name = areal_features_fields[i];

            // each Areal Feature has a button
            let domElement = document.getElementById('checkbox_' + name);
            if (!domElement) {
                window.alert("There is no Areal Feature button: 'checkbox_" + name + "'");
            } else {
                // Adds 'Check this to enable input for this areal feature'
                domElement.title = open_af_button_title(name);
            }

            // and a text-box called 'ui_' name
            domElement = document.getElementById('ui_' + name + '_area'); //TODO
            if (!domElement) {
                window.alert("There is no Areal Feature text-box: 'ui_" + name + "'");
            } else {
                // set the input filter to a float
                setInputFilter(domElement, function (value) {
                    return (/^\d{0,5}\.?\d{0,2}$/.test(value));
                });
            }
        }
    }

    set_structures_input_filter(scenario_template.siteData.conventional_structures.inputs);

    set_structures_input_filter(scenario_template.siteData.nonconventional_structures.inputs);

    //structure costs
    set_structure_costs_input_filter(scenario_template.siteData.cost_items.fields);

    // cost item unit costs
    set_costitem_unit_costs_input_filter(scenario_template.siteData.cost_items.fields);
}

/*

    This section has functionality that controls the display(sic/?).  It was in a separate file displaycontrols.js but
    I think the only reason was that this file seems too large.

 */

function setCookie(cname, cvalue, exdays) {
  let d = new Date();
  d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
  let expires = "expires="+d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

// using jQuery
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = $.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function open_structure_checkbox_title(structure){
    /* this seems random, like not functioning code */
     return "Check this to enable input for this structure";
}

// mouse-over text attached to each Areal Feature button
function open_af_button_title(button_context) {
    //TODO: implement logic to go get text for display
    return "Check this to enable input for this areal feature";
}

function open_costitem_help(button_context) {
    // get the id of the input that this label is connected too. i.e. ui_stormwater_wetland

    var id;
    var helpDom;
    if (typeof (button_context) === 'string') {
        id = button_context;
        helpDom = document.getElementById('CostItemItemUnitCostsHelpText');
    } else {
        id = button_context.id;
        id = id.replace('structure_costitem_', '');
        helpDom = document.getElementById('StructureCostItemHelpText');
    }

    if (helpDom.style.display === 'block') {
        // now see if they are toggling off an existing help section
        var helpSelectedDom = helpDom.querySelector('[id="' + id + '"]');

        if (helpSelectedDom !== null) {
            //helpSelectedDom.innerHTML = '';
            //helpSelectedDom.style.display = "none";
            helpSelectedDom.remove();
            if (helpDom.childElementCount === 1) {
                helpDom.style.display = 'none';
            }
            return;
        }
    }

    var base_url = URLS.costitem_help;
    var url = base_url + '/' + id + '/?format=html';

    $.ajax(url, {
        contentType: 'application/json; charset=utf-8',
        type: 'GET',
        async: false, // wait for the response
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: function (data) {
            helpDom.style.display = 'block';
            helpDom.innerHTML = helpDom.innerHTML + data;
        },
        error: function (data) {
            window.alert("unable to get structure cost item help for " + id);
        }
    });
}
