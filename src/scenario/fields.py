from django.core.exceptions import ValidationError
from django import forms


class ListTextWidget(forms.TextInput):
    def __init__(self, data_list, name, *args, **kwargs):
        super(ListTextWidget, self).__init__(*args, **kwargs)
        self._name = name
        self._list = data_list
        self.attrs.update({'list': 'list__%s' % self._name})

    def render(self, name, value, attrs=None, renderer=None):
        text_html = super(ListTextWidget, self).render(name, value, attrs=attrs)
        data_list = '<datalist id="list__%s">' % self._name
        for item in self._list:
            data_list += '<option value="%s">' % item
        data_list += '</datalist>'

        return text_html + data_list


class OptionalChoiceWidget(forms.MultiWidget):
    def decompress(self, value):
        # this might need to be tweaked if the name of a choice != value of a choice
        if value:  # indicates we have a updating object versus new one
            if value in [x[0] for x in self.widgets[0].choices]:
                return [value, ""]  # make it set the dropdown to choice
            else:
                return ["", value]  # keep dropdown to blank, set freetext
        return ["", ""]  # default for new object


class OptionalChoiceField(forms.MultiValueField):
    def __init__(self, choices, max_length=80, *args, **kwargs):
        """ sets the two fields as not required but will enforce that (at least) one is set in compress """
        fields = (forms.ChoiceField(choices=choices, required=False),
                  forms.CharField(required=False))
        self.widget = OptionalChoiceWidget(widgets=[f.widget for f in fields])
        super(OptionalChoiceField, self).__init__(required=False, fields=fields, *args, **kwargs)

    def compress(self, data_list):
        """ return the choicefield value if selected or character field value (if both empty, will throw exception """
        if not data_list:
            raise ValidationError('Need to select choice or enter text for this field')
        return data_list[0] or data_list[1]

    @staticmethod
    def is_hidden():
        return False
