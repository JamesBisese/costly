import datetime

from django import forms
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML, Div
from crispy_forms.bootstrap import FormActions
from bootstrap_datepicker_plus import DatePickerInput

from .models import Project, Scenario

User = get_user_model()


class ProjectForm(forms.ModelForm):
    """ this is the Project Create / Update pop-up form """
    class Meta:
        model = Project
        fields = ('user',
                  'project_title',
                  'project_ownership',
                  'project_location',
                  'project_type',
                  'project_purchase_information',
                  # 'priority_watershed',
                  'project_area',
                  'land_unit_cost',
                  )

    # TODO
    # def clean_project_area(self):
    #     value = self.cleaned_data.get("project_area")
    #     try:
    #         value = value.replace(",", "")
    #         response = validator.project_area

    def __init__(self, *args, **kwargs):
        _user_id = kwargs.pop('user_id', None)

        super(ProjectForm, self).__init__(*args, **kwargs)

        self.fields['project_location'].widget.attrs['placeholder'] = 'Lat/Long or Address as applicable'
        self.fields['project_area'].widget.attrs['class'] = 'col-sm-6'
        self.fields['project_area'].widget.attrs['placeholder'] = 'Area in square feet'
        #self.fields['land_unit_cost'].widget.attrs['class'] = 'col-sm-3 row land_unit_cost_money_field'
        self.fields['land_unit_cost'].widget.attrs['class'] = 'land_unit_cost_money_field'
        # self.fields['id_land_unit_cost_1'].widget.attrs['class'] = 'col-sm-6'
        if _user_id:
            self.fields['user'].queryset = User.objects.filter(id=_user_id)
            self.fields['user'].empty_label = None
        else:
            self.fields['user'].empty_label = '--- Select User (required) ---'

# # not used
#
# class ProjectDeleteForm(forms.ModelForm):
#     class Meta:
#         model = Project
#         fields = '__all__'
#
#     success_url = reverse_lazy('scenario.location_list')
#
#     def __init__(self, *args, **kwargs):
#         super(ProjectDeleteForm, self).__init__(*args, **kwargs)
#         self.helper = FormHelper()
#         self.helper.form_id = 'id-locationForm'
#         self.helper.form_class = 'blueForms'
#         self.helper.form_method = 'POST'
#         self.helper.form_action = 'location_delete'

# # this is the Scenario Pop-up form (not used)
#
# class ScenarioForm(forms.ModelForm):
#
#     class Meta:
#         model = Scenario
#         fields = ('project', 'scenario_date', 'scenario_title', 'counter',)
#         widgets = {'name': forms.Textarea(attrs={'rows': 4, 'cols': 20}),
#                    # 'scenario_date': DatePickerInput(format='%m/%d/%Y',
#                    #                                 attrs={'autocomplete': 'off', },
#                    #                                 ),
#                    }
#
#     def __init__(self, *args, **kwargs):
#         _user_id = kwargs.pop('user_id', None)
#
#         super(ScenarioForm, self).__init__(*args, **kwargs)
#
#         self.fields['user'].empty_label = '--- Select Person (required) ---'
#         if _user_id:
#             self.fields['user'].queryset = User.objects.filter(id=_user_id)
#             self.fields['user'].empty_label = None
#         else:
#             self.fields['user'].empty_label = '--- Select User (required) ---'


class ScenarioEditForm(forms.ModelForm):
    """

        Scenario Form - used in Create and Update
        this returns the Cost Tool

    """
    template_name = 'scenario/costtool/index.html'

    class Meta:
        model = Scenario
        fields = '__all__'

        # TODO: need to get minDate and maxDate working.  Should set a range of valid dates.
        # so far, I get a javascript error if either are set.  causes the scenario_date widget to
        # display the current date.
        minDate_tx = f"{(datetime.datetime.now() - datetime.timedelta(weeks=52)):%m/%d/%Y}"
        maxDate_tx = f"{datetime.datetime.now():%Y-%m-%d}"

        widgets = {'name': forms.Textarea(attrs={'rows': 4, 'cols': 25}),
                   'scenario_date': DatePickerInput(format='%m/%d/%Y',
                                                    attrs={'autocomplete': 'off', },
                                                    ),
                   }

    def __init__(self, *args, **kwargs):
        _user_id = kwargs.pop('user_id', None)

        super(ScenarioEditForm, self).__init__(*args, **kwargs)

        self.fields['user'].empty_label = '--- Select Person (required) ---'
        # self.fields['location'].empty_label = '--- Select Location ---'

        if _user_id:
            self.fields['user'].queryset = User.objects.filter(id=_user_id)
            self.fields['user'].empty_label = None
        else:
            self.fields['user'].empty_label = '--- Select User (required) ---'

        self.helper = FormHelper()
        self.helper.form_id = 'id-scenarioForm'
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            Fieldset(
                'Scenario with initial "Scenario Date": {{scenario.scenario_date}}',
                Div(
                    Div('scenario_date', css_class='col-sm-6', ),
                    css_class='row',
                ),
                Div(
                    Div('user', css_class='col-sm-6',),
                    # Div('location',css_class='col-sm-6',),
                    css_class='row',
                ),
                # Div(
                #     Div('person_hours',css_class='col-sm-6',),
                #     Div('equipment_hours',css_class='col-sm-6',),
                #     css_class='row'
                # ),
                'name',
                # 'city',
                # 'location',
            ),
            FormActions(
                Submit('save', 'Save changes'),
                HTML('<a class="btn btn-primary" href={% url next_url %}>Cancel</a>')
            )
        )

    def save(self, commit=True):
        instance = super(ScenarioEditForm, self).save(commit=False)
        if commit:
            instance.save()
        return instance


class ScenarioDeleteForm(forms.ModelForm):
    class Meta:
        model = Scenario
        fields = '__all__'

    success_url = reverse_lazy('scenario_list')

    def __init__(self, *args, **kwargs):
        super(ScenarioDeleteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-personForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'scenario_delete'
