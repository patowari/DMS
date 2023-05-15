from ...source_backends.literals import DEFAULT_PERIOD_INTERVAL

from ..literals import TEST_SOURCE_BACKEND_PERIODIC_PATH

from .base import SourceTestMixin


class PeriodicSourceBackendTestMixin(SourceTestMixin):
    _create_source_method = '_create_test_periodic_source_backend'

    def _create_test_periodic_source_backend(self, extra_data=None):
        backend_data = {
            'interval': DEFAULT_PERIOD_INTERVAL
        }

        if extra_data:
            backend_data.update(extra_data)

        self._create_test_source(
            backend_path=TEST_SOURCE_BACKEND_PERIODIC_PATH,
            backend_data=backend_data
        )
