
// project_index.js

$(function () {

    var is_superuser = false;

    /* Binding */
    $(document).ready(function() {

        var inputDom = document.getElementById('is_superuser');

        is_superuser = (inputDom) ? true : false;

        loadTable();
    });

  var loadTable = function() {

      var export_columns = [0, 1, 2, 3, 4, 5, 6];

      var options = {
          "serverSide": true,
          "ajax": SETTINGS.URLS.project_list,
          "paging": false,
          "info": false,
          "dom": 'frtipB',
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
              {"data": "user.email", "searchable": true},
              {"data": "user.profile.user_type", "searchable": true},
              {"data": "project_title", "searchable": true},
              {"data": "project_location", "searchable": true},
              {"data": "project_type", "sortable": true},
              {"data": "project_purchase_information", "searchable": true},
              {"data": "project_area",
                  "render": $.fn.dataTable.render.number( ',' ),
                  "searchable": true},
              {"data": "scenario_count", "sortable": true, "searchable": false},
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
      // hide the user column if the user is not a super user - the values should all be that particular user
      if (is_superuser == false) {
          options['columnDefs'].push({
                  "targets": 1,
                  "visible": false
              }
          )
      }

      var table = $('#project-table').DataTable(options);

        table.on( 'order.dt search.dt', function () {
            table.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
            cell.innerHTML = i+1;
        } );
    } ).draw();
  };


  /* Functions */

  var loadForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-project .modal-content").html("");
        $("#modal-project").modal("show");
      },
      success: function (data) {
        $("#modal-project .modal-content").html(data.html_form);

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

          $("#modal-project").modal("hide");
          $('#project-table').DataTable().ajax.reload();
        }
        else {
          $("#modal-project .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };




  // Create project - this works
  $(".js-create-project").click(loadForm);
  $("#modal-project").on("submit", ".js-project-create-form", saveForm);

    // Update project - still not working
  $("#project-table").on("click", ".js-update-project", loadForm);
  $("#modal-project").on("submit", ".js-project-update-form", saveForm);

  // Delete project - this is working now
  $("#project-table").on("click", ".js-delete-project", loadForm);
  $("#modal-project").on("submit", ".js-project-delete-form", saveForm);

});
