from mayan.apps.source_apps.sources.classes import SourceBackend
from mayan.apps.source_apps.sources.source_backends.source_backend_mixins import SourceBackendMixinPeriodic

from ..source_backends.mixins import SourceBackendEmailMixin

__all__ = ('SourceBackendTestEmail',)


class SourceBackendTestEmail(
    SourceBackendEmailMixin, SourceBackendMixinPeriodic, SourceBackend
):
    label = 'Test email source backend'

    def get_shared_uploaded_files(self):
        data = self.get_model_instance().get_backend_data()

        message = getattr(
            self, 'content', data.get('_test_content')
        )

        return self.process_message(message=message)
