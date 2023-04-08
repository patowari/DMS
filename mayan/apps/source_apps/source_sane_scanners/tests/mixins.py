from mayan.apps.source_apps.sources.source_backends.literals import SOURCE_UNCOMPRESS_CHOICE_NEVER
from mayan.apps.source_apps.sources.tests.mixins import SourceTestMixin

from ..source_backends import SourceBackendSANEScanner


class SANEScannerSourceTestMixin(SourceTestMixin):
    _create_source_method = '_create_test_sane_scanner_source'

    def _create_test_sane_scanner_source(self, extra_data=None):
        backend_data = {
            'device_name': 'test',
            'uncompress': SOURCE_UNCOMPRESS_CHOICE_NEVER,
            'arguments': '{test-picture: grid}'
        }

        if extra_data:
            backend_data.update(extra_data)

        self._create_test_source(
            backend_path=SourceBackendSANEScanner.get_class_path(),
            backend_data=backend_data
        )
