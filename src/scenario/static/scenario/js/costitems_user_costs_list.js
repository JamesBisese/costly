
// the URLs used in this script are loaded from from another JS file
// in the HTML file.


$(function () {

    var is_superuser = false;

    /* Binding */
    $(document).ready(function() {

        var inputDom = document.getElementById('is_superuser');

        is_superuser = (inputDom) ? true: false;

        loadTable();
    });

    var loadTable = function() {

        var export_columns = [0, 1 , 3, 4, 5, 6, 7, 8];

        var options = {
            "serverSide": true,
            "responsive": true,
            "ajax": SETTINGS.URLS.costitems_user_costs_list,
            "paging": false,
            "info" : false,
            "dom": 'Bfrtip',
            "buttons": [
                { 'extend': 'copy',  'exportOptions': {'columns': export_columns}},
                { 'extend': 'csv',   'exportOptions': {'columns': export_columns}},
                { 'extend': 'excel', 'exportOptions': {'columns': export_columns}},
                { 'extend': 'pdf',   'exportOptions': {'columns': export_columns}},
                { 'extend': 'print', 'exportOptions': {'columns': export_columns}},
            ],
            "columns": [
                {"data": "project.project_title", "searchable": true},
                {"data": "scenario.scenario_title", "searchable": true},
                // {"data": "costitem_name", "searchable": true},
                // {"data": "units", "searchable": true},
                // {"data": "base_year", "searchable": true},
                // {"data": "user_input_cost", "searchable": true},
                // {"data": "replacement_life", "searchable": true},
                // {"data": "o_and_m_pct", "searchable": true},

                // {"data": "units", "searchable": true},
             ],
            "columnDefs": [],
        };


        var table = $('#costitem-table').DataTable(options);
    };

    /* Functions */

    var loadForm = function () {
        var btn = $(this);
        $.ajax({
            url: btn.attr("data-url"),
            type: 'get',
            dataType: 'json',
            beforeSend: function () {
                $("#modal-scenario .modal-content").html("");
                $("#modal-scenario").modal("show");
            },
            success: function (data) {
                $("#modal-scenario .modal-content").html(data.html_form);
            }
        });
    };

    var saveForm = function () {
        var form = $(this);
        $.ajax({
            url: form.attr("action"),
            data: form.serialize(),
            type: form.attr("method"),
            dataType: 'json',
            success: function (data) {
                if (data.form_is_valid) {
                    $("#modal-scenario").modal("hide");
                    $('#scenario-table').DataTable().ajax.reload();
                }
                else {
                  $("#modal-scenario .modal-content").html(data.html_form);
                }
            }
        });
        return false;
    };

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



  // Create project
  // $(".js-create-scenario").click(loadForm);
  // $("#modal-scenario").on("submit", ".js-project-create-form", saveForm);
    // $("#subbing").on("click", ".js-project-create-form", saveForm);
    //
  // increment Counter (this is for testing of the UI
  // $("#scenario-table").on("click", ".js-increment-scenario", incrementCounter);

    // Update project
  // $("#scenario-table").on("click", ".js-update-project", loadForm);
  // $("#modal-scenario").on("submit", ".js-project-update-form", saveForm);

  // Delete project
  // $("#costitem-table").on("click", ".js-delete-project", loadForm);
  // $("#modal-scenario").on("submit", ".js-project-delete-form", saveForm);
