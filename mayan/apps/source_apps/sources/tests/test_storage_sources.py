from mayan.apps.credentials.tests.mixins import StoredCredentialPasswordUsernameTestMixin
from mayan.apps.testing.tests.base import BaseTestCase

from .mixins.storage_source_mixins import StorageSourceBackendTestMixin


class StorageSourceBackendTestCase(
    StorageSourceBackendTestMixin, BaseTestCase
):
    auto_create_test_source = False

    def test_storage_arguments_template_default(self):
        TEST_SOURCE_STORAGE_BACKEND_ARGUMENTS_TEXT = '{\'location\': \'\'}'
        TEST_SOURCE_STORAGE_BACKEND_ARGUMENTS_OBJECT = {'location': ''}

        self._create_test_storage_source_backend(
            extra_backend_data={
                'storage_backend_arguments': TEST_SOURCE_STORAGE_BACKEND_ARGUMENTS_TEXT
            }
        )

        backend = self._test_source.get_backend_instance()

        storage_backend_arguments = backend.get_storage_backend_arguments()

        self.assertEqual(
            storage_backend_arguments,
            TEST_SOURCE_STORAGE_BACKEND_ARGUMENTS_OBJECT
        )


class StorageSourceBackendCredentialTestCase(
    StorageSourceBackendTestMixin, StoredCredentialPasswordUsernameTestMixin,
    BaseTestCase
):
    auto_create_test_source = False

    def test_storage_arguments_credential_template(self):
        TEST_SOURCE_STORAGE_BACKEND_ARGUMENTS_TEXT = '{\'username\': \'{{ credential.username }}\', \'password\': \'{{ credential.password }}\'}'
        TEST_SOURCE_STORAGE_BACKEND_ARGUMENTS_OBJECT = {
            'password': self._test_stored_credential._password,
            'username': self._test_stored_credential._username
        }

        self._create_test_storage_source_backend(
            extra_backend_data={
                'stored_credential_id': self._test_stored_credential.pk,
                'storage_backend_arguments': TEST_SOURCE_STORAGE_BACKEND_ARGUMENTS_TEXT
            }
        )

        backend = self._test_source.get_backend_instance()

        storage_backend_arguments = backend.get_storage_backend_arguments()

        self.assertEqual(
            storage_backend_arguments,
            TEST_SOURCE_STORAGE_BACKEND_ARGUMENTS_OBJECT
        )
