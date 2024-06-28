from mayan.apps.common.serialization import yaml_dump
from mayan.apps.forms import form_widgets, forms

from .models import DocumentTypeDriverConfiguration


class FormDocumentTypeFileMetadataDriverConfiguration(forms.ModelForm):
    class Meta:
        fields = ('enabled', 'arguments')
        model = DocumentTypeDriverConfiguration

    def __init__(self, driver_configuration=None, *args, **kwargs):
        self._driver_configuration = driver_configuration

        super().__init__(*args, **kwargs)

        if self.instance:
            arguments = self.instance.get_arguments()

            for key, value in arguments.items():
                self.initial[key] = value

        self.fields['arguments'].widget = form_widgets.HiddenInput()

    def clean(self):
        # Otherwise grab the values from the dynamic form and create
        # the argument JSON object.
        result = {}

        arguments = self.instance.get_arguments()

        for argument in arguments:
            if self.cleaned_data[argument] is not None:
                result[argument] = self.cleaned_data[argument]

        self.cleaned_data['arguments'] = yaml_dump(data=result)
