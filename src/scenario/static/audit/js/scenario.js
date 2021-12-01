var table;

$(document).ready(function() {

  table = $('#scenario-audit-table').DataTable({
            'serverSide': true,
            'ajax': SETTINGS.URLS.audit_scenario_data + '?format=datatables',
            'pageLength': 200,
            "dom": 'Bfrtip',
            "processing": true,
            'language': {
                'loadingRecords': '&nbsp;',
                'processing': '<div class="spinner"></div>'
            },
            "buttons": [
                { 'extend': 'copy'},
                { 'extend': 'csv'},
                { 'extend': 'excel'},
                {
                    text: 'Detailed Excel',
                    action: function ( e, dt, node, config ) {

                        //TODO: figure out how to get the loader to display while the export is happening
                        $(".spinner").show();
                        // set the url for exporting all the scenarios in the table
                        $("#scenario-audit-table_processing").css("display","inline");

                        var scenario_ids = table.column(0).data();
                        var url = SETTINGS.URLS.scenario_export_extended_excel_report + scenario_ids.join(',');
                        var e = document.createElement('a');
                        e.href = url;
                        document.body.appendChild(e);
                        e.click();
                        document.body.removeChild(e);
                        $("#scenario-audit-table_processing").css("display","none");
                        $(".spinner").hide();
                    }
                }
            ],
            'columns': [
              // Use dot notation to reference nested serializers.
                {"data": "id", "searchable": false},
                {"data": "project.user.name", "searchable": true},
                {"data": "project.user.organization_tx", "searchable": true},
                {"data": "project.user.profile.user_type", "searchable": true},
                {"data": "project.project_title", "searchable": true},
                {"data": "scenario_title", "searchable": true},
                {"data": "create_date", "searchable": true},
                {"data": "modified_date", "searchable": true},
            ],
            "columnDefs": [
              {
                    "searchable": false,
                    "orderable": false,
                    "targets": 0
              },
            ],
            "order": [[ 1, 'asc' ]]

          });
    });

    $('#scenario-audit-table tbody').on( 'click', 'tr', function () {
        //jab changed this to allow selecting more than 2 so the export will work
        //
        $(this).toggleClass('selected');
    });

    table.on( 'order.dt search.dt', function () {
        table.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
        cell.innerHTML = i+1;
        t.cell(cell).invalidate('dom');
    } );
} ).draw();
