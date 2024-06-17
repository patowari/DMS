
from mayan.apps.forms import forms

from .models import DocumentTypeDriverConfiguration


class FormDocumentTypeFileMetadataDriverConfiguration(forms.ModelForm):
    class Meta:
        fields = ('enabled',)
        model = DocumentTypeDriverConfiguration
