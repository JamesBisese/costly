    window.onload = init_results_compare;

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
    function retop_div(div_class){
        let max_height = 0;
        let max_top = 0;
        let elements = document.getElementsByClassName(div_class);
        for (let i = 0; i < elements.length; i++) {
            let height = elements[i].offsetTop;
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
        leftScenarioDiv = document.getElementsByClassName('scenario_1')[0];
        rightScenarioDiv = document.getElementsByClassName('scenario_2')[0];
        var leftHTML = leftScenarioDiv.innerHTML;
        // remove the button
        rightScenarioDiv.getElementsByClassName('buttonHolder')[0].innerHTML = '';

        leftScenarioDiv.innerHTML = rightScenarioDiv.innerHTML;

        rightScenarioDiv.innerHTML = leftHTML;

        captionTableDiv = rightScenarioDiv.getElementsByClassName('buttonHolder')[0];

        var buttonDiv = document.createElement("button");
        buttonDiv.type = "button";
        buttonDiv.classList.add("reorderButton");
        buttonDiv.addEventListener("click", reorderScenarios);

        var imageDiv = document.createElement("img");
        imageDiv.src = SETTINGS.URLS.IIS_PREFIX + "/static/scenario/images/swap.png";
        imageDiv.style.border = "0";
        imageDiv.style.width = "20";
        imageDiv.style.height = "20";
        buttonDiv.appendChild(imageDiv);

        captionTableDiv.appendChild(buttonDiv);

        compareScenarios();
        // get these divs to take up the same page height
        resize_div("caption_table2");
        resize_div("project_table");
        resize_div("design_elements");

        resize_div("pervious");
        resize_div("planning_and_design");
        resize_div("project_life_cycle_costs");

        resize_div("construction_costs");
        resize_div("o_and_m_costs");
        resize_div("life_cycle_costs");

        // resize_div("areal_features");

        return;
    }
    function init_results_compare() {
        // get these divs to take up the same page height
        resize_div("caption_table2");
        resize_div("project_table");
        resize_div("design_elements");

        resize_div("pervious");
        resize_div("planning_and_design");
        resize_div("project_life_cycle_costs");

        resize_div("construction_costs");
        resize_div("o_and_m_costs");
        resize_div("life_cycle_costs");

        //resize_div("areal_features");

        // add a 'switch-sides' button to the top left side of the
        // right side scenario
        rightScenarioDiv = document.getElementsByClassName('scenario_2')[0];

        captionTableDiv = rightScenarioDiv.getElementsByClassName('buttonHolder')[0];

        var buttonDiv = document.createElement("button");
        buttonDiv.type = "button";
        buttonDiv.classList.add("reorderButton");
        buttonDiv.addEventListener("click", reorderScenarios);

        var imageDiv = document.createElement("img");
        imageDiv.src = SETTINGS.URLS.IIS_PREFIX + "/static/scenario/images/swap.png";
        imageDiv.style.border = "0";
        imageDiv.style.width = "20";
        imageDiv.style.height = "20";
        buttonDiv.appendChild(imageDiv);

        captionTableDiv.appendChild(buttonDiv);

    };
    function compareScenarios(button_context) {
        leftScenarioDiv = document.getElementsByClassName('scenario_1')[0];
        rightScenarioDiv = document.getElementsByClassName('scenario_2')[0];

        leftScenarioID = leftScenarioDiv.getElementsByClassName('scenario_id')[0].innerHTML;
        rightScenarioID = rightScenarioDiv.getElementsByClassName('scenario_id')[0].innerHTML;

        var url = SETTINGS.URLS.scenario_compare_column + leftScenarioID.toString() + ',' + rightScenarioID.toString();

       $.ajax(url, {
            type : 'GET',
            async: false, // wait for the response
            success: function (data) {
                compareDiv = document.getElementsByClassName('scenario_compare')[0];
                compareDiv.innerHTML = data;
                HideLoading();
            },
            error: function(data) {
                return "unable to get comparison results TBD";
                HideLoading();
            }
        });

        return;
    }

    function ShowLoading() {
        let loading = document.getElementsByClassName('scenarioPair')[0];
        loading.style.backgroundColor = 'red';
    };
    function HideLoading() {
        let loading = document.getElementsByClassName('scenarioPair')[0];
        loading.style.backgroundColor = '';
    };