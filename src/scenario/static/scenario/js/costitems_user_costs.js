
// the URLs used in this script are loaded from from another JS file
// in the HTML file.


/* Binding */
$(document).ready(function()
{
    loadTable();
});

var loadTable = function() {
    var options = {
        'serverSide': true,
        'ajax': '/api/costitem_user_costs/?format=datatables',
        'pageLength': 200,
        "dom": 'Bfrtip',
        "buttons": [
            {'extend': 'copy'},
            {'extend': 'csv'},
            {'extend': 'excel'},
        ],
        'columns': [
            // Use dot notation to reference nested serializers.
            {"data": "id", "searchable": false},
            // {"data": "user", "searchable": true},
            {"data": "scenario.project_title", "searchable": false, "name": "scenario.project_title"},
            {"data": "scenario.scenario_title", "searchable": true},

            {"data": "costitem_name", "searchable": true},
            // {"data": "scenario.project.user.email", "searchable": true},
            // {"data": "project.user.email", "searchable": true},

            {"data": "units", "searchable": true},
            {"data": "base_year", "searchable": true},
            {"data": "user_input_cost", "searchable": true},
            {"data": "replacement_life", "searchable": true},
            {"data": "o_and_m_pct", "searchable": true},
            // {"data": "create_date", "searchable": true},
            // {"data": "modified_date", "searchable": true},
        ],
        "columnDefs": [
            {
                "searchable": false,
                "orderable": false,
                "targets": 0
            },
        ],
        "order": [[1, 'asc']]
    };
    var table = $('#costitem_user_cost-audit-table').DataTable(options);

    table.on('order.dt search.dt', function () {
        table.column(0, {search: 'applied', order: 'applied'}).nodes().each(function (cell, i) {
            cell.innerHTML = i + 1;
        });
    }).draw();
};

//
//
// $(function () {
//
//     var is_superuser = false;
//
//     /* Binding */
//     $(document).ready(function() {
//
//         var inputDom = document.getElementById('is_superuser');
//
//         is_superuser = (inputDom) ? true: false;
//
//         loadTable();
//     });
//
//     var loadTable = function() {
//
//         var export_columns = [0, 1, 2, 3, 4, 5, 6, 7, 8];
//
//         var options = {
//             "serverSide": true,
//             "responsive": true,
//             "ajax": SETTINGS.URLS.costitems_default_costs_list,
//             "paging": false,
//             "info" : false,
//             "dom": 'Bfrtip',
//             "buttons": [
//                 { 'extend': 'copy',  'exportOptions': {'columns': export_columns}},
//                 { 'extend': 'csv',   'exportOptions': {'columns': export_columns}},
//                 { 'extend': 'excel', 'exportOptions': {'columns': export_columns}},
//                 { 'extend': 'pdf',   'exportOptions': {'columns': export_columns}},
//                 { 'extend': 'print', 'exportOptions': {'columns': export_columns}},
//             ],
//             "columns": [
//                 // Use dot notation to reference nested serializers.
//                 {"data": "costitem.sort_nu", "searchable": true},
//                 {"data": "costitem.name", "searchable": true},
//                 {"data": "costitem.units", "searchable": true},
//
//                 {"data": "rsmeans_va", "searchable": true},
//
//                 //TODO: use this once we have enough data for the db values
//                 // {"data": "db_25pct_va", "searchable": false},
//                 // {"data": "db_50pct_va", "searchable": false},
//                 // {"data": "db_75pct_va", "searchable": false},
//
//                 {"data": "replacement_life", "searchable": true},
//                 {"data": "o_and_m_pct", "searchable": false},
//              ],
//             "columnDefs": [],
//         };
//
//
//         var table = $('#costitem-table').DataTable(options);
//     };
//
//
//
// });
