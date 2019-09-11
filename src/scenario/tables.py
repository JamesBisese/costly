from django.contrib.auth import get_user_model
import django_tables2 as tables

from . import models # import Project, Scenario, Structures, CostItemDefaultCosts, CostItemDefaultAssumptions

User = get_user_model()

class StructuresTable(tables.Table):
    export_formats = ['csv', 'xls']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = models.Structures
        template_name = 'django_tables2/bootstrap.html'
        order_by = 'id'
        attrs = {"class": "paleblue"}

class CostItemsTable(tables.Table):
    export_formats = ['csv', 'xls']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = models.CostItem
        template_name = 'django_tables2/bootstrap.html'
        order_by = 'id'
        attrs = {"class": "paleblue"}

class CostItemDefaultCostsTable(tables.Table):
    export_formats = ['csv', 'xls']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = models.CostItemDefaultCosts
        # exclude = ('id',)
        # sequence = ('edit_column', 'scenario_date',
        #             'user',
        #
        #             'location',
        #             'name', 'delete_column','create_date', 'modified_date', )
        template_name = 'django_tables2/bootstrap.html'
        order_by = 'id'
        attrs = {"class": "paleblue"}

class CostItemDefaultEquationsTable(tables.Table):
    export_formats = ['csv', 'xls']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = models.CostItemDefaultEquations
        template_name = 'django_tables2/bootstrap.html'
        order_by = 'id'
        attrs = {"class": "paleblue"}

class CostItemDefaultFactorsTable(tables.Table):
    export_formats = ['csv', 'xls']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = models.CostItemDefaultFactors
        template_name = 'django_tables2/bootstrap.html'
        order_by = 'id'
        attrs = {"class": "paleblue"}

class ProjectTable(tables.Table):
    export_formats = ['csv', 'xls']
    scenario_date = tables.Column(verbose_name="Date")
    edit_column = tables.TemplateColumn('<a href="{% url "project:project_update" record.id %}"  class="btn btn-sm">2Edit</a>',
                                        verbose_name='', orderable=False, exclude_from_export=True)
    delete_column = tables.TemplateColumn('<a href="{% url "project:project_delete" record.id %}" class="btn btn-sm">Delete</a>',
                                          verbose_name='Delete', orderable=False, exclude_from_export=True)
    create_date = tables.DateTimeColumn(format='M d Y, h:i A')
    modified_date = tables.TemplateColumn('{% if record.create_date|date:"h:i" != record.modified_date|date:"h:i" %}{{record.modified_date|date:"M d Y, h:i A"}}{%else%}{%endif%}')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def before_render(self, request):
        if request.user.has_perm('project.delete_location'):
            self.columns.show('delete_column')
        else:
            self.columns.hide('delete_column')

        if 'delete' in request.path:
            self.columns.hide('edit_column')
            self.columns.hide('delete_column')
        elif request.user.has_perm('project.change_location'):
            self.columns.show('edit_column')
            self.columns.show('create_date')
            self.columns.show('modified_date')
        else:
            self.columns.hide('edit_column')
            self.columns.hide('create_date')
            self.columns.hide('modified_date')

        if not (request.user.is_superuser or request.user.is_staff):
            self.columns.hide('user')

    class Meta:
        model = models.Project
        exclude = ('id',)
        sequence = ('edit_column', 'scenario_date',
                    'user',

                    'project',
                    'name', 'delete_column','create_date', 'modified_date', )
        template_name = 'django_tables2/bootstrap.html'
        order_by = 'user'
        attrs = {"class": "paleblue"}


class ScenarioTable(tables.Table):
    export_formats = ['csv', 'xls']
    scenario_date = tables.Column(verbose_name="Date")
    edit_column = tables.TemplateColumn('<a href="{% url "scenario:scenario_update" record.id %}"  class="btn btn-sm">2Edit</a>',
                                        verbose_name='', orderable=False, exclude_from_export=True)
    delete_column = tables.TemplateColumn('<a href="{% url "scenario:scenario_delete" record.id %}" class="btn btn-sm">Delete</a>',
                                          verbose_name='Delete', orderable=False, exclude_from_export=True)
    create_date = tables.DateTimeColumn(format='M d Y, h:i A')
    modified_date = tables.TemplateColumn('{% if record.create_date|date:"h:i" != record.modified_date|date:"h:i" %}{{record.modified_date|date:"M d Y, h:i A"}}{%else%}{%endif%}')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def before_render(self, request):
        if request.user.has_perm('scenario.delete_location'):
            self.columns.show('delete_column')
        else:
            self.columns.hide('delete_column')

        if 'delete' in request.path:
            self.columns.hide('edit_column')
            self.columns.hide('delete_column')
        elif request.user.has_perm('scenario.change_location'):
            self.columns.show('edit_column')
            self.columns.show('create_date')
            self.columns.show('modified_date')
        else:
            self.columns.hide('edit_column')
            self.columns.hide('create_date')
            self.columns.hide('modified_date')

        if not (request.user.is_superuser or request.user.is_staff):
            self.columns.hide('user')

    class Meta:
        model = models.Scenario
        exclude = ('id',)
        sequence = ('edit_column',
                    'scenario_date',
                    'project.user',
                    'location',
                    'name',
                    'delete_column','create_date', 'modified_date', )
        template_name = 'django_tables2/bootstrap.html'
        order_by = 'user'
        attrs = {"class": "paleblue"}