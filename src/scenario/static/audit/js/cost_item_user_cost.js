/*jshint esversion: 6 */
/*jshint strict:false */
/*globals $:false */

var table;
var URLS = null; // this gets set via another javascript file sourced before this file

$(document).ready(function() {

    URLS = SETTINGS.URLS;

    table = $('#user_cost-audit-table').DataTable({
                'serverSide': true,
                'ajax': URLS.audit_cost_item_user_costs_data + '?format=datatables',
                'pageLength': 58,
                "lengthMenu": [ [29, 58, 150, -1], [29, 58, 150, "All"] ],
                "paging": true,
                "dom": 'Blpifrt',
                "buttons": [
                    { 'extend': 'copy'},
                    { 'extend': 'csv'},
                    { 'extend': 'excel'},
                ],
                'columns': [
                    {"data": "user_name", 'name': 'scenario.project.user.name', "searchable": true},
                    {"data": "organization_tx", 'name': 'scenario.project.user.organization_tx', "searchable": false},
                    {"data": "user_type", 'name': 'scenario.project.user.profile.user_type', "searchable": false},
                    {"data": "project_title", 'name': 'scenario.project.project_title', "searchable": false},
                    {"data": "scenario2.scenario_title", 'name': 'scenario.scenario_title', "searchable": true},
                    {"data": "costitem_sort_nu", 'name': 'costitem.sort_nu', "searchable": true},
                    {"data": "costitem_name", 'name': 'costitem.name', "searchable": true},
                    {"data": "units", 'name': 'costitem.units', "searchable": false},
                    {"data": "default_cost.cost_type", 'name': 'default_cost.cost_type', "searchable": true},
                    {"data": "default_cost.valid_start_date_tx", 'name': 'default_cost.valid_start_date_tx', "searchable": false},
                    {"data": "default_cost.value_numeric", 'name': 'default_cost.value_numeric', "searchable": false,
                        'render': $.fn.dataTable.render.number( ',', '.', 2, '$' ) },
                    {"data": "replacement_life", "searchable": false},
                    {"data": "o_and_m_pct", "searchable": false},
                ],
                "columnDefs": [
                    { "targets": [5], "visible": false },
                    { "targets": [10], className: 'dt-body-right' },
                ],
                "order": [[ 0, 'asc' ], [ 4, 'asc'], [5, 'asc']]
            });
});

table.on( 'order.dt search.dt', function () {
    table.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
        cell.innerHTML = i+1;
        t.cell(cell).invalidate('dom');
    } );
} ).draw();
