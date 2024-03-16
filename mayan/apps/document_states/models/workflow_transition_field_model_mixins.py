import hashlib

from django.core import serializers

from mayan.apps.common.serialization import yaml_load


class WorkflowTransitionFieldBusinessLogicMixin:
    def get_hash(self):
        return hashlib.sha256(
            string=serializers.serialize(
                format='json', queryset=(self,)
            ).encode()
        ).hexdigest()

    def get_widget_kwargs(self):
        return yaml_load(
            stream=self.widget_kwargs or '{}'
        )
