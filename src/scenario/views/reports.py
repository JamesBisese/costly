import io
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import xlsxwriter
from rest_framework.views import APIView
from scenario.models import Scenario

"""
    generate and return (excel) reports.  aka export excel reports
"""


class ScenarioExcelResults(APIView):
    """
    #
    # this is the Excel export function to return the scenario in Excel
    #
    # NOTE: this needs to be redone so that multiple results can be exported to a single workbook
    #
    #
    # created on 2021-11-05
    #
    """
    def get(self, request, pk):
        # create and populate the workbook and return it as an output stream
        output = scenario_workbook([pk, ])

        # Set up the Http response.
        filename = 'scenario_results.xlsx'
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response


class CompareScenarioExcelResults(APIView):

    def get(self, request, multiple_pks):
        pass

    def get(self, request):
        id_tx = request.query_params['id']
        ids = id_tx.split(',')

        # create and populate the workbook and return it as an output stream
        output = scenario_workbook(ids)

        # Set up the Http response.
        filename = 'scenario_results.xlsx'
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response


class ScenarioExtendedExcelReport(APIView):
    """
        this is the wide and very complex export of all the data into a spreadsheet

    """
    def get(self, request, multiple_pks):
        pass

    def get(self, request):
        id_tx = request.query_params['id']
        ids = id_tx.split(',')

        # create and populate the workbook and return it as an output stream
        output = scenario_extended_excel_report(ids)

        # Set up the Http response.
        filename = 'scenario_extended_results.xlsx'
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response

def scenario_workbook(scenario_ids):
    """
        this populates the workbook on the output stream provides and using the scenario_id provided

    """
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()

    # Even though the final file will be in memory the module uses temp
    # files during assembly for efficiency. To avoid this on servers that
    # don't allow temp files, for example the Google APP Engine, set the
    # 'in_memory' Workbook() constructor option as shown in the docs.

    workbook = xlsxwriter.Workbook(output)

    # build up all the formats required
    formats = create_formats(workbook)

    worksheet = workbook.add_worksheet()

    i = 0
    for id in scenario_ids:
        # add the leftmost scenario
        start_col = i
        populate_workbook(workbook, worksheet, id, formats, start_col)
        i += 5

    # Close the workbook before sending the data.
    workbook.close()

    # Rewind the buffer.
    output.seek(0)

    return output


def scenario_extended_excel_report(scenario_ids):
    """
        this populates the workbook on the output stream provides and using the scenario_id provided
        this is the wide version of the export
    """

    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()

    # Even though the final file will be in memory the module uses temp
    # files during assembly for efficiency. To avoid this on servers that
    # don't allow temp files, for example the Google APP Engine, set the
    # 'in_memory' Workbook() constructor option as shown in the docs.

    workbook = xlsxwriter.Workbook(output)

    # build up all the formats required
    formats = create_formats(workbook)

    worksheet = workbook.add_worksheet()

    i = 0
    for id in scenario_ids:
        # add the leftmost scenario
        start_row = i
        populate_scenario_extended_excel_report_workbook(workbook, worksheet, id, formats, start_row)
        i += 1

    # Close the workbook before sending the data.
    workbook.close()

    # Rewind the buffer.
    output.seek(0)

    return output


def create_formats(workbook):
    # helper for reusing partial formats
    def copy_format(book, fmt):
        properties = [f[4:] for f in dir(fmt) if f[0:4] == 'set_']
        dft_fmt = book.add_format()
        return book.add_format(
            {k: v for k, v in fmt.__dict__.items() if k in properties and dft_fmt.__dict__[k] != v})

    # NOTE: store these in a dictionary so they can be passed to a function easily
    formats = {}

    # Add a bold format to use to highlight cells.
    formats['bold'] = workbook.add_format({'bold': True})

    formats['header_bold'] = copy_format(workbook, formats['bold'])
    formats['header_bold'].set_align('center')
    formats['header_bold'].set_border(1)

    formats['label_col'] = workbook.add_format()
    formats['label_col'].set_border(1)

    formats['input_col'] = workbook.add_format({'bg_color': 'DDEBF7', 'align': 'right'})  # light blue
    formats['input_col'].set_top(1)
    formats['input_col'].set_bottom(1)
    formats['input_col'].set_left(1)

    formats['input_col_text'] = copy_format(workbook, formats['input_col'])
    formats['input_col_text'].set_align('left')

    formats['input_col_right'] = copy_format(workbook, formats['input_col'])
    formats['input_col_right'].set_left(0)
    formats['input_col_right'].set_right(1)

    formats['output_col'] = workbook.add_format({'bg_color': 'E2EFDA'})  # light green
    formats['output_col'].set_border(1)

    # Add a number format for cells with money.
    formats['money_big'] = workbook.add_format({'num_format': '$#,##0'})
    formats['money_big'].set_top(1)
    formats['money_big'].set_bottom(1)
    formats['money_big'].set_left(1)

    formats['money_small'] = workbook.add_format({'num_format': '$#,##0.00', 'bg_color': 'DDEBF7'})
    formats['money_small'].set_top(1)
    formats['money_small'].set_bottom(1)
    formats['money_small'].set_left(1)

    formats['output_col_money_big'] = workbook.add_format({'num_format': '$#,##0', 'bg_color': 'E2EFDA'})
    formats['output_col_money_big'].set_top(1)
    formats['output_col_money_big'].set_bottom(1)
    formats['output_col_money_big'].set_left(1)
    formats['output_col_money_big'].set_right(1)

    formats['int_big'] = workbook.add_format({'num_format': '#,##0', 'bg_color': 'DDEBF7'})
    formats['int_big'].set_top(1)
    formats['int_big'].set_bottom(1)
    formats['int_big'].set_left(1)

    formats['int_big_output'] = copy_format(workbook, formats['int_big'])
    formats['int_big_output'].set_bg_color('E2EFDA')
    formats['int_big_output'].set_num_format('$#,##0')

    formats['table_title'] = workbook.add_format({'bold': 'true', 'align': 'center', 'border': 1})

    # header above each sub-section
    formats['merge_format'] = workbook.add_format({'align': 'center', 'valign': 'vcenter', })
    formats['merge_format'].set_top(1)
    formats['merge_format'].set_bottom(1)
    formats['merge_format'].set_left(1)
    formats['merge_format'].set_right(1)

    return formats


def populate_workbook(workbook, worksheet, scenario_id, formats, start_col=0):
    # region --get data--
    #
    # generate the data used in the tall-thin export
    #
    scenario = get_object_or_404(Scenario, pk=scenario_id)

    cost_results = scenario.get_costs()

    project_life_cycle_costs = cost_results.pop('project_life_cycle_costs')
    structure_life_cycle_costs = cost_results.pop('structure_life_cycle_costs')
    # endregion

    # region --worksheet--

    worksheet.set_column(start_col, start_col, 27)
    worksheet.set_column(start_col + 1, start_col + 1, 20)
    worksheet.set_column(start_col + 2, start_col + 2, 25)

    # Write some data headers.
    worksheet.write(0, start_col, 'User', formats['bold'])
    worksheet.write(0, start_col + 1, scenario.project.user.name, formats['bold'])
    worksheet.write(1, start_col, 'User Type', formats['bold'])
    worksheet.write(1, start_col + 1, scenario.project.user.profile.get_user_type_display(), formats['bold'])
    worksheet.write(2, start_col, 'Project Title', formats['bold'])
    worksheet.write(2, start_col + 1, scenario.project.project_title, formats['bold'])
    worksheet.write(3, start_col, 'Scenario Title', formats['bold'])
    worksheet.write(3, start_col + 1, scenario.scenario_title, formats['bold'])

    # Some data we want to write to the worksheet.
    project_description = (
        ['Project Organizer', scenario.project.get_project_ownership_display(), formats['input_col_text']],
        ['Location of the project', scenario.project.project_location, formats['input_col_text']],
        ['Project Type', scenario.project.get_project_type_display(), formats['input_col_text']],
        ['Purchase Information', scenario.project.get_project_purchase_information_display(),
         formats['input_col_text']],
        ['Total Project Area', int(scenario.project.project_area), formats['int_big']],
        ['Land cost per ft', scenario.project.land_unit_cost.amount, formats['money_small']],
        ['Land Value', float(scenario.project.project_area) * float(scenario.project.land_unit_cost.amount),
         formats['output_col_money_big']],
    )

    # Start from the first cell below the headers.
    row = 5
    col = start_col

    # Iterate over the data and write it out row by row.
    for label, value, formatz in project_description:
        worksheet.write(row, col, label, formats['label_col'])
        if formatz == 'text':
            worksheet.write(row, col + 1, value)
        else:
            worksheet.write(row, col + 1, value, formatz)
            worksheet.write(row, col + 2, '', formats['input_col_right'])
        row += 1

    # Write a second instance of the total using a formula. Example Only.
    # worksheet.write(row, 0, 'Land Value', label_col)
    # worksheet.write(row, 1, '=B8*B9', output_col_money_big)

    row += 1

    worksheet.merge_range(row, col, row + 1, col + 2, 'Design Elements', formats['merge_format'])

    row += 1
    row += 1

    project_description = (
        ['Nutrient requirements met?', scenario.get_nutrient_req_met_display(), formats['input_col_text']],
        ['Captures 90th pct storm?', scenario.get_captures_90pct_storm_display(), formats['input_col_text']],
        ['Meets peak flow req?', scenario.get_meets_peakflow_req_display(), formats['input_col_text']],
    )

    # Iterate over the data and write it out row by row.
    for label, value, formatz in (project_description):
        worksheet.write(row, col, label, formats['label_col'])
        if formatz == 'text':
            worksheet.write(row, col + 1, value)
        else:
            worksheet.write(row, col + 1, value, formatz)
            worksheet.write(row, col + 2, '', formats['input_col_right'])
        row += 1

    row += 1

    project_description = (
        ['Pervious Area', scenario.pervious_area, formats['int_big']],
        ['Impervious Area', scenario.impervious_area, formats['int_big']],
    )

    # Iterate over the data and write it out row by row.
    for label, value, formatz in (project_description):
        worksheet.write(row, col, label, formats['label_col'])
        if formatz == 'text':
            worksheet.write(row, col + 1, value)
        else:
            worksheet.write(row, col + 1, value, formatz)
            worksheet.write(row, col + 2, '', formats['input_col_right'])
        row += 1

    worksheet.merge_range(row, col, row + 1, col + 2, 'Life Cycle Costs Assumptions', formats['merge_format'])

    row += 1
    row += 1

    project_description = (
        ['Planning and Design Factor', '{} %'.format(scenario.planning_and_design_factor), formats['input_col']],
        ['Study Life', '{} years'.format(scenario.study_life), formats['input_col']],
        ['Discount Rate', '{} %'.format(scenario.discount_rate), formats['input_col']],
    )

    # Iterate over the data and write it out row by row.
    for label, value, format in (project_description):
        worksheet.write(row, col, label, formats['label_col'])
        if format == 'text':
            worksheet.write(row, col + 1, value)
        else:
            worksheet.write(row, col + 1, value, format)
            worksheet.write(row, col + 2, '', formats['input_col_right'])
        row += 1

    # now try and make all 4 cost blocks as a loop on a more complex object

    cost_blocks = (
        ['Project Life Cycle Costs',
         ['Item', 'Dollars'],
         [
             ['Construction', int(project_life_cycle_costs['total']['construction']), formats['output_col_money_big']],
             ['Planning and Design', int(project_life_cycle_costs['total']['planning_and_design']),
              formats['output_col_money_big']],
             ['O & M', int(project_life_cycle_costs['total']['o_and_m']), formats['output_col_money_big']],
             ['Replacement', int(project_life_cycle_costs['total']['replacement']), formats['output_col_money_big']],
             ['Total', int(project_life_cycle_costs['total']['sum']), formats['output_col_money_big']],
         ]
         ],
        ['Project Construction Costs',
         ['Structure Class', 'Construction', 'P & D'],
         [
             ['Non-Conventional (GSI)',
              int(project_life_cycle_costs['nonconventional']['costs']['construction']),
              int(project_life_cycle_costs['nonconventional']['costs']['planning_and_design']),
              formats['output_col_money_big']],
             ['Conventional',
              int(project_life_cycle_costs['conventional']['costs']['construction']),
              int(project_life_cycle_costs['conventional']['costs']['planning_and_design']),
              formats['output_col_money_big']],
             ['Total',
              int(project_life_cycle_costs['total']['construction']),
              int(project_life_cycle_costs['total']['planning_and_design']), formats['output_col_money_big']],
         ]
         ],
        ['O&M and Replacement Costs',
         ['Structure Class', 'O & M', 'Replacement'],
         [
             ['Non-Conventional (GSI)',
              int(structure_life_cycle_costs['nonconventional']['costs']['o_and_m_sum']),
              int(structure_life_cycle_costs['nonconventional']['costs']['replacement_sum']),
              formats['output_col_money_big']],
             ['Conventional',
              int(structure_life_cycle_costs['conventional']['costs']['o_and_m_sum']),
              int(structure_life_cycle_costs['conventional']['costs']['replacement_sum']),
              formats['output_col_money_big']],
             ['Total',
              int(structure_life_cycle_costs['nonconventional']['costs']['o_and_m_sum'])
              + int(structure_life_cycle_costs['conventional']['costs']['o_and_m_sum']),
              int(structure_life_cycle_costs['nonconventional']['costs']['replacement_sum']
                  + int(structure_life_cycle_costs['conventional']['costs']['replacement_sum'])),
              formats['output_col_money_big']],
         ]
         ],
        ['Life Cycle Costs',
         ['Structure', 'Life Cycle Total'],
         [
             ['Non-Conventional (GSI)', int(project_life_cycle_costs['nonconventional']['costs']['sum']),
              formats['output_col_money_big']],
             ['Conventional', int(project_life_cycle_costs['conventional']['costs']['sum']),
              formats['output_col_money_big']],
             ['Total', int(project_life_cycle_costs['total']['sum']), formats['int_big_output']],
         ]],
    )

    for header, titles, values in (cost_blocks):
        worksheet.merge_range(row, col, row + 1, col + 2, header, formats['merge_format'])
        row += 2
        if len(titles) == 2:
            worksheet.write(row, col, titles[0], formats['table_title'])
            worksheet.write(row, col + 1, titles[1], formats['table_title'])
            row += 1
            for label, value, format in values:
                worksheet.write(row, col, label, formats['label_col'])
                if format == 'text':
                    worksheet.write(row, col + 1, value)
                else:
                    worksheet.write(row, col + 1, value, format)
                row += 1
        else:  # there are 2 values per-line
            worksheet.write(row, col, titles[0], formats['table_title'])
            worksheet.write(row, col + 1, titles[1], formats['table_title'])
            worksheet.write(row, col + 2, titles[2], formats['table_title'])
            row += 1
            for label, value1, value2, format in values:
                worksheet.write(row, col, label, formats['label_col'])
                if format == 'text':
                    worksheet.write(row, col + 1, value1)
                    worksheet.write(row, col + 2, value2)
                else:
                    worksheet.write(row, col + 1, value1, format)
                    worksheet.write(row, col + 2, value2, format)
                row += 1

        # endregion





def populate_scenario_extended_excel_report_workbook(workbook, worksheet, scenario_id, formats, start_row=0):
    """

    make the wide version of the export
    Note: this tries to make a sensible row-col inserts, and deals with writing the header also.
    But it is confusing and the names of the navigation variables is ... strange.

    """
    # region --get data--
    #
    # generate the data used in the export
    #
    queryset = Scenario.objects\
        .select_related('project', 'project__user', 'project__user__profile')\
        .filter(pk=scenario_id)
    scenario = get_object_or_404(queryset)

    cost_results = scenario.get_costs()

    project_life_cycle_costs = cost_results.pop('project_life_cycle_costs')
    structure_life_cycle_costs = cost_results.pop('structure_life_cycle_costs')
    # endregion

    # region --worksheet--
    start_col = 0
    col = 0
    col_title_row = 1
    insert_header = start_row == 0
    # Start from the first cell below the headers.
    row = start_row + 2

    # set the column widths
    worksheet.set_column(start_col, start_col, 13)
    worksheet.set_column(start_col + 1, start_col + 1, 28)
    worksheet.set_column(start_col + 2, start_col + 2, 12)
    worksheet.set_column(start_col + 3, start_col + 3, 29)

    worksheet.set_column(start_col + 4, start_col + 4, 18)
    worksheet.set_column(start_col + 5, start_col + 5, 38)
    worksheet.set_column(start_col + 6, start_col + 6, 30)
    worksheet.set_column(start_col + 7, start_col + 7, 18)
    worksheet.set_column(start_col + 8, start_col + 8, 11.5)
    worksheet.set_column(start_col + 9, start_col + 9, 12)
    worksheet.set_column(start_col + 10, start_col + 10, 12)

    worksheet.set_column(start_col + 11, start_col + 11, 35)
    worksheet.set_column(start_col + 12, start_col + 12, 21)

    for col_index in range(13, 13 + 15 + 7 + 12):
        worksheet.set_column(col_index, col_index, 15)

    # remove the blue or green background from some formats
    formats['input_col'].set_bg_color('white')
    formats['input_col_text'].set_bg_color('white')
    formats['int_big'].set_bg_color('white')
    formats['money_small'].set_bg_color('white')
    formats['output_col_money_big'].set_bg_color('white')

    # this was just used for debugging.  it can be removed
    skip_this_section = False

    if skip_this_section is False:
        # Write some data headers.
        if insert_header is True:
            worksheet.merge_range(0, col, 0, 2, 'User', formats['merge_format'])
            worksheet.merge_range(0, 3, 0, 10, 'Project', formats['merge_format'])

            ## Note: this is out of place because there is a mistake somewhere below causing an excel error. it works when done here.
            worksheet.merge_range(0, 11, 0, 19, 'Scenario', formats['merge_format'])

        # Some data we want to write to the worksheet.
        project_description = (
            ['user_name', scenario.project.user.name, formats['input_col_text']],
            ['organization', scenario.project.user.organization_tx, formats['input_col_text']],
            ['user_type', scenario.project.user.profile.user_type, formats['input_col_text']],
            ['project_title', scenario.project.project_title, formats['input_col_text']],
            ['project_ownership', scenario.project.get_project_ownership_display(), formats['input_col_text']],
            ['project_location', scenario.project.project_location, formats['input_col_text']],
            ['project_type', scenario.project.get_project_type_display(), formats['input_col_text']],
            ['project_purchase_information', scenario.project.get_project_purchase_information_display(),
             formats['input_col_text']],
            ['project_area', int(float(scenario.project.project_area)), formats['int_big']],
            ['land_unit_cost', scenario.project.land_unit_cost.amount, formats['money_small']],
            ['land_value', float(scenario.project.project_area) * float(scenario.project.land_unit_cost.amount),
             formats['output_col_money_big']],
        )

        col = 0

        # Iterate over the data and write it out row by row.
        for label, value, format in (project_description):
            if insert_header is True:
                worksheet.write(col_title_row, col, label, formats['header_bold'])
            worksheet.write(row, col, value, format)
            col += 1

        #TODO: fix this.  it is causing an Excel error, and I can't figure out what.
        # worksheet.merge_range(0, 11, 0, 19, 'Scenario', formats['merge_format'])

        # write in the scenario stuff
        worksheet.write(col_title_row, col , 'scenario_title', formats['header_bold'])

        worksheet.write(row, col , scenario.scenario_title, formats['input_col_text'])
        col += 1

        scenario_description = (
            ['nutrient_req_met', scenario.get_nutrient_req_met_display(), formats['input_col_text']],
            ['captures_90pct_storm', scenario.get_captures_90pct_storm_display(), formats['input_col_text']],
            ['meets_peakflow_req', scenario.get_meets_peakflow_req_display(), formats['input_col_text']],
        )

        # Iterate over the data and write it out row by row.
        for label, value, format in (scenario_description):
            if insert_header is True:
                worksheet.write(col_title_row, col, label, formats['header_bold'])
            worksheet.write(row, col, value, format)
            col += 1

        scenario_description = (
            ['pervious_area', scenario.pervious_area, formats['int_big']],
            ['impervious_area', scenario.impervious_area, formats['int_big']],
        )

        # Iterate over the data and write it out row by row.
        for label, value, formatz in (scenario_description):
            if insert_header is True:
                worksheet.write(col_title_row, col, label, formats['header_bold'])
            worksheet.write(row, col, value, formatz)
            col += 1

        scenario_description = (
            ['planning_and_design_factor', '{} %'.format(scenario.planning_and_design_factor), formats['input_col']],
            ['study_life', '{} years'.format(scenario.study_life), formats['input_col']],
            ['discount_rate', '{} %'.format(scenario.discount_rate), formats['input_col']],
        )

        # Iterate over the data and write it out row by row.
        for label, value, formatz in (scenario_description):
            if insert_header is True:
                worksheet.write(col_title_row, col, label, formats['header_bold'])
            worksheet.write(row, col, value, formatz)
            col += 1

    # now add the 3 cost-blocks, each with 5 values

    cost_blocks = (
        ['Non-Conventional (GSI) Structures Costs',
         ['Construction', 'P & D', 'O & M', 'Replacement', 'Total'],
         [
             int(structure_life_cycle_costs['nonconventional']['costs']['construction']),
             int(structure_life_cycle_costs['nonconventional']['costs']['planning_and_design']),
             int(structure_life_cycle_costs['nonconventional']['costs']['o_and_m_sum']),
             int(structure_life_cycle_costs['nonconventional']['costs']['replacement_sum']),
             int(project_life_cycle_costs['nonconventional']['costs']['sum']),
         ]
        ],
        ['Conventional Structures Costs',
         ['Construction', 'P & D', 'O & M', 'Replacement', 'Total'],
         [
             int(structure_life_cycle_costs['conventional']['costs']['construction']),
             int(structure_life_cycle_costs['conventional']['costs']['planning_and_design']),
             int(structure_life_cycle_costs['conventional']['costs']['o_and_m_sum']),
             int(structure_life_cycle_costs['conventional']['costs']['replacement_sum']),
             int(project_life_cycle_costs['conventional']['costs']['sum']),
         ]
        ],
        ['Project Life Cycle Costs',
         ['Construction', 'P & D', 'O & M', 'Replacement', 'Total'],
         [
             int(project_life_cycle_costs['total']['construction']),
             int(project_life_cycle_costs['total']['planning_and_design']),
             int(project_life_cycle_costs['total']['o_and_m']),
             int(project_life_cycle_costs['total']['replacement']),
             int(project_life_cycle_costs['total']['sum']),
         ]
        ],
    )

    format = formats['output_col_money_big']
    for header_1, header_2, values in (cost_blocks):
        if insert_header is True:
            col_count = len(header_2)
            worksheet.merge_range(0, col, 0 , col + col_count - 1, header_1, formats['merge_format'])
            hold_col = col
            for label in header_2:
                worksheet.write(1, col, label, formats['header_bold'])
                col += 1
            col = hold_col

        # Iterate over the data and write it out row by row.
        for value in (values):
            worksheet.write(row, col, value, format)
            col += 1

        # endregion

    """ areal features.  this is the last of the insertable groups """
    format = formats['input_col']

    if scenario.areal_features is None:
        return

    #property_alpha = [field_nm for field_nm in vars(scenario.areal_features) if field_nm.endswith("_area")]
    #prop_names = [field_nm.replace("_area", '') for field_nm in property_alpha]

    prop_names = [field_nm.replace("_area", '') for field_nm in vars(scenario.areal_features) if field_nm.endswith("_area")]
    if insert_header is True:
        col_count = len(prop_names)
        worksheet.merge_range(0, col, 0, col + col_count - 1, 'Areal Features (square feet)', formats['merge_format'])
        hold_col = col
        for label in prop_names:
            worksheet.write(1, col, label, formats['bold'])
            col += 1
        col = hold_col

    for label in prop_names:
        value = None
        if getattr(scenario.areal_features, label + '_checkbox') == True:
            value = getattr(scenario.areal_features, label + '_area')
        worksheet.write(row, col, value, format)
        col += 1

    return