from __future__ import unicode_literals
import datetime
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from django.contrib.auth import get_user_model

from bootstrap_datepicker_plus import DatePickerInput
# from intl_tel_input.widgets import IntlTelInputWidget

from . import models


User = get_user_model()


class UserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False
        self.helper.layout = Layout(
            Field('name'),
            Field('email'),
            Field('phone_tx'),
            Field('organization_tx'),
            Field('job_title'),


        )

    class Meta:
        model = User
        fields = ['name', 'phone_tx', 'job_title', 'organization_tx', 'email',]


class ProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['user_type'].label = "Desired Level of Tool Use"

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False  # this was suggested in https://github.com/benmurden/django-intl-tel-input
        self.helper.layout = Layout(
            # Field('picture'),
            Field('bio'),
            Field('user_type'),
            # Field('favoriteDate'),
            #Submit('update', 'Update', css_class="btn-sm"),
            FormActions(
                Submit('save', 'Save changes'),
                HTML('<a class="btn btn-info" href={% url "profiles:show_self" %}>Cancel</a>')
            )
        )

    class Meta:
        model = models.Profile
        fields = ['bio', 'user_type', ] # 'picture', 'favoriteDate'

        # minDate_tx = f"{(datetime.datetime.now() - datetime.timedelta(weeks=4)):%Y-%m-%d}"
        # maxDate_tx = f"{datetime.datetime.now():%Y-%m-%d}"

        # widgets = {
        #            'favoriteDate': DatePickerInput(format='%Y-%m-%d',
        #                                            attrs={'autocomplete': 'off', },
        #                                            options={'debug': True,
        #                                                     # "minDate": "2018-10-25", #minDate_tx, #
        #                                                     # "maxDate": "2018-11-06", #maxDate_tx, #
        #                                                     }),
        #            }