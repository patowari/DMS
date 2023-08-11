from mayan.apps.sources.classes import SourceBackend
from mayan.apps.source_compressed.source_backends.compressed_mixins import SourceBackendMixinCompressed

from ..source_backend_actions.interactive_actions import (
    SourceBackendActionInteractiveDocumentUpload,
    SourceBackendActionInteractiveDocumentFileUpload
)
from ..source_backends.interactive_mixins import SourceBackendMixinInteractive


class SourceBackendTestInteractive(
    SourceBackendMixinInteractive, SourceBackend
):
    label = 'Test interactive source backend'


class SourceBackendTestInteractiveAction(
    SourceBackendMixinCompressed, SourceBackendMixinInteractive,
    SourceBackend
):
    action_class_list = (
        SourceBackendActionInteractiveDocumentFileUpload,
        SourceBackendActionInteractiveDocumentUpload
    )
    label = 'Test interactive source backend'
