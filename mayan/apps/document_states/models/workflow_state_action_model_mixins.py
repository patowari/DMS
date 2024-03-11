import hashlib

from django.conf import settings
from django.core import serializers
from django.utils.translation import gettext_lazy as _

from mayan.apps.templating.classes import Template

from ..literals import (
    GRAPHVIZ_ID_STATE_ACTION, GRAPHVIZ_SYMBOL_CONDITIONAL,
    WORKFLOW_ACTION_WHEN_CHOICES
)


class WorkflowStateActionBusinessLogicMixin:
    def do_diagram_generate(self, diagram):
        if self.enabled:
            if self.has_condition():
                markup_state_action_label = '{} {}'.format(
                    self.label, GRAPHVIZ_SYMBOL_CONDITIONAL
                )
            else:
                markup_state_action_label = self.label

            markup_state_action_name = self.get_graph_id()
            markup_state_action_state = self.state.get_graph_id()

            node_kwargs = {
                'label': markup_state_action_label,
                'name': markup_state_action_name,
                'shape': 'box'
            }
            diagram.node(**node_kwargs)

            state_action_choice_dict = dict(WORKFLOW_ACTION_WHEN_CHOICES)
            edge_label = str(
                state_action_choice_dict[self.when]
            )
            edge_kwargs = {
                'arrowhead': 'dot',
                'arrowtail': 'dot',
                'dir': 'both',
                'label': edge_label,
                'head_name': markup_state_action_name,
                'style': 'dashed',
                'tail_name': markup_state_action_state
            }

            diagram.edge(**edge_kwargs)

    def get_graph_id(self):
        return '{}{}'.format(GRAPHVIZ_ID_STATE_ACTION, self.pk)

    def get_hash(self):
        return hashlib.sha256(
            string=serializers.serialize(
                format='json', queryset=(self,)
            ).encode()
        ).hexdigest()

    def evaluate_condition(self, workflow_instance):
        if self.has_condition():
            template = Template(template_string=self.condition)
            context = {'workflow_instance': workflow_instance}
            return template.render(context=context).strip()
        else:
            return True

    def execute(self, context, workflow_instance):
        if self.evaluate_condition(workflow_instance=workflow_instance):
            context.update(
                {
                    'workflow_instance': workflow_instance
                }
            )

            try:
                backend_instance = self.get_backend_instance()
                backend_instance.execute(context=context)
            except Exception as exception:
                self.error_log.create(
                    text='{}; {}'.format(
                        exception.__class__.__name__, exception
                    )
                )

                if settings.DEBUG or settings.TESTING:
                    raise
            else:
                queryset_error_log = self.error_log.all()
                queryset_error_log.delete()

    def has_condition(self):
        return self.condition.strip()

    has_condition.help_text = _(
        message='The state action will be executed, depending on the condition '
        'return value.'
    )
    has_condition.short_description = _(message='Has a condition?')
