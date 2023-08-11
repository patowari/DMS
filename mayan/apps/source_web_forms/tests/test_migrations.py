from mayan.apps.sources.tests.mixins.base_mixins import SourceTestMixin
from mayan.apps.testing.tests.base import MayanMigratorTestCase


class SourceBackendPathMigrationTestCase(
    SourceTestMixin, MayanMigratorTestCase
):
    auto_create_test_source = False
    migrate_from = ('sources', '0029_update_source_backend_paths')
    migrate_to = ('source_web_forms', '0001_update_source_backend_paths')

    def prepare(self):
        Source = self.old_state.apps.get_model(
            app_label='sources', model_name='Source'
        )
        self._test_source_backend_model = Source

        self._create_test_source(
            backend_path='mayan.apps.sources.source_backends.web_form_backends.SourceBackendWebForm'
        )

    def test_source_backend_path_updates(self):
        Source = self.old_state.apps.get_model(
            app_label='sources', model_name='Source'
        )

        self.assertTrue(
            Source.objects.get(label='test source_0').backend_path,
            'mayan.apps.source_web_forms.source_backends.SourceBackendWebForm'
        )
