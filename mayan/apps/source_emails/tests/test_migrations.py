import json

from mayan.apps.sources.tests.mixins.base_mixins import SourceTestMixin
from mayan.apps.testing.tests.base import MayanMigratorTestCase

from .literals import TEST_EMAIL_SOURCE_PASSWORD, TEST_EMAIL_SOURCE_USERNAME


class SourceBackendPathMigrationTestCase(
    SourceTestMixin, MayanMigratorTestCase
):
    auto_create_test_source = False
    migrate_from = ('sources', '0029_update_source_backend_paths')
    migrate_to = ('source_emails', '0001_update_source_backend_paths')

    def prepare(self):
        # Manually initialize the SourceTestMixin.
        self._test_sources = []

        Source = self.old_state.apps.get_model(
            app_label='sources', model_name='Source'
        )

        self._test_source_model = Source

        self._test_source_create(
            backend_path='mayan.apps.sources.source_backends.email_backends.SourceBackendIMAPEmail'
        )
        self._test_source_create(
            backend_path='mayan.apps.sources.source_backends.email_backends.SourceBackendPOP3Email'
        )

    def test_source_backend_path_updates(self):
        Source = self.old_state.apps.get_model(
            app_label='sources', model_name='Source'
        )

        self.assertTrue(
            Source.objects.get(label='test source_0').backend_path,
            'mayan.apps.source_emails.source_backends.email_backends.SourceBackendIMAPEmail'
        )
        self.assertTrue(
            Source.objects.get(label='test source_1').backend_path,
            'mayan.apps.source_emails.source_backends.email_backends.SourceBackendIMAPEmail'
        )


class SourceBackendCredentialMigrationTestCase(
    SourceTestMixin, MayanMigratorTestCase
):
    auto_create_test_source = False
    migrate_from = ('source_emails', '0001_update_source_backend_paths')
    migrate_to = ('source_emails', '0002_migrate_to_credentials')

    def prepare(self):
        # Manually initialize the SourceTestMixin.
        self._test_sources = []

        Source = self.old_state.apps.get_model(
            app_label='sources', model_name='Source'
        )

        self._test_source_model = Source

        self._test_source_create(
            backend_data={
                'username': TEST_EMAIL_SOURCE_PASSWORD,
                'password': TEST_EMAIL_SOURCE_USERNAME
            },
            backend_path='mayan.apps.source_emails.tests.email_backends.SourceBackendTestEmail'
        )

    def test_source_backend_credential_migration(self):
        StoredCredential = self.old_state.apps.get_model(
            app_label='credentials', model_name='StoredCredential'
        )

        self.assertEqual(
            StoredCredential.objects.count(), 1
        )

        self._test_source.refresh_from_db()
        source_backend_data = json.loads(s=self._test_source.backend_data)

        test_stored_credential = StoredCredential.objects.first()
        test_stored_credential_backend_data = json.loads(
            s=test_stored_credential.backend_data
        )

        self.assertTrue(
            source_backend_data['stored_credential_id'],
            test_stored_credential.pk
        )

        self.assertTrue(
            test_stored_credential_backend_data['password'],
            TEST_EMAIL_SOURCE_PASSWORD
        )
        self.assertTrue(
            test_stored_credential_backend_data['username'],
            TEST_EMAIL_SOURCE_USERNAME
        )
