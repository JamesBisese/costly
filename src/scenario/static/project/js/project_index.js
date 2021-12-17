/*jshint esversion: 6 */
/*jshint strict:false */
/*globals $:false */

// project_index.js
var URLS = null; // this gets set via another javascript file sourced before this file

$(function () {

    var is_superuser = false;
    let is_staff = false;
    URLS = SETTINGS.URLS;

    /* Binding */
    $(document).ready(function() {

        var inputDom = document.getElementById('is_superuser');

        is_superuser = (inputDom) ? true : false;
        inputDom = document.getElementById('is_staff');

        is_staff = (inputDom) ? true : false;
        loadTable();
    });

  var loadTable = function() {

      var export_columns = [0, 1, 2, 3, 4, 5, 6];

      var options = {
          "serverSide": true,
          "ajax": URLS.project_list,
          "paging": false,
          "info": false,
          "dom": 'frtipB',
          "processing": true,
            'language': {
                'loadingRecords': '&nbsp;',
                'processing': '<div class="spinner"></div>'
            },
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
              {"data": "user.name", "searchable": true},
              {"data": "user.organization_tx", "searchable": true},
              {"data": "user.job_title", "searchable": true},
              {"data": "user.profile.user_type", "searchable": true},
              {"data": "project_title", "searchable": true},
              {"data": "project_location", "searchable": true},
              {"data": "project_type", "sortable": true},
              {"data": "project_purchase_information", "searchable": true},
              {"data": "project_area",
                  "render": $.fn.dataTable.render.number( ',' ),
                  "searchable": true},
              {"data": "scenario_count", "sortable": true, "searchable": false},
              //added these fields for audit
              {"data": "create_date", "searchable": true},
              {"data": "modified_date", "searchable": true},
              {"data": "id", "searchable": false, "sortable": false},
          ],
          "columnDefs": [
              {
                    "searchable": false,
                    "orderable": false,
                    "targets": 0
              },
              {
                  "targets": 13,
                  "sWidth": "260px",
                  "render": function (data, type, row) {
                        var scenario_url = URLS.project_scenario_list.replace('<int:pk>', data);
                        let scenario_button = '<a class="btn btn-warning btn-sm " '+
                            'href="' + scenario_url + '">' +
                            '<span class="glyphicon glyphicon-pencil"></span> Scenarios' +
                            '</a>' + '&nbsp;';
                        var update_url = URLS.project_update.replace('<int:pk>', data);
                        let update_button = is_staff === false ? '<button type="button"' +
                            ' class="btn btn-warning btn-sm js-update-project" '+
                            'data-url="' + update_url + '">' +
                            '<span class="glyphicon glyphicon-pencil"></span> Edit' +
                            '</button>' + '&nbsp;' : '';
                        var delete_url = URLS.project_delete.replace('<int:pk>', data);
                        let delete_button = is_staff === false ? '<button type="button" ' +
                            'class="btn btn-danger btn-sm js-delete-project" '+
                            'data-url="' + delete_url + '">'+
                           '<span class="glyphicon glyphicon-trash"></span> Delete'+
                           '</button>' : '';

                        return scenario_button + update_button + delete_button;

                  }
              },
          ],
          "order": [[ 1, 'asc' ]]
      };
      // hide the user column if the user is not a super user - the values should all be that particular user
      if (is_superuser === false && is_staff === false) {
          options.columnDefs.push({
                  "targets": 1,
                  "visible": false
              }
          );
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
