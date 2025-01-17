/*jshint esversion: 6 */
/*jshint strict:false */
/*globals $:false */

// scenario_index.js
let URLS = null; // this gets set via another javascript file sourced before this file

$(function () {

    let is_superuser = false;

    URLS = SETTINGS.URLS;

    /* Binding */
    $(document).ready(function() {

        let inputDom = document.getElementById('is_superuser');

        is_superuser = (inputDom) ? true: false;

        inputDom = document.getElementById('project_id');

        let project_id;
        if (inputDom){
            project_id = inputDom.innerText;
        }

        loadTable(project_id);

        $('#compareScenarios2').addClass('disabled');
        $('#exportScenarios2').addClass('disabled');
        $('#exportScenariosExtended').addClass('disabled');
        // limit user to selecting 2 rows

        $('#scenario-table tbody').on( 'click', 'tr', function ()
        {
            //jab changed this to allow selecting more than 2 so the export will work
            //
            if($('.selected').length < 40 || $(this).hasClass('selected'))
            {
               $(this).toggleClass('selected');
            }

            if($('.selected').length > 0)
            {
                let table;
                let tblData;
                let scenario_id;

                if($('.selected').length === 1)
                {
                    table = $('#scenario-table').DataTable();
                    tblData = table.rows('.selected').data();
                    scenario_id = tblData[0].id;
                }
                if($('.selected').length === 2)
                {
                    $('#compareScenarios2').removeClass('disabled');
                }
                else if ($('.selected').length > 2)
                {
                    $('#compareScenarios2').addClass('disabled');
                }

               $('#exportScenarios2').removeClass('disabled');
               $('#exportScenariosExtended').removeClass('disabled');

                table = $('#scenario-table').DataTable();

                tblData = table.rows('.selected').data();

                let scenario_ids = [];
                $.each(tblData, function(i, val)
                {
                    let tmpData = tblData[i];
                    scenario_ids.push(tmpData.id);
                });

                let url = URLS.scenario_results + scenario_ids.join(',');

                document.getElementById("compareScenarios2").href= url ;

                // set the url for exporting 1 or 2 scenarios
                url = URLS.scenario_export_results + scenario_ids.join(',');

                document.getElementById("exportScenarios2").href= url ;

                // set the url for exporting 1 or 2 scenarios DETAIL view
                url = URLS.scenario_export_extended_excel_report + scenario_ids.join(',');

                document.getElementById("exportScenariosExtended").href= url ;
            }
            else
            {
                $('#compareScenarios2').addClass('disabled');
                $('#exportScenarios2').addClass('disabled');
                $('#exportScenariosExtended').addClass('disabled');
            }
        } );

        $('#compareScenarios').click( function ()
        {
            let table = $('#scenario-table').DataTable();

            let tblData = table.rows('.selected').data();
            let scenario_id = [];
            $.each(tblData, function(i, val)
            {
                let tmpData = tblData[i];
                scenario_id.push(tmpData.id);
            });

            let url = URLS.scenario_results + scenario_id.join(',');
            window.alert( 'compare scenarios at ' + url);
        } );
    });

    var loadTable = function(project_id) {

        let export_columns = [0, 1, 2, 3];

        let scenario_url = URLS.new_scenario_list.replace('<int:pk>', project_id);

        let options = {
            "serverSide": false,
            "responsive": true,
            "ajax": scenario_url,
            "paging": false,
            "info" : false,
            "dom": 'frtipB',
          "processing": true,
            'language': {
                'loadingRecords': '&nbsp;',
                'processing': "<span class='fa-stack fa-lg'><i class='fa fa-spinner fa-spin fa-stack-2x fa-fw'></i></span>&emsp;Processing ..."
            },
            "columns": [
                {"data": "id", "searchable": false},
                {"data": "scenario_title", "searchable": true},
                {"data": "nutrient_req_met", "searchable": false},
                {"data": "captures_90pct_storm", "searchable": false},
                {"data": "meets_peakflow_req", "searchable": false},
                {"data": "pervious_area",
                    "render": $.fn.dataTable.render.number( ',' ),
                    "searchable": false},
                {"data": "impervious_area",
                    "render": $.fn.dataTable.render.number( ',' ),
                    "searchable": false},
                {"data": "create_date", "searchable": true},
                {"data": "modified_date", "searchable": true},
                {"data": "id", "searchable": false, "sortable": false},
             ],
            "columnDefs": [
                {
                    "searchable": false,
                    "orderable": false,
                    "targets": 0
                },
                {
                    "targets": 9,
                    "sWidth": "250px",
                    "render": function (data, type, row) {

                        let duplicate_url = URLS.scenario_duplicate.replace('<int:pk>', data);
                        let update_url = URLS.scenario_update.replace('<int:pk>', data);
                        let delete_url = URLS.scenario_delete.replace('<int:pk>', data);

                        return '<button type="button" class="btn btn-primary btn-sm js-duplicate-scenario" data-url="' + duplicate_url + '">'+
                           '<span class="glyphicon glyphicon-duplicate"></span> Copy'+
                           '</button>' + '&nbsp;' +

                            '<a class="btn btn-warning btn-sm js-update-project" href="' + update_url + '">' +
                            '<span class="glyphicon glyphicon-pencil"></span> Edit' +
                            '</a>' + '&nbsp;' +

                            '<button type="button" class="btn btn-danger btn-sm js-delete-scenario" data-url="' + delete_url + '">'+
                           '<span class="glyphicon glyphicon-trash"></span> Delete'+
                           '</button>';
                    }
                },
            ],
            "order": [[ 1, 'asc' ]]
        };

        let table = $('#scenario-table').DataTable(options);

        table.on( 'order.dt search.dt', function () {
            table.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
            cell.innerHTML = i+1;
        } );
    } ).draw();

    };

    /* Functions */
    function showValidationErrors(error) {
        $("#help-block").text(error);
    }

    function clearValidationError() {
        $("#help-block").text();
    }

    /* generic */
    var loadForm = function () {
        let btn = $(this);
        $.ajax({
            url: btn.attr("data-url"),
            type: 'get',
            dataType: 'json',
            beforeSend: function () {
                $("#modal-scenario .modal-content").html("");
                $("#modal-scenario").modal("show");
                // $('#duplicate_scenario').css('display','none');
            },
            success: function (data) {
                $("#modal-scenario .modal-content").html(data.html_form);
            }
        });
    };

    /* generic with one extra step to reload the data table */
    var duplicateForm = function () {
        let btn = $(this);

        $.ajax({
            url: btn.attr("data-url"),
            type: 'get',
            dataType: 'json',
            data: $("scenario-duplicate-form").serialize(),
            beforeSend: function () {
                $("#modal-scenario .modal-content").html("");
                $("#modal-scenario").modal("show");
            },
            success: function (data) {
                // $("#modal-scenario .modal-content").html(data.html_form);
                if (data.form_is_valid) {
                    $("#modal-scenario").modal("hide");
                    $('#scenario-table').DataTable().ajax.reload();
                }
                else {
                  $("#modal-scenario .modal-content").html(data.html_form);
                }
            }
        });
    };

    /* ajax used when the modal is submitted */
    var submitForm = function () {
        let form = $(this);
        $.ajax({
            url: form.attr("action"),
            data: form.serialize(),
            type: form.attr("method"),
            dataType: 'json',
            success: function (data) {
                if (data.hasOwnProperty('exception')){
                    showValidationErrors(data.exception);
                }
                else {
                    if (data.form_is_valid) {
                        $("#modal-scenario").modal("hide");
                        $('#scenario-table').DataTable().ajax.reload();
                    }
                    else {
                      $("#modal-scenario .modal-content").html(data.html_form);
                    }
                }

            },
            error: function (res) {

                if (res.status === 422) {
                    let data = res.responseJSON;

                    for (let i in data) {
                        showValidationErrors(i, data[i][0]);
                    }
                }
            }
        });
        return false;
    };

    // Create scenario
    $("#create_scenario").on("click",  loadForm);
    $("#modal-scenario").on("submit", ".js-scenario-create-form", submitForm);

    // Duplicate scenario
    $("#scenario-table").on("click",  ".js-duplicate-scenario", duplicateForm);
    $("#modal-scenario").on("submit", ".js-scenario-duplicate-form", submitForm);

    // Delete scenario
    $("#scenario-table").on("click", ".js-delete-scenario", loadForm);
    $("#modal-scenario").on("submit", ".js-project-delete-form", submitForm);

});
