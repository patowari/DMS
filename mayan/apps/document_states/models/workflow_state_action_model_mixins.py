import hashlib
import json

from django.conf import settings
from django.core import serializers
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from mayan.apps.templating.classes import Template


class WorkflowStateActionBusinessLogicMixin:
    def dumps(self, data):
        self.action_data = json.dumps(obj=data)
        self.save()

    def get_hash(self):
        return hashlib.sha256(
            string=serializers.serialize(
                format='json', queryset=(self,)
            ).encode()
        ).hexdigest()

    def evaluate_condition(self, workflow_instance):
        if self.has_condition():
            return Template(template_string=self.condition).render(
                context={'workflow_instance': workflow_instance}
            ).strip()
        else:
            return True

    def execute(self, context, workflow_instance):
        if self.evaluate_condition(workflow_instance=workflow_instance):
            try:
                self.get_class_instance().execute(context=context)
            except Exception as exception:
                self.error_log.create(
                    text='{}; {}'.format(
                        exception.__class__.__name__, exception
                    )
                )

                if settings.DEBUG or settings.TESTING:
                    raise
            else:
                self.error_log.all().delete()

    def get_class(self):
        return import_string(dotted_path=self.action_path)

    def get_class_instance(self):
        return self.get_class()(
            form_data=self.loads()
        )

    def get_class_label(self):
        try:
            return self.get_class().label
        except ImportError:
            return _('Unknown action type')

    def has_condition(self):
        return self.condition.strip()
    has_condition.help_text = _(
        'The state action will be executed, depending on the condition '
        'return value.'
    )
    has_condition.short_description = _('Has a condition?')

    def loads(self):
        return json.loads(s=self.action_data or '{}')
