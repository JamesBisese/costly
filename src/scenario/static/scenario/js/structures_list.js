
// the SETTINGS.URLS is loaded from from urls.js (or urls_production.js)
// which is loaded via the HTML file.

//NOTE: TODO: update my datatables and use grouping on classification_display

$(function () {

    var is_superuser = false;

    /* Binding */
    $(document).ready(function() {

        var inputDom = document.getElementById('is_superuser');

        is_superuser = (inputDom) ? true: false;

        loadTable();
    });

    var loadTable = function() {

        var options = {
            "serverSide": true,
            "responsive": true,
            "ajax": SETTINGS.URLS.structures_list,
            "paging": false,
            "info" : false,
            "dom": 'Bfrtip',
            "buttons": [
                { 'extend': 'copy'},
                { 'extend': 'csv'},
                { 'extend': 'excel'},
                { 'extend': 'pdf'},
                { 'extend': 'print'},
            ],
            "columns": [
                // Use dot notation to reference nested serializers.
                {"data": "sort_nu"},
                {"data": "classification_display"},
                {"data": "name"},
                {"data": "code"},
                 {"data": "units_html", "searchable": false, "sortable": false},
                {"data": "help_text", "searchable": true},

             ],
            "order": [[0, 'asc']],
            // "columnDefs": [
            //         { "targets": 0, "visible": false},
            //         { "targets": 1, "visible": false},
            //         { "targets": 2, "visible": false}
            //     ],
            "rowGroup": { "dataSrc": 'classification_display'}
        };

        // hide the user column if the user is not a super user - the values should all be that particular user
        // if (is_superuser == false)
        // {
        // options['columnDefs'].push({
        //         "targets": 0,
        //         "visible": false
        //     }
        // )
        // }

        var table = $('#structures-table').DataTable(options);
};



});
