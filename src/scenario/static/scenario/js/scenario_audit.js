
// project_index.js

$(function () {

    /* Binding */
    $(document).ready(function() {
        loadTable();
    });

  var loadTable = function() {

      var export_columns = [0, 1, 2, 3, 4, 5, 6];

      var options = {
          "serverSide": true,
          "ajax": SETTINGS.URLS.scenario_list,
          "paging": false,
          "info": false,
          "dom": 'Bfrtip',
          "buttons": [
              'copy',
              {
                  'extend': 'csv',
                  'exportOptions': {'columns': export_columns}
              },
              'excel',
              'pdf',
              'print'
          ],
          "columns": [
              {"data": "id", "searchable": false},
              // Use dot notation to reference nested serializers.
              {"data": "project.user.email", "searchable": true},
              {"data": "project.user.profile.user_type", "searchable": true},
              {"data": "project_title", "searchable": true},
              // {"data": "project_location", "searchable": true},
              // {"data": "project_type", "sortable": true},
              // {"data": "project_purchase_information", "searchable": true},
              // {"data": "project_area",
              //     "render": $.fn.dataTable.render.number( ',' ),
              //     "searchable": true},
              // {"data": "scenario_count", "sortable": true, "searchable": false},
          ],
          "columnDefs": [
              {
                    "searchable": false,
                    "orderable": false,
                    "targets": 0
              },

          ],
          "order": [[ 1, 'asc' ]]
      };


      var table = $('#scenario-audit-table').DataTable(options);

        table.on( 'order.dt search.dt', function () {
            table.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
            cell.innerHTML = i+1;
        } );
    } ).draw();
  };




});
