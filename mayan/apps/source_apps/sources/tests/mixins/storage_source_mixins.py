from ..literals import TEST_SOURCE_BACKEND_STORAGE_PATH

from .base import SourceTestMixin


class StorageSourceBackendTestMixin(SourceTestMixin):
    _create_source_method = '_create_test_storage_source_backend'

    def _create_test_storage_source_backend(self, extra_backend_data=None):
        backend_data = {}

        if extra_backend_data:
            backend_data.update(extra_backend_data)

        self._create_test_source(
            backend_data=backend_data,
            backend_path=TEST_SOURCE_BACKEND_STORAGE_PATH,
        )
