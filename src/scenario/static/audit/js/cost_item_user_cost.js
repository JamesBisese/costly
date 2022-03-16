

var table;
$(document).ready(function() {
  table = $('#user_cost-audit-table').DataTable({
                'serverSide': false,
                'ajax': SETTINGS.URLS.audit_cost_item_user_costs_data + '?format=datatables',
                'pageLength': 200,
                "dom": 'Bfrtip',
                "buttons": [
                    { 'extend': 'copy'},
                    { 'extend': 'csv'},
                    { 'extend': 'excel'},
                ],
                'columns': [
                    // Use dot notation to reference nested serializers.
                    {"data": "user.name", "searchable": true},
                    {"data": "user.organization_tx", "searchable": true},
                    {"data": "user.user_type", "searchable": true},
                    {"data": "project.project_title", "searchable": true},
                    {"data": "scenario2.scenario_title", "searchable": true},
                    {"data": "costitem_name", "searchable": true},
                    {"data": "units", "searchable": false},
                    {"data": "cost_source", "searchable": false},
                    {"data": "user_input_cost", "searchable": false},
                    {"data": "base_year", "searchable": false},
                    // {"data": "replacement_life", "searchable": false},
                    {"data": "o_and_m_pct", "searchable": false},
                ],

                "order": [[ 0, 'asc' ]]
            });
});

table.on( 'order.dt search.dt', function () {
    table.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
        cell.innerHTML = i+1;
        t.cell(cell).invalidate('dom');
    } );
} ).draw();
