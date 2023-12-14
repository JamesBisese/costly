/*jshint esversion: 6 */
/*jshint strict:false */
/*globals $:false */

let URLS = null; // this gets set via another javascript file sourced before this file
URLS = SETTINGS.URLS;

    window.onload = init_results_compare;

    $(document).ready(function() {
      // $('button:contains("Areal Features")').css({'color': 'red'});
    });

    function resize_div(div_class){
        let max_height = 0;
        let max_top = 0;
        let elements = document.getElementsByClassName(div_class);
        for (let i = 0; i < elements.length; i++) {
            let height = elements[i].offsetHeight;
            if (height > max_height){
                max_height = height;
            }
        }

        for (let i = 0; i < elements.length; i++) {
            elements[i].style.height = max_height;
        }
        for (let i = 0; i < elements.length; i++) {
            let top = elements[i].offsetTop;
            if (top > max_top){
                max_top = top;
            }
        }
        for (let i = 0; i < elements.length; i++) {
            elements[i].style.top = max_top;
        }
    }


    function reorderScenarios(button_context) {
        ShowLoading();
        let leftScenarioDiv = document.getElementsByClassName('scenario_1')[0];
        let rightScenarioDiv = document.getElementsByClassName('scenario_2')[0];
        let leftHTML = leftScenarioDiv.innerHTML;
        // remove the button
        rightScenarioDiv.getElementsByClassName('buttonHolder')[0].innerHTML = '';

        leftScenarioDiv.innerHTML = rightScenarioDiv.innerHTML;

        rightScenarioDiv.innerHTML = leftHTML;

        let captionTableDiv = rightScenarioDiv.getElementsByClassName('buttonHolder')[0];

        let buttonDiv = document.createElement("button");
        buttonDiv.type = "button";
        buttonDiv.classList.add("reorderButton");
        buttonDiv.addEventListener("click", reorderScenarios);

        let imageDiv = document.createElement("img");
        imageDiv.src = URLS.IIS_PREFIX + "/static/scenario/images/swap.png";
        imageDiv.style.border = "0";
        imageDiv.style.width = "20";
        imageDiv.style.height = "20";
        buttonDiv.appendChild(imageDiv);

        captionTableDiv.appendChild(buttonDiv);

        compareScenarios();
        // get these divs to take up the same page height
        resize_divs();
    }

    function init_results_compare() {
        // get these divs to take up the same page height
        resize_divs();

        //resize_div("areal_features");

        // add a 'switch-sides' button to the top left side of the
        // right side scenario
        let rightScenarioDiv = document.getElementsByClassName('scenario_2')[0];

        let captionTableDiv = rightScenarioDiv.getElementsByClassName('buttonHolder')[0];

        let buttonDiv = document.createElement("button");
        buttonDiv.type = "button";
        buttonDiv.classList.add("reorderButton");
        buttonDiv.addEventListener("click", reorderScenarios);

        let imageDiv = document.createElement("img");
        imageDiv.src = URLS.IIS_PREFIX + "/static/scenario/images/swap.png";
        imageDiv.style.border = "0";
        imageDiv.style.width = "20";
        imageDiv.style.height = "20";
        buttonDiv.appendChild(imageDiv);

        captionTableDiv.appendChild(buttonDiv);
    }

    function resize_divs()
    {
        resize_div("caption_table2");
        resize_div("project_table");
        resize_div("design_elements");

        resize_div("pervious");
        resize_div("planning_and_design");
        resize_div("project_life_cycle_costs");

        resize_div("construction_costs");
        resize_div("o_and_m_costs");
        resize_div("life_cycle_costs");
    }

    function compareScenarios(button_context) {
        let leftScenarioDiv = document.getElementsByClassName('scenario_1')[0];
        let rightScenarioDiv = document.getElementsByClassName('scenario_2')[0];

        let leftScenarioID = leftScenarioDiv.getElementsByClassName('scenario_id')[0].innerHTML;
        let rightScenarioID = rightScenarioDiv.getElementsByClassName('scenario_id')[0].innerHTML;

        let url = URLS.scenario_compare_column + leftScenarioID.toString() + ',' + rightScenarioID.toString();

       $.ajax(url, {
            type : 'GET',
            async: false, // wait for the response
            success: function (data) {
                let compareDiv = document.getElementsByClassName('scenario_compare')[0];
                compareDiv.innerHTML = data;
                HideLoading();
            },
            error: function() {
                return "unable to get comparison results TBD";
                // HideLoading();
            }
        });
    }

    function ShowLoading() {
        let loading = document.getElementsByClassName('scenarioPair')[0];
        loading.style.backgroundColor = 'red';
    }

    function HideLoading() {
        let loading = document.getElementsByClassName('scenarioPair')[0];
        loading.style.backgroundColor = '';
    }

    /* open and close the details parts.
     *  this relies on the next dom node being the thing to collapse,
     *  and the first class name being the 'name' to use */
    function toggleDetail(element, boolOpen) {

        let className = element.nextElementSibling.classList[0];

        let elements = document.getElementsByClassName(className);

        if (elements.length <= 0) {
            return;
        }
        let i;
        // let isShowing = elements[0].classList.contains("w3-show");
        for (i = 0; i < elements.length; i++) {
            let classList = elements[i].className.split(" ");
            if (boolOpen === true && classList.indexOf("w3-show") === -1) {
                elements[i].className += " " + "w3-show";
            } else if (boolOpen === false && classList.indexOf("w3-show") !== -1) {
                elements[i].className = elements[i].className.replace(/\bw3-show\b/g, "");
            }
        }
        /* if isShowing == true then we are closing.  collapse to 0 height */
        if (boolOpen === true) {
            let max_height = 0;

            for (let i = 0; i < elements.length; i++) {
                let height = elements[i].offsetHeight;

                if (height > max_height) {
                    max_height = height;
                }
            }
            for (let i = 0; i < elements.length; i++) {
                elements[i].style.height = max_height;
            }
        } else {
            for (let i = 0; i < elements.length; i++) {
                elements[i].style.height = 'unset';
            }
        }
    }


    function expandAllDetail(element) {
        let resultDetails = document.getElementsByClassName('resultDetails');
        for (let j = 0; j < resultDetails.length; j++) {
            let kbButtons = resultDetails[j].getElementsByClassName("w3-container-button");
            for (let i = 0; i < kbButtons.length; i++) {
                let classList = kbButtons[i].className.split(" ");
                if (classList.indexOf("w3-button-open") === -1) {
                    kbButtons[i].className += " " + "w3-button-open";
                }
                toggleDetail(kbButtons[i], true);
            }
        }
        // let button_text = 'Areal Features';
        let top_of_areal_features = $('button:contains("Land Area")').offset().top;
        let areal_features_dom = document.getElementsByClassName('areal_features');
        // areal_features_dom[2].clientTop = top_of_areal_features;
        resultDetails[2].style.top = top_of_areal_features;
    }


    function collapseAllDetail(element) {
        let resultDetails = document.getElementsByClassName('resultDetails');
        for (let j = 0; j < resultDetails.length; j++) {
            let kbButtons = resultDetails[j].getElementsByClassName("w3-container-button");
            for (let i = 0; i < kbButtons.length; i++) {
                let classList = kbButtons[i].className.split(" ");
                if (classList.indexOf("w3-button-open") !== -1) {
                    kbButtons[i].className = kbButtons[i].className.replace(/\bw3-button-open\b/g, "");
                }
                toggleDetail(kbButtons[i], false);
            }
        }
    }
