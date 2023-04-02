from ..classes import SourceBackend
from ..source_backends.email_backends import SourceBackendEmailMixin
from ..source_backends.source_backend_mixins import (
    SourceBaseMixin, SourceBackendPeriodicMixin
)

__all__ = ('SourceBackendTestEmail',)


class SourceBackendTestEmail(
    SourceBackendEmailMixin, SourceBackendPeriodicMixin, SourceBaseMixin,
    SourceBackend
):
    label = 'Test email source backend'

    def get_shared_uploaded_files(self):
        data = self.get_model_instance().get_backend_data()

        message = getattr(
            self, 'content', data.get('_test_content')
        )

        return self.process_message(message=message)
