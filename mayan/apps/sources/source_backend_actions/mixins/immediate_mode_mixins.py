from ..interfaces import (
    SourceBackendActionInterface, SourceBackendActionInterfaceRequestRESTAPI,
    SourceBackendActionInterfaceTask
)

from .arguments import (
    argument_immediate_mode_optional, argument_immediate_mode_required
)
from .literals import DEFAULT_IMMEDIATE_MODE


class SourceBackendActionMixinImmediateMode:
    class Interface:
        class Model(SourceBackendActionInterface):
            class Argument:
                immediate_mode = argument_immediate_mode_optional

            def process_interface_context(self):
                super().process_interface_context()

                self.action_kwargs['immediate_mode'] = self.context['immediate_mode']

        class RESTAPI(SourceBackendActionInterfaceRequestRESTAPI):
            class Argument:
                immediate_mode = argument_immediate_mode_optional

            def process_interface_context(self):
                super().process_interface_context()

                self.action_kwargs['immediate_mode'] = self.context['immediate_mode']

        class Task(SourceBackendActionInterfaceTask):
            class Argument:
                immediate_mode = argument_immediate_mode_required

            def process_interface_context(self):
                super().process_interface_context()

                self.action_kwargs['immediate_mode'] = self.context['immediate_mode']

    def _background_task(self, immediate_mode, **kwargs):
        result = super()._background_task(**kwargs)

        result['immediate_mode'] = immediate_mode

        return result

    def get_task_kwargs(
        self, immediate_mode=DEFAULT_IMMEDIATE_MODE, **kwargs
    ):
        result = super().get_task_kwargs(**kwargs)

        result['action_interface_kwargs']['immediate_mode'] = immediate_mode

        return result
