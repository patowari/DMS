from mayan.apps.testing.tests.base import MayanMigratorTestCase

from .mixins.base_mixins import SourceTestMixin


class SourceBackendPathMigrationTestCase(
    SourceTestMixin, MayanMigratorTestCase
):
    auto_create_test_source = False
    migrate_from = ('sources', '0028_auto_20210905_0558')
    migrate_to = ('sources', '0029_update_source_backend_paths')

    def prepare(self):
        Source = self.old_state.apps.get_model(
            app_label='sources', model_name='Source'
        )
        self._test_source_backend_model = Source

        self._create_test_source(
            backend_path='mayan.apps.sources.source_backends.email_backends.SourceBackendIMAPEmail'
        )
        self._create_test_source(
            backend_path='mayan.apps.sources.source_backends.email_backends.SourceBackendPOP3Email'
        )
        self._create_test_source(
            backend_path='mayan.apps.sources.source_backends.sane_scanner_backends.SourceBackendSANEScanner'
        )
        self._create_test_source(
            backend_path='mayan.apps.sources.source_backends.staging_folder_backends.SourceBackendStagingFolder'
        )
        self._create_test_source(
            backend_path='mayan.apps.sources.source_backends.watch_folder_backends.SourceBackendWatchFolder'
        )
        self._create_test_source(
            backend_path='mayan.apps.sources.source_backends.web_form_backends.SourceBackendWebForm'
        )

    def test_source_backend_path_updates(self):
        Source = self.old_state.apps.get_model(
            app_label='sources', model_name='Source'
        )

        self.assertTrue(
            Source.objects.get(label='test source_0').backend_path,
            'mayan.apps.source_apps.sources.source_backends.email_backends.SourceBackendIMAPEmail'
        )
        self.assertTrue(
            Source.objects.get(label='test source_1').backend_path,
            'mayan.apps.source_apps.sources.source_backends.email_backends.SourceBackendIMAPEmail'
        )
        self.assertTrue(
            Source.objects.get(label='test source_2').backend_path,
            'mayan.apps.source_apps.sources.source_backends.sane_scanner_backends.SourceBackendSANEScanner'
        )
        self.assertTrue(
            Source.objects.get(label='test source_3').backend_path,
            'mayan.apps.source_apps.sources.source_backends.staging_folder_backends.SourceBackendStagingFolder'
        )
        self.assertTrue(
            Source.objects.get(label='test source_4').backend_path,
            'mayan.apps.source_apps.sources.source_backends.watch_folder_backends.SourceBackendWatchFolder'
        )
        self.assertTrue(
            Source.objects.get(label='test source_5').backend_path,
            'mayan.apps.source_apps.sources.source_backends.web_form_backends.SourceBackendWebForm'
        )
