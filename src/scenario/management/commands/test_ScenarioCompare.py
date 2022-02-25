from django.core.management.base import BaseCommand
import itertools

from scenario.models import Project, Scenario

from scenario.views.index import comparison_column
#
# snippet used to update Project.modified_date to null since I added the field late an
# accidentally set the value to the same as the default create_date
#
#
# (venv) C:\inetpub\wwwdjango\gsicosttool\src>c
#
class Command(BaseCommand):
    """
    ad hoc test to make sure that the Scenario Comparison function doesn't fail when
    testing any pair of scenarios.  I have seen it fail when one of the scenarios is
    missing attributes that 'should' be there
    if it was a populated scenario.

    """
    help = 'snippet used to make sure that the Scenario Comparison functions for all possible combinations.'

    def handle(self, *args, **options):

        projects = Project.objects.all()
        for project in projects:
            print("Project {} last modified: {}".format(project.project_title, project.modified_date))
            scenarios = Scenario.objects \
                .select_related('project')\
                .filter(project=project).order_by('id')

            scenario_list = set()
            for scenario in scenarios:
                scenario_list.add(scenario.id)
                print("{:>6}. {} {}".format(scenario.id, scenario.project.project_title, scenario.scenario_title))

            combos = itertools.combinations(scenario_list, 2)
            for c in combos:
                right_scenario = None
                left_scenario = None

                right_scenario_objs = [x for x in scenarios if x.id == c[0]]
                if right_scenario_objs is not None and len(right_scenario_objs) > 0:
                    right_scenario = right_scenario_objs[0]

                left_scenario_objs = [x for x in scenarios if x.id == c[1]]
                if left_scenario_objs is not None and len(left_scenario_objs) > 0:
                    left_scenario = left_scenario_objs[0]

                success = False
                try:
                    comparison_column_html = comparison_column(left_scenario, right_scenario)
                    success = True
                except:
                    pass


                print ("comparision {} for ({}) {} and ({}) {}".format(
                    'worked' if success is True else 'failed',
                    left_scenario.id, left_scenario.scenario_title,
                    right_scenario.id, right_scenario.scenario_title))
            # break

