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

        var export_columns = [ 0, 1, 3, 4, 5, 6, 7, 8, 9];

        var options = {
            "serverSide": true,
            "responsive": true,
            "ajax": URLS.audit_structure_cost_item_default_factors_data + '?format=datatables',
            'pageLength': 50,
            "paging": true,
            "info" : false,
            "dom": 'Bfrtip',
            "buttons": [
                { 'extend': 'copy',  'exportOptions': {'columns': export_columns}},
                { 'extend': 'csv',   'exportOptions': {'columns': export_columns}},
                { 'extend': 'excel', 'exportOptions': {'columns': export_columns}},
                { 'extend': 'pdf',   'exportOptions': {'columns': [ 3, 4, 5, 6, 7, 8, 9]}, 'title': 'Cost Item Default Equations'},
                { 'extend': 'print', 'exportOptions': {'columns': [ 3, 4, 5, 6, 7, 8, 9]}, 'title': 'Cost Item Default Equations'},
            ],
            "columns": [
                // Use dot notation to reference nested serializers.
                {"data": "structure.sort_nu"},
                {"data": "costitem.sort_nu"},

                {"data": "id"},

                {"data": "structure.name", "searchable": true},
                {"data": "structure.units", "searchable": true},


                {"data": "costitem.name", "searchable": true},
                {"data": "costitem.units", "searchable": true},

                {"data": "a_area", "searchable": true},
                {"data": "z_depth", "searchable": true},
                {"data": "d_density", "searchable": true},


             ],
            "order": [[0, 'asc'],[1, 'asc']],
            "columnDefs": [
                    { "targets": 0, "visible": false},
                    { "targets": 1, "visible": false},
                    { "targets": 2, "visible": false},

                ],
        };


        var table = $('#costitem-table').DataTable(options);
    };



});
