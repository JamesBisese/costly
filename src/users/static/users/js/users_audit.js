
// users_audit.js is loaded in to C:\inetpub\wwwdjango\gsicosttool\src\costly\templates\audit\users.html

$(function () {

    var is_superuser = false;

    /* Binding */
    $(document).ready(function() {

        var inputDom = document.getElementById('is_superuser');

        is_superuser = (inputDom) ? true : false;

        loadTable();
    });


// $(document).ready(function() {
//
//               var export_columns = [0, 1, 2, 3, 4, 5, 6, 7, 8];
//
//               $('#users-table').DataTable({
//                       'serverSide': true,
//                       'ajax': SETTINGS.URLS.user_list,
//                     "dom": 'Bfrtip',
//                     "buttons": [
//                         { 'extend': 'copy',  'exportOptions': {'columns': export_columns}},
//                         { 'extend': 'csv',   'exportOptions': {'columns': export_columns}},
//                         { 'extend': 'excel', 'exportOptions': {'columns': export_columns}},
//                         { 'extend': 'pdf',   'exportOptions': {'columns': export_columns}},
//                         { 'extend': 'print', 'exportOptions': {'columns': export_columns}},
//                     ],
//                   'columns': [
//                       {'data': 'is_active', "sortable": true},
//                       {'data': 'name', "sortable": true},
//                       {'data': 'email', "sortable": true},
//                       {'data': 'phone_tx', "sortable": true},
//                       {'data': 'organization_tx', "sortable": true},
//                       {'data': 'job_title', "sortable": true},
//                       {'data': 'profile.user_type', "sortable": true},
//                       {'data': 'date_joined', "sortable": true},
//                       {'data': 'last_login', "sortable": true},
//                       {#{'data': 'name'},#}
//                       {#{'data': 'year'},#}
//                       {#{'data': 'genres', 'name': 'genres.name'},#}
//                   ]
//
//               });
//           });



    var loadTable = function() {

    var export_columns = [0, 1, 2, 3, 4, 5, 6, 7, 8];

    var options = {
      "serverSide": true,
      "ajax": SETTINGS.URLS.user_list,
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
           {'data': 'name', },
           {'data': 'organization_tx', "sortable": true},
           {'data': 'job_title', "sortable": true},
           {'data': 'profile.user_type', "sortable": true},
           {'data': 'email', },
           {'data': 'phone_tx', },


           {'data': 'date_joined', "sortable": true},
           {'data': 'last_login', "sortable": true},
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
    // if (is_superuser == false) {
    //   options['columnDefs'].push({
    //           "targets": 1,
    //           "visible": false
    //       }
    //   )
    // }

    var table = $('#users-table').DataTable(options);

    table.on( 'order.dt search.dt', function () {
        table.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
            cell.innerHTML = i+1;
        } );
    } ).draw();
};







});
