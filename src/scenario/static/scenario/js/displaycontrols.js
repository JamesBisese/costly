/*jshint esversion: 6 */
/*jshint strict:false */
/*globals $:false */

function normal(mydiv) {

	var something = mydiv.parentElement.parentElement.parentElement.querySelector('.col2');
	something.style.display = "none";
}


function hover(mydiv) {
	var something = mydiv.parentElement.parentElement.parentElement.querySelector('.col2');
	something.style.display = "block";
}


function toggleHelpText(mydivId){
	var x = document.getElementById(mydivId);
	if (! x){
	    window.alert("toggleHelpText('" + mydivId + "') unable to find HelpText div");
    }
    else {
        if (x.style.display === "none") {
            x.style.display = "block";
        } else {
            x.style.display = "none";
        }
    }
}


function toggleDescription(d) {
    var description = document.getElementById(d);
    if (description.style.display !== 'block') {
        description.style.display = 'block';
    }
    else {
        description.style.display = 'none';
    }
}


function open_areal_features_help(button_context){
    open_structure_help(button_context, "areal_features_header");
}


function open_nonconventional_structure_help(button_context) {
    open_structure_help(button_context, 'nonconventional');
}


function open_conventional_structure_help(button_context) {
    open_structure_help(button_context, 'conventional');
}


function open_structure_help(button_context, type){

    var sibling_id = button_context.firstElementChild.firstElementChild.id;
    var structure_id = sibling_id.replace('checkbox_', '');

    var sourceContentDiv = document.getElementById("help_" + structure_id + "_innerHTML");

    var help_div_id = "help_" + structure_id;

    if (sourceContentDiv !== null){
        if (sourceContentDiv.style.display === "none"){
            sourceContentDiv.style.display = "";
        }
        else {
            sourceContentDiv.style.display = "none";
        }
        //it's already been set up
        if (sourceContentDiv.getElementsByClassName("closebutton").length > 0)
        {
            return;
        }
    }

    var page_help_div_id = "structures_help_col";
    var top_align_div_id = type + "_structure_header";
    var title_tx = "TBD";

    let pageHelpDiv = document.getElementById(page_help_div_id);
    let topAlignDiv = document.getElementById(top_align_div_id);

    var sourceTitleContentDiv;
    let sourceTitleContentDivs = sourceContentDiv.getElementsByClassName(["title"]);
    if (sourceTitleContentDivs.length === 1){
        sourceTitleContentDiv = sourceTitleContentDivs[0];
    }

    var buttonDiv = document.createElement("button");
    buttonDiv.type = "button";
    buttonDiv.classList.add("closebutton");
    buttonDiv.addEventListener("click", close_cs_help);

    var imageDiv = document.createElement("img");
    imageDiv.src =  SETTINGS.URLS.IIS_PREFIX + "/static/scenario/images/close2.gif";
    imageDiv.style.border = "0";
    buttonDiv.appendChild(imageDiv);

    sourceContentDiv.classList.add("major_help");
    sourceTitleContentDiv.appendChild(buttonDiv);
    sourceTitleContentDiv.style.fontSize = "18px";
    sourceTitleContentDiv.style.fontWeight = "bold";

    // add a tag to the picture
    let picrightDivs = sourceContentDiv.getElementsByClassName(["picright"]);
    if (picrightDivs.length === 1){
        var captionDiv = document.createElement("p");
        captionDiv.innerHTML = "Jenn Lenart, Tetra Tech, INC";
        captionDiv.classList.add("source");
        picrightDivs[0].appendChild(captionDiv);
    }

    sourceContentDiv.style.display = "";
}


function close_cs_help(button_context) {
    // Toggle Conventional Structure Help. Open clicked structure(, and close all others ???)
    // use the string to find the help section (which found looking for an ID which is the same string preceeded by 'cs_')
    if (button_context.parentElement === undefined){
        //support new mouse click event
        button_context.currentTarget.parentElement.parentElement.style.display = 'none';
    }
    else
    {
        button_context.parentElement.style.display = 'none';
    }

    return;
}


function close_cost_item_help(button_context) {
    /* this is the close button on the Cost Item Unit Costs tab to close the help using the x  button */

    let id = button_context;

    // this is confusing. there are 2 ids used  CostItemItemUnitCostsHelpText and StructureCostItemHelpText
    // this moves up the stack and finds the correct id to use to find the dom that holds the help text

    // updated - now just remove the individual help, not the whole thing
    let helpDom = document.getElementById(button_context.parentElement.parentElement.id);
    //let helpDom = document.getElementById(button_context.parentElement.id);

    //TODO: figure out how to allow multiple help things to show and only close if there are none left
    if (helpDom.style.display === 'block')
    {
        // now see if they are toggling off an existing help section
        let item_id = button_context.parentElement.id;

        var helpSelectedDom = helpDom.querySelector('[id="' + item_id + '"]');

        if (helpSelectedDom !== null)
        {
            helpSelectedDom.remove();
            if (helpDom.childElementCount === 1)
            {
                helpDom.style.display = 'none';
            }
            return;
        }
    }
    return;
}

function close_ci_help(button_context) {
    /* this is the close button on the Cost Item Unit Costs tab to close the help using the x  button */

    let id = button_context;

    // this is confusing. there are 2 ids used this one and StructureCostItemHelpText
    let helpDom = document.getElementById('StructureCostItemHelpText');

    //TODO: figure out how to allow multiple help things to show and only close if there are none left
    if (helpDom.style.display === 'block')
    {
        // now see if they are toggling off an existing help section
        var helpSelectedDom = helpDom.querySelector('[id="' + id + '"]');

        if (helpSelectedDom !== null)
        {
            helpDom.innerHTML = '';
            helpDom.style.display = "none";
            return;
        }
    }
    return;
}

function collapseDetail(element) {
    /* open and close the details parts.
     *  this relies on the next dom node being the thing to collapse,
     *  and the first class name being the 'name' to use */

    let className = element.nextElementSibling.classList[0];

    var elements = document.getElementsByClassName(className);

    if (elements.length > 0){
        var i;
        var isShowing = elements[0].classList.contains("w3-show");
        for (let i = 0; i < elements.length; i++) {
            elements[i].classList.toggle("w3-show");

            let kbButton = elements[i].previousElementSibling;
            if (kbButton !== null)
            {
                var classList = kbButton.className.split(" ");
                if (classList.indexOf("w3-button-open") === -1) {
                    kbButton.className += " " + "w3-button-open";
                }
                else {
                    kbButton.className = kbButton.className.replace(/\bw3-button-open\b/g, "");
                }
            }

        }
        /* if isShowing == true then we are closing.  collapse to 0 height */
        if (isShowing === true)
        {
            for (let i = 0; i < elements.length; i++) {
                elements[i].style.height = 'unset';
            }
        }
        else
        {
            var max_height = 0;
            var max_top = 0;
            for (let i = 0; i < elements.length; i++) {
                var height = elements[i].offsetHeight;
                var top = elements[i].offsetTop;
                if (height > max_height){
                    max_height = height;
                }
                if (top > max_top){
                    max_top = top;
                }
            }
            for (let i = 0; i < elements.length; i++) {
                elements[i].style.height = max_height;
                // get the content in the comparison column to align using top
                if (elements[i].classList.contains("comparison_column")) {
                    elements[i].style.position = 'absolute';
                    elements[i].style.top = max_top;
                }
            }
        }

    }
}

/* open and close the details parts.
 *  this relies on the next dom node being the thing to collapse,
 *  and the first class name being the 'name' to use */
function toggleDetail(element, boolOpen) {

    let className = element.nextElementSibling.classList[0];

    var elements = document.getElementsByClassName(className);

    if (elements.length <= 0) {
        return;
    }
    var i;
    // var isShowing = elements[0].classList.contains("w3-show");
    for (i = 0; i < elements.length; i++) {
        var classList = elements[i].className.split(" ");
        if (boolOpen === true && classList.indexOf("w3-show") === -1){
            elements[i].className += " " + "w3-show";
        }
        else if (boolOpen === false && classList.indexOf("w3-show") !== -1) {
            elements[i].className = elements[i].className.replace(/\bw3-show\b/g, "");
        }
    }
    /* if isShowing == true then we are closing.  collapse to 0 height */
    if (boolOpen === true)
    {
        var max_height = 0;

        for (let i = 0; i < elements.length; i++) {
            var height = elements[i].offsetHeight;

            if (height > max_height){
                max_height = height;
            }
        }
        for (let i = 0; i < elements.length; i++) {
            elements[i].style.height = max_height;
        }
    }
    else {
        for (let i = 0; i < elements.length; i++) {
            elements[i].style.height = 'unset';
        }
    }
}


function expandAllDetail(element){
    var resultDetails = document.getElementsByClassName('resultDetails');
    for (var j = 0; j < resultDetails.length; j++)
    {
        let kbButtons = resultDetails[j].getElementsByClassName("w3-container-button");
        for (var i = 0; i < kbButtons.length; i++){
            var classList = kbButtons[i].className.split(" ");
            if (classList.indexOf("w3-button-open") === -1) {
                kbButtons[i].className += " " + "w3-button-open";
            }
            toggleDetail(kbButtons[i], true);
        }
    }
}


function collapseAllDetail(element){
    var resultDetails = document.getElementsByClassName('resultDetails');
    for (var j = 0; j < resultDetails.length; j++) {
        let kbButtons = resultDetails[j].getElementsByClassName("w3-container-button");
        for (var i = 0; i < kbButtons.length; i++) {
            var classList = kbButtons[i].className.split(" ");
            if (classList.indexOf("w3-button-open") !== -1) {
                kbButtons[i].className = kbButtons[i].className.replace(/\bw3-button-open\b/g, "");
            }
            toggleDetail(kbButtons[i], false);
        }
    }
}




//
// function toggle_structure_help(cs_option, button_context) {
//
//     if (button_context !== null)
//     {
//         // get the id of the input that this label is connected too. i.e. ui_stormwater_wetland
//         sibling_id = button_context.nextElementSibling.id;
//
//         if (button_context.classList.contains("closebutton"))
//         {
//             button_context.parentElement.style.display = 'none';
//             return;
//         }
//     }
//
//     let structure_id = 'cs_' + cs_option;
//     let help_section = document.getElementById(structure_id);
//
//     if (! help_section){
//         window.alert("There is no help section found for cs_option: '" + cs_option + "'");
//     }
//     else {
//         help_section.style.display = (help_section.style.display === 'block') ? 'none' : 'block';
//
//         for (var i in arr_conventional_structures) {
//
//             if (cs_option !== arr_conventional_structures[i]) {
//                 let structure_id = 'cs_' + arr_conventional_structures[i];
//                 let help_section = document.getElementById(structure_id);
//
//                 if (help_section) {
//                     help_section.style.display = "none";
//                 }
//
//                 //TODO would it be best to display the help stuff at the page height level as the link used to access it?
//                 //document.getElementById('inputs').scrollTop = 0;
//             }
//         }
//     }
// }

