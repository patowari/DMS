from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _

from mayan.apps.metadata.classes import MetadataLookup
from mayan.apps.templating.fields import ModelTemplateField
from mayan.apps.views.forms import ModelForm

from ..models.workflow_instance_models import WorkflowInstance
from ..models.workflow_transition_field_models import WorkflowTransitionField


class WorkflowTransitionFieldForm(ModelForm):
    fieldsets = (
        (
            _(message='Basic'), {
                'fields': ('name', 'label')
            }
        ), (
            _(message='Field'), {
                'fields': ('field_type', 'help_text')
            }
        ), (
            _(message='Value'), {
                'fields': ('lookup', 'required')
            }
        ), (
            _(message='Appearance'), {
                'fields': ('widget', 'widget_kwargs')
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lookup'] = ModelTemplateField(
            initial_help_text=format_lazy(
                '{}{}{}',
                self.fields['lookup'].help_text,
                _(message=' Available template context variables: '),
                MetadataLookup.get_as_help_text()
            ), model=WorkflowInstance, model_variable='workflow_instance',
            required=False
        )

    class Meta:
        fields = (
            'name', 'label', 'field_type', 'lookup', 'help_text', 'required',
            'widget', 'widget_kwargs'
        )
        model = WorkflowTransitionField
