
// scenario_index.js

$(function () {

    var is_superuser = false;

    /* Binding */
    $(document).ready(function() {

        var inputDom = document.getElementById('is_superuser');

        is_superuser = (inputDom) ? true: false;

        var inputDom = document.getElementById('project_id');

        if (inputDom){
            project_id = inputDom.innerText;
        }

        loadTable(project_id);

        $('#compareScenarios').attr('disabled','disabled');
        $('#compareScenarios2').addClass('disabled');

        // limit user to selecting 2 rows
        $('#scenario-table tbody').on( 'click', 'tr', function ()
        {
            if($('.selected').length < 2 || $(this).hasClass('selected'))
            {
                    $(this).toggleClass('selected');
            }

            if($('.selected').length > 0)
            {
                if($('.selected').length == 1)
                {
                    var table = $('#scenario-table').DataTable();
                    var tblData = table.rows('.selected').data();
                    scenario_id = tblData[0]['id'];

                    // $('#duplicate_scenario').css('display','');
                    // $('#duplicate_scenario').attr('data-url',
                    //     SETTINGS.URLS.scenario_duplicate.replace('<int:pk>', scenario_id));
                }
                // else
                // {
                //     $('#duplicate_scenario').css('display','none');
                //
                // }
               $('#compareScenarios').removeAttr('disabled');
               $('#compareScenarios2').removeClass('disabled');

                var table = $('#scenario-table').DataTable();

                var tblData = table.rows('.selected').data();
                var scenario_id = [];
                $.each(tblData, function(i, val)
                {
                    tmpData = tblData[i];
                    scenario_id.push(tmpData['id'])
                });

                var url = SETTINGS.URLS.scenario_results + scenario_id.join(',');

                document.getElementById("compareScenarios2").href= url ;
            }
            else
            {
                // $('#duplicate_scenario').css('display','none');


                $('#compareScenarios').attr('disabled','disabled');
                $('#compareScenarios2').addClass('disabled');
            }
        } );

        $('#compareScenarios').click( function ()
        {
            var table = $('#scenario-table').DataTable();

            var tblData = table.rows('.selected').data();
            var scenario_id = [];
            $.each(tblData, function(i, val)
            {
                tmpData = tblData[i];
                scenario_id.push(tmpData['id'])
            });

            var url = SETTINGS.URLS.scenario_results + scenario_id.join(',');
            alert( 'compare scenarios at ' + url);
        } );
    });

    var loadTable = function(project_id) {

        var export_columns = [0, 1, 2, 3];

        //var scenario_url = SETTINGS.URLS.project_scenario_list_api.replace('<int:pk>', project_id);
        //scenario_url = scenario_url + "?format=datatables";

        var scenario_url = SETTINGS.URLS.new_scenario_list.replace('<int:pk>', project_id);;

        var options = {
            "serverSide": true,
            "responsive": true,
            "ajax": scenario_url,
            "paging": false,
            "info" : false,
            "dom": 'frtipB',
            // "buttons": [
            //     { 'extend': 'copy',  'exportOptions': {'columns': export_columns}},
            //     { 'extend': 'csv',   'exportOptions': {'columns': export_columns}},
            //     { 'extend': 'excel', 'exportOptions': {'columns': export_columns}},
            //     { 'extend': 'pdf',   'exportOptions': {'columns': export_columns}},
            //     { 'extend': 'print', 'exportOptions': {'columns': export_columns}},
            // ],
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
                {"data": "id", "searchable": false, "sortable": false},
             ],
            "columnDefs": [
                {
                    "searchable": false,
                    "orderable": false,
                    "targets": 0
                },
                {
                    "targets": 7,
                    "sWidth": "250px",
                    "render": function (data, type, row) {

                        var duplicate_url = SETTINGS.URLS.scenario_duplicate.replace('<int:pk>', data);
                        var update_url = SETTINGS.URLS.scenario_update.replace('<int:pk>', data);
                        var delete_url = SETTINGS.URLS.scenario_delete.replace('<int:pk>', data);

                        return '<button type="button" class="btn btn-primary btn-sm js-duplicate-scenario" data-url="' + duplicate_url + '">'+
                           '<span class="glyphicon glyphicon-duplicate"></span> Copy'+
                           '</button>' + '&nbsp;' +

                            '<a class="btn btn-warning btn-sm js-update-project" href="' + update_url + '">' +
                            '<span class="glyphicon glyphicon-pencil"></span> Edit' +
                            '</a>' + '&nbsp;' +

                            '<button type="button" class="btn btn-danger btn-sm js-delete-scenario" data-url="' + delete_url + '">'+
                           '<span class="glyphicon glyphicon-trash"></span> Delete'+
                           '</button>'
                    }
                },
            ],
            "order": [[ 1, 'asc' ]]
        };

        // hide the user column if the user is not a super user - the values should all be that particular user
        // if (is_superuser == false)
        // {
        //     options['columnDefs'].push({
        //             "targets": 1,
        //             "visible": false
        //         }
        //     )
        // }

        var table = $('#scenario-table').DataTable(options);

        table.on( 'order.dt search.dt', function () {
            table.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
            cell.innerHTML = i+1;
        } );
    } ).draw();

    };

    /* Functions */
    function showValidationErrors(error) {
        // var group = $("#input-group");
        // group.addClass('has-error');
        // group.find('.help-block').text(error);
        $("#help-block").text(error)
    }

    function clearValidationError() {
        // var group = $("#input-group");
        // group.removeClass('has-error');
        // group.find('.help-block').text('');
        $("#help-block").text()
    }

    /* generic */
    var loadForm = function () {
        var btn = $(this);
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
        var btn = $(this);

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
        var form = $(this);
        $.ajax({
            url: form.attr("action"),
            data: form.serialize(),
            type: form.attr("method"),
            dataType: 'json',
            success: function (data) {
                if (data.hasOwnProperty('exception')){
                    showValidationErrors(data['exception'])
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

                if (res.status == 422) {
                    var data = res.responseJSON;

                    for (let i in data) {
                        showValidationErrors(i, data[i][0])
                    }
                }
            }
        });
        return false;
    };

  // increment Counter (this is for testing of the UI
  // $("#scenario-table").on("click", ".js-increment-scenario", incrementCounter);

    //clear any validation error once the user starts typing
    // $("#scenario_title").on('keyup', function () {
    //     clearValidationError()
    // });
    // $("#scenario_title").on('change', function () {
    //     clearValidationError();
    // });

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


// not used
// var incrementCounter = function () {
//     var btn = $(this);
//     $.ajax({
//       url: btn.attr("data-url"),
//
//       type: 'GET',
//       dataType: 'json',
//       success: function (data) {
//         if (data.form_is_valid) {
//           $('#scenario-table').DataTable().ajax.reload();
//         }
//       }
//     });
//     return false;
// };