
// Cost Item Default Costs
// /cost_item/default_costs/

$(function () {

    var is_superuser = false;

    /* Binding */
    $(document).ready(function() {

        var inputDom = document.getElementById('is_superuser');

        is_superuser = (inputDom) ? true: false;

        loadTable();
    });

    var loadTable = function() {

        var export_columns = [0, 1, 2, 3, 4, 5, 6, 7, 8];

        var options = {
            "serverSide": true,
            "responsive": true,
            "ajax": SETTINGS.URLS.audit_cost_item_default_cost_data + '?format=datatables',
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
                // Use dot notation to reference nested serializers.
                {"data": "costitem.sort_nu", "searchable": true},
                {"data": "costitem.name", "searchable": true},
                {"data": "costitem.units", "searchable": true},

                {"data": "rsmeans_va", "searchable": true},

                //TODO: use this once we have enough data for the db values
                // {"data": "db_25pct_va", "searchable": false},
                // {"data": "db_50pct_va", "searchable": false},
                // {"data": "db_75pct_va", "searchable": false},

                {"data": "replacement_life", "searchable": true},
                {"data": "o_and_m_pct", "searchable": false},
             ],
            "columnDefs": [],
        };


        var table = $('#costitem-table').DataTable(options);
    };
});

