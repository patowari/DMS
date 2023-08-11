from ..classes import SourceBackend
from ..permissions import permission_sources_edit, permission_sources_view
from ..source_backend_actions.base import SourceBackendAction
from ..source_backend_actions.interfaces import (
    SourceBackendActionInterfaceRequestRESTAPI,
    SourceBackendActionInterfaceRequestView,
    SourceBackendActionInterfaceTask
)

from .literals import (
    TEST_SOURCE_ACTION_CONFIRM_FALSE_NAME,
    TEST_SOURCE_ACTION_CONFIRM_TRUE_NAME
)


class SourceBackendActionTestConfirmFalse(SourceBackendAction):
    confirmation = False
    name = TEST_SOURCE_ACTION_CONFIRM_FALSE_NAME
    permission = permission_sources_view

    class Interface:
        class RESTAPI(SourceBackendActionInterfaceRequestRESTAPI):
            """Empty interface. No arguments or processing."""

        class Task(SourceBackendActionInterfaceTask):
            """Empty interface. No arguments or processing."""

        class View(SourceBackendActionInterfaceRequestView):
            """Empty interface. No arguments or processing."""


class SourceBackendActionTestConfirmTrue(SourceBackendAction):
    confirmation = True
    name = TEST_SOURCE_ACTION_CONFIRM_TRUE_NAME
    permission = permission_sources_edit

    class Interface:
        class RESTAPI(SourceBackendActionInterfaceRequestRESTAPI):
            """Empty interface. No arguments or processing."""

        class Task(SourceBackendActionInterfaceTask):
            """Empty interface. No arguments or processing."""

        class View(SourceBackendActionInterfaceRequestView):
            """Empty interface. No arguments or processing."""


class SourceBackendTest(SourceBackend):
    action_class_list = (
        SourceBackendActionTestConfirmFalse,
        SourceBackendActionTestConfirmTrue
    )
    label = 'Test source backend'
