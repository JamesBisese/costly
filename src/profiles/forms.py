from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, Field
from crispy_forms.bootstrap import FormActions
from django.contrib.auth import get_user_model

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
            Field('organization_tx', placeholder='eg. City of Raleigh, your company name, etc.'),
            Field('job_title'),
        )

    class Meta:
        model = User
        fields = ['name', 'phone_tx', 'job_title', 'organization_tx', 'email', ]


class ProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['user_type'].label = "Desired Level of Tool Use"

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False  # this was suggested in https://github.com/benmurden/django-intl-tel-input
        self.helper.layout = Layout(
            Field('bio'),
            Field('user_type'),
            FormActions(
                Submit('save', 'Save changes'),
                HTML('<a class="btn btn-info" href={% url "profiles:show_self" %}>Cancel</a>')
            )
        )

    class Meta:
        model = models.Profile
        fields = ['bio', 'user_type', ]
