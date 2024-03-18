import hashlib

from django.core import serializers
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from mayan.apps.common.serialization import yaml_load
from mayan.apps.common.utils import comma_splitter
from mayan.apps.templating.classes import Template


class WorkflowTransitionFieldBusinessLogicMixin:
    def get_hash(self):
        return hashlib.sha256(
            string=serializers.serialize(
                format='json', queryset=(self,)
            ).encode()
        ).hexdigest()

    def get_lookup_values(self, workflow_instance):
        template = Template(template_string=self.lookup)
        return comma_splitter(
            template.render(
                context={'workflow_instance': workflow_instance}
            )
        )

    def get_widget_kwargs(self):
        return yaml_load(
            stream=self.widget_kwargs or '{}'
        )

    def validate_value(self, value, workflow_instance):
        if self.lookup:
            lookup_options = self.get_lookup_values(
                workflow_instance=workflow_instance
            )

            if value and value not in lookup_options:
                raise ValidationError(
                    message=_(
                        message='Value is not one of the provided options.'
                    )
                )
