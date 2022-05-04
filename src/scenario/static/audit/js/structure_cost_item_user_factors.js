/*jshint esversion: 6 */
/*jshint strict:false */
/*globals $:false */

var table;
var URLS = null; // this gets set via another javascript file sourced before this file


$(function () {

    var is_superuser = false;

    /* Binding */
    $(document).ready(function() {

        URLS = SETTINGS.URLS;

        var inputDom = document.getElementById('is_superuser');

        is_superuser = (inputDom) ? true: false;

        loadTable();
    });

    var loadTable = function() {

        var export_columns = [ 0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13];

        var options = {
            "serverSide": true,
            "responsive": true,
            "ajax": URLS.audit_cost_item_user_factors_data + '?format=datatables',
            "lengthMenu": [ [50, 100, 250, -1], [50, 100, 250, "All"] ],
            "paging": true,
            "info" : false,
            "dom": 'Blpifrt',
            "buttons": [
                { 'extend': 'copy',  'exportOptions': {'columns': export_columns}},
                { 'extend': 'csv',   'exportOptions': {'columns': export_columns}},
                { 'extend': 'excel', 'exportOptions': {'columns': export_columns}},
                { 'extend': 'pdf',   'exportOptions': {'columns': [ 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]}, 'title': 'Cost Item Default Equations'},
                { 'extend': 'print', 'exportOptions': {'columns': [ 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]}, 'title': 'Cost Item Default Equations'},
            ],
            "columns": [
                // Use dot notation to reference nested serializers.
                {"data": "user.name", 'name': 'scenario.project.user.name', "searchable": true},
                {"data": "user.organization_tx", 'name': 'scenario.project.user.organization_tx', "searchable": false},
                {"data": "user.profile.user_type", 'name': 'scenario.project.user.profile.user_type', "searchable": false},
                {"data": "project_title", 'name': 'scenario.project.project_title', "searchable": false},
                {"data": "scenario_title", 'name': 'scenario.scenario_title', "searchable": true},

                {"data": "structure.name", "searchable": true},
                {"data": "structure.units", "searchable": true},

                {"data": "costitem.name", "searchable": true},
                {"data": "costitem.units", "searchable": true},

                {"data": "checked", "searchable": true},
                {"data": "a_area", "searchable": true},
                {"data": "z_depth", "searchable": true},
                {"data": "d_density", "searchable": true},
                {"data": "n_number", "searchable": true},


             ],
            // "order": [[0, 'asc'],[1, 'asc']],
            "columnDefs": [
                    // { "targets": 0, "visible": false},
                    // { "targets": 1, "visible": false},
                    // { "targets": 2, "visible": false},

                ],
        };


        var table = $('#costitem-table').DataTable(options);
    };



});
