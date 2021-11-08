            var table;
            $(document).ready(function() {
              var export_columns = [0, 1, 2, 3, 4, 5, 6, 7];

              table = $('#scenario-audit-table').DataTable({
                      'serverSide': true,
                      'ajax': SETTINGS.URLS.scenario_audit + '?format=datatables',
                    'pageLength': 200,
                    "dom": 'Bfrtip',
                    "buttons": [
                        { 'extend': 'copy'},
                        { 'extend': 'csv'},
                        { 'extend': 'excel'},
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



        table.on( 'order.dt search.dt', function () {
            table.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
            cell.innerHTML = i+1;
            t.cell(cell).invalidate('dom');
        } );
    } ).draw();
