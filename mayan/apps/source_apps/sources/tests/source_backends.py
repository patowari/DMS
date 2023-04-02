from ..classes import SourceBackend
from ..source_backends.source_backend_mixins import (
    SourceBaseMixin, SourceBackendPeriodicMixin
)

__all__ = ('SourceBackendSimple', 'SourceBackendTestPeriodic')


class SourceBackendSimple(SourceBaseMixin, SourceBackend):
    label = 'Test source backend'

    def process_documents(self, dry_run=False):
        """Do nothing. This method is added to allow view testing."""


class SourceBackendTestPeriodic(
    SourceBackendPeriodicMixin, SourceBaseMixin, SourceBackend
):
    label = 'Test periodic source backend'
