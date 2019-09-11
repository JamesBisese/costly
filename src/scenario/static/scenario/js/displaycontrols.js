

function setCookie(cname, cvalue, exdays) {
  var d = new Date();
  d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
  var expires = "expires="+d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
  var name = cname + "=";
  var ca = document.cookie.split(';');
  for(var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}


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
	    alert("toggleHelpText('" + mydivId + "') unable to find HelpText div");
    }
    else {
        if (x.style.display === "none") {
            x.style.display = "block";
        } else {
            x.style.display = "none";
        }
    }
}
function named_hover_out(mydivId) {

	var something = document.getElementById(mydivId);
	something.style.display = "none";
}
function named_hover(mydivId) {
	var something = document.getElementById(mydivId);
	something.style.display = "block";
}


function toggleDescription(d) {
    var description = document.getElementById(d);
    if (description.style.display != 'block') {
        description.style.display = 'block';
    }
    else {
        description.style.display = 'none';
    }
}

function toggleInfobox(d) {
    var description = document.getElementById(d);
    var os = Number(document.getElementById('inputs').scrollTop) + 50;
    os = os + 'px';
    if (description.style.display != 'block') {
        description.style.display = 'block';
        description.style.position = 'absolute';
        description.style.width = '300px';
        description.style.left = '100px';
        description.style.top = os;
    }
    else {
        description.style.display = 'none';
    }
}

// Toggle Structure Help. Open clicked structure(, and close all others ???)
// use the string to find the help section (which found looking for an ID which is the same string preceeded by 'cs_')

function close_structure_help(button_context) {
    button_context.parentElement.style.display = 'none';
    return;
}
function open_areal_features_help(button_context){
    open_structure_help(button_context, "areal_features_header");
}

/*

create this

<div id="help_stormwater_wetland" class="conventional_structure_help" style="display:none;">
    <button type="button" onclick="close_cs_help(this);" class="closebutton">
        <img src="{% static 'scenario/images/close2.gif' %}" style="border:0;">
    </button>
    <h4>Title TBD</h4>
    Content TBD
</div>


 */

function open_nonconventional_structure_help(button_context) {
    open_structure_help(button_context, 'nonconventional')
}
function open_conventional_structure_help(button_context) {
    open_structure_help(button_context, 'conventional')
}


function open_structure_help(button_context, type){

    var sibling_id = button_context.firstElementChild.firstElementChild.id;
    var structure_id = sibling_id.replace('checkbox_', '');

    var sourceContentDiv = document.getElementById("help_" + structure_id + "_innerHTML");

    var help_div_id = "help_" + structure_id;

    newStructureHelpDiv = document.getElementById(help_div_id);

    if (sourceContentDiv !== null){
        if (sourceContentDiv.style.display == "none"){
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

    pageHelpDiv = document.getElementById(page_help_div_id);
    topAlignDiv = document.getElementById(top_align_div_id);

    var sourceTitleContentDiv;
    sourceTitleContentDivs = sourceContentDiv.getElementsByClassName(["title"]);
    if (sourceTitleContentDivs.length == 1){
        sourceTitleContentDiv = sourceTitleContentDivs[0];
    }

    var buttonDiv = document.createElement("button");
    buttonDiv.type = "button";
    buttonDiv.classList.add("closebutton");
    buttonDiv.addEventListener("click", close_cs_help);

    var imageDiv = document.createElement("img");
    imageDiv.src = "/static/scenario/images/close2.gif";
    imageDiv.style.border = "0";
    buttonDiv.appendChild(imageDiv);

    sourceContentDiv.classList.add("conventional_structure_help");
    sourceTitleContentDiv.appendChild(buttonDiv);
    sourceTitleContentDiv.style.fontSize = "18px";
    sourceTitleContentDiv.style.fontWeight = "bold";

    // add a tag to the picture
    picrightDivs = sourceContentDiv.getElementsByClassName(["picright"]);
    if (picrightDivs.length == 1){
        var captionDiv = document.createElement("p");
        captionDiv.innerHTML = "Jenn Lenart, Tetra Tech, INC";
        captionDiv.classList.add("source");
        picrightDivs[0].appendChild(captionDiv);
    }

    sourceContentDiv.style.display = "";
}

//poorly functioning because I cant' get positioning correct
function open_structure_help2(button_context, type){

    var sibling_id = button_context.firstElementChild.firstElementChild.id;
    var structure_id = sibling_id.replace('checkbox_', '');

    var help_div_id = "help_" + structure_id;
    newStructureHelpDiv = document.getElementById(help_div_id);
    if (newStructureHelpDiv !== null){
        if (newStructureHelpDiv.style.display == "none"){
            newStructureHelpDiv.style.display = "";
        }
        else {
            newStructureHelpDiv.style.display = "none";
        }
        return;
    }

    var page_help_div_id = "structures_help_col";
    var top_align_div_id = type + "_structure_header";
    var title_tx = "TBD";
    pageHelpDiv = document.getElementById(page_help_div_id);
    topAlignDiv = document.getElementById(top_align_div_id);

    sourceContentDiv = document.getElementById("help_" + structure_id + "_innerHTML");
    sourceTitleContentDiv = sourceContentDiv.getElementsByClassName(["title"]);
    if (sourceTitleContentDiv.length == 1){
        title_tx = sourceTitleContentDiv[0].innerHTML;
        sourceTitleContentDiv[0].style.display = "none";
    }

    var helpDiv = document.createElement("div");
    helpDiv.id = help_div_id;
    helpDiv.classList.add("conventional_structure_help");
    helpDiv.style.display = "none";

    var buttonDiv = document.createElement("button");
    buttonDiv.type = "button";
    buttonDiv.classList.add("closebutton");
    buttonDiv.addEventListener("click", close_cs_help);

    var imageDiv = document.createElement("img");
    imageDiv.src = "/static/scenario/images/close2.gif";
    imageDiv.style.border = "0";
    buttonDiv.appendChild(imageDiv);

    helpDiv.appendChild(buttonDiv);

    var h4Div = document.createElement("h4");
    h4Div.innerHTML = title_tx;
    // h4Div.classList.add("closebutton");

    helpDiv.appendChild(h4Div);

    var contentDiv = document.createElement("div");
    contentDiv.innerHTML = sourceContentDiv.innerHTML;
    contentDiv.classList.add("closebutton");

    helpDiv.appendChild(contentDiv);

    helpDiv.style.display = "";

    // helpDiv.style.top = topAlignDiv.offsetTop.toString() + "px";
    helpDiv.style.position = "absolute";

    pageHelpDiv.appendChild(helpDiv);


    // open_structure_help(button_context, "conventional_structure_header");
}
// function open_nonconventional_structure_help(button_context){
//     open_structure_help(button_context, "nonconventional_structure_header");
// }
// function open_structure_help(button_context, top_align_div_nm) {
//     // get the id of the input that this label is connected too. i.e. ui_stormwater_wetland
//     var sibling_id = button_context.firstElementChild.firstElementChild.id;
//     var structure_id = sibling_id.replace('checkbox_', 'help_');
//     var help_section = document.getElementById(structure_id);
//
//     var button_parent_div = button_context.parentElement;
//
//     if(top_align_div_nm !== undefined){
//         test_div = document.getElementById(top_align_div_nm);
//         if (test_div !== undefined)
//         {
//             button_parent_div = test_div;
//         }
//     }
//
//     if (! help_section){
//         alert("There is no help section found for sibling_id: '" + sibling_id + "'");
//     }
//     else {
//         help_section.style.display = (help_section.style.display == 'block') ? 'none' : 'block';
//         help_section.style.top = button_parent_div.offsetTop.toString() + "px";
//         help_section.style.position = "absolute";
//     }
// }
function toggle_structure_help(cs_option, button_context) {

    if (button_context != null)
    {
        // get the id of the input that this label is connected too. i.e. ui_stormwater_wetland
        sibling_id = button_context.nextElementSibling.id;

        if (button_context.classList.contains("closebutton"))
        {
            button_context.parentElement.style.display = 'none'
            return;
        }
    }



    var structure_id = 'cs_' + cs_option;
    var help_section = document.getElementById(structure_id);

    if (! help_section){
        alert("There is no help section found for cs_option: '" + cs_option + "'");
    }
    else {
        help_section.style.display = (help_section.style.display == 'block') ? 'none' : 'block';

        for (var i in arr_conventional_structures) {

            if (cs_option != arr_conventional_structures[i]) {
                var structure_id = 'cs_' + arr_conventional_structures[i];
                var help_section = document.getElementById(structure_id);

                if (help_section) {
                    help_section.style.display = "none";
                }

                //TODO would it be best to display the help stuff at the page height level as the link used to access it?
                //document.getElementById('inputs').scrollTop = 0;
            }
        }
    }
}


// Toggle Conventional Structure Help. Open clicked structure(, and close all others ???)
// use the string to find the help section (which found looking for an ID which is the same string preceeded by 'cs_')

function close_cs_help(button_context) {
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
function open_cs_help(button_context) {
    // get the id of the input that this label is connected too. i.e. ui_stormwater_wetland
    var sibling_id = button_context.previousElementSibling.id;
    var structure_id = sibling_id.replace('ui_', 'cs_');
    var help_section = document.getElementById(structure_id);

    if (! help_section){
        alert("There is no help section found for sibling_id: '" + sibling_id + "'");
    }
    else {
        help_section.style.display = (help_section.style.display == 'block') ? 'none' : 'block';
    }
}
function open_cost_help(button_context) {
    // get the id of the input that this label is connected too. i.e. ui_stormwater_wetland
    var id = button_context.id;
    var help_id = id + '_help';
    var help_section = document.getElementById(help_id);

    if (! help_section){
        alert("There is no cost help section found for id: '" + id + "'");
    }
    else {
        help_section.style.display = (help_section.style.display == 'block') ? 'none' : 'block';
    }
}

function open_costitem_help(button_context) {
    // get the id of the input that this label is connected too. i.e. ui_stormwater_wetland

    var id;
    var helpDom;
    if (typeof(button_context) == 'string')
    {
        id = button_context;
        helpDom = document.getElementById('CostItemItemUnitCostsHelpText');
    }
    else
    {
        id = button_context.id;
        id = id.replace('structure_costitem_', '');
        helpDom = document.getElementById('StructureCostItemHelpText');
    }



    if (helpDom.style.display == 'block')
    {
        // now see if they are toggling off an existing help section
        var helpSelectedDom = helpDom.querySelector('[id="' + id + '"]');

        if (helpSelectedDom != undefined)
        {
            helpDom.innerHTML = '';
            helpDom.style.display = "none";
            return;
        }
    }
    // else
    // {
    //     help_section.style.display = "block";
    // }

    var base_url = SETTINGS.URLS.costitem_help;
    var url = base_url + '/' + id + '/?format=html';

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
            // return data;
            //alert("The costitem help found for id is: '" + data + "'");
            helpDom.style.display = 'block'
            helpDom.innerHTML = helpDom.innerHTML + data;


        },
        error: function(data) {
            alert( "unable to get structure cost item help for " + cost_item_code);
        }
    });

    // var help_id = id + '_help';
    // var help_section = document.getElementById('StructureCostsHelpText');
    //
    // // if (! help_section){
    // //     alert("There is no costitem help found for id: '" + id + "'");
    // // }
    // // else {
    //     alert("The costitem help found for id is: '" + help_text + "'");
    //
    // // }
}

function close_ci_help(button_context) {
    button_context.parentElement.style.display = 'none';

    var helpDom = document.getElementById('StructureCostItemHelpText');

    //TODO: figure out how to allow multiple help things to show and only close if there are none left
    if (helpDom.style.display == 'block')
    {
        // now see if they are toggling off an existing help section
        var helpSelectedDom = helpDom.querySelector('[id="' + id + '"]');

        if (helpSelectedDom != undefined)
        {
            helpDom.style.display = "none";
            return;
        }
    }

    return;
}

function toggle_cs_help(cs_option, button_context) {

    if (button_context != null)
    {
        // get the id of the input that this label is connected too. i.e. ui_stormwater_wetland
        sibling_id = button_context.previousElementSibling.id;

        if (button_context.classList.contains("closebutton"))
        {
            button_context.parentElement.style.display = 'none'
            return;
        }
    }



    var structure_id = 'cs_' + cs_option;
    var help_section = document.getElementById(structure_id);

    if (! help_section){
        alert("There is no help section found for cs_option: '" + cs_option + "'");
    }
    else {
        help_section.style.display = (help_section.style.display == 'block') ? 'none' : 'block';

        // if (help_section.style.display == 'block')
        // {
        //     help_section.style.display = "none";
        // }
        // else
        // {
        //     help_section.style.display = "block";
        // }


        for (var i in arr_conventional_structures) {

            if (cs_option != arr_conventional_structures[i]) {
                var structure_id = 'cs_' + arr_conventional_structures[i];
                var help_section = document.getElementById(structure_id);

                if (help_section) {
                    help_section.style.display = "none";
                }

                //TODO would it be best to display the help stuff at the page height level as the link used to access it?
                //document.getElementById('inputs').scrollTop = 0;
            }
        }
    }
}

function open_af_help(button_context) {
    // get the id of the input that this button is connected too. i.e. button_stormwater_management_feature
    var structure_id = button_context.replace('button_', 'af_');
    var help_section = document.getElementById(structure_id);

    if (! help_section){
        alert("There is no help section found for Areal Feature: '" + button_context.replace('button_', '') + "'");
    }
    else {
        help_section.style.display = (help_section.style.display == 'block') ? 'none' : 'block';
    }
}

// mouse-over text attached to each Areal Feature button
function open_af_button_title(button_context) {
    //TODO: implement logic to go get text for display
    return "mouse_over button place-holder text: " + button_context;
}
// mouse-over text attached to each Areal Feature input box
function open_af_input_title(button_context) {
    //TODO: implement logic to go get text for display
    return "mouse_over input place-holder text: " + button_context;
}

function toggleCol2(bmp) {
    var bmpdescription;
    var bmps = arr_bmps; // get global array
    bmps[bmps.length] = 'all';
    for (var bmpname in bmps) {
        bmpdescription = 'gd_' + bmps[bmpname];
        if (document.getElementById(bmpdescription)) {
            var x = document.getElementById(bmpdescription);

            if (bmp == bmps[bmpname]) {

                if (x.style.display === "none") {
                    x.style.display = "block";
                } else {
                    x.style.display = "none";
                }
                //TODO would it be best to display the help stuff at the page height level as the link used to access it?
                document.getElementById('inputs').scrollTop = 0;
            }
            else {
                x.display = 'none';
            }
        }
    }
}



// function toggleInputPane(pane) {
// 	var panes = new Array ('lotinfo','conventional','green','advanced', 'result'); //jab removed 'start','predevelopment','goal'
// 	for (var i in panes) {
// 		if (pane==panes[i]) {
// 			document.getElementById('input-' + panes[i]).style.display = 'block';
// 			document.getElementById('inputlist-' + panes[i]).className = 'active';
// 		}
// 		else {
// 			document.getElementById('input-' + panes[i]).style.display = 'none';
// 			document.getElementById('inputlist-' + panes[i]).className = 'inactive';
// 		}
// 	}
// 	document.getElementById('inputs').scrollTop = 0;
// }

// function toggleResultPane(pane) {
// 	var panes = new Array ('volume-control','land-use','runoff','costs','benefits');
// 	for (var i in panes) {
// 		if (document.getElementById('result-' + panes[i])) {
// 			if (pane==panes[i]) {
// 				document.getElementById('result-' + panes[i]).style.display = 'block';
// 				document.getElementById('rlist-' + panes[i]).className = 'active';
// 			}
// 			else {
// 				document.getElementById('result-' + panes[i]).style.display = 'none';
// 				document.getElementById('rlist-' + panes[i]).className = 'inactive';
// 			}
// 		}
// 	}
// }

// function checkInputPane() {
// 	var panes = new Array ('lotinfo','conventional','green','advanced', 'result'); //'start','predevelopment','goal',
// 	var pane = 'start';
// 	for (var i in panes) {
// 		if (document.getElementById('input-' + panes[i]).style.display == 'block') {
// 			pane = panes[i];
// 		}
// 	}
// 	return pane;
// }

// function checkResultPane() {
// 	var panes = new Array ('volume-control','land-use','runoff','costs','benefits');
// 	var pane = 'volume-control';
// 	if (document.getElementById('result-volume-control')) {
// 		for (var i in panes) {
// 			if (document.getElementById('result-' + panes[i]).style.display == 'block') {
// 				pane = panes[i];
// 			}
// 		}
// 	}
// 	return pane;
// }

// function adjustPane(a) {
// 	// var minimumSize = 150;
// 	// var maximumSize = 900;
// 	// var increment = 100;
// 	// var pane = document.getElementById('inputs');
// 	// pane.style.height = '70%';
// 	// var paneHeight = parseInt(pane.style.height);
// 	// if (!a) {
// 	// 		pane.style.height = '700px';
// 	// }
// 	// if (a=='smaller') {
// 	// 	if (paneHeight > minimumSize + increment - 1) {
// 	// 		paneHeight = paneHeight - increment;
// 	// 		pane.style.height = paneHeight + 'px';
// 	// 	}
// 	// }
// 	// if (a=='larger') {
// 	// 	if (paneHeight < maximumSize - increment + 1) {
// 	// 		paneHeight = paneHeight + increment;
// 	// 		pane.style.height = paneHeight + 'px';
// 	// 	}
// 	// }
// }