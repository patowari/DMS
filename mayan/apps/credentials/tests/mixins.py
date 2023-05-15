import json

from django.db.models import Q

from ..models import StoredCredential

from .literals import (
    TEST_STORED_CREDENTIAL_BACKEND_DATA_FIELDS,
    TEST_STORED_CREDENTIAL_BACKEND_DATA_PASSWORD,
    TEST_STORED_CREDENTIAL_BACKEND_DATA_USERNAME,
    TEST_STORED_CREDENTIAL_BACKEND_PATH,
    TEST_STORED_CREDENTIAL_INTERNAL_NAME, TEST_STORED_CREDENTIAL_LABEL,
    TEST_STORED_CREDENTIAL_LABEL_EDITED
)


class StoredCredentialAPIViewTestMixin:
    def _request_test_stored_credential_create_api_view(self):
        pk_list = list(
            StoredCredential.objects.values_list('pk', flat=True)
        )

        backend_data = json.dumps(
            obj=TEST_STORED_CREDENTIAL_BACKEND_DATA_FIELDS
        )

        response = self.post(
            viewname='rest_api:credential-list', data={
                'internal_name': TEST_STORED_CREDENTIAL_INTERNAL_NAME,
                'label': TEST_STORED_CREDENTIAL_LABEL,
                'backend_path': TEST_STORED_CREDENTIAL_BACKEND_PATH,
                'backend_data': backend_data
            }
        )

        try:
            self._test_stored_credential = StoredCredential.objects.get(
                ~Q(pk__in=pk_list)
            )
        except StoredCredential.DoesNotExist:
            self._test_stored_credential = None

        return response

    def _request_test_stored_credential_delete_api_view(self):
        return self.delete(
            viewname='rest_api:credential-detail', kwargs={
                'credential_id': self._test_stored_credential.pk
            }
        )

    def _request_test_stored_credential_detail_api_view(self):
        return self.get(
            viewname='rest_api:credential-detail', kwargs={
                'credential_id': self._test_stored_credential.pk
            }
        )

    def _request_test_stored_credential_edit_via_patch_api_view(self):
        return self.patch(
            viewname='rest_api:credential-detail', kwargs={
                'credential_id': self._test_stored_credential.pk
            }, data={
                'label': TEST_STORED_CREDENTIAL_LABEL_EDITED
            }
        )

    def _request_test_stored_credential_list_api_view(self):
        return self.get(viewname='rest_api:credential-list')


class StoredCredentialTestMixin:
    _test_stored_credential_backend_data = TEST_STORED_CREDENTIAL_BACKEND_DATA_FIELDS
    _test_stored_credential_backend_path = TEST_STORED_CREDENTIAL_BACKEND_PATH
    auto_create_test_credential = True

    def setUp(self):
        super().setUp()
        self._test_stored_credential_list = []

        if self.auto_create_test_credential:
            self._create_test_stored_credential()

    def _create_test_stored_credential(self, backend_data=None):
        total_test_stored_credential_count = len(
            self._test_stored_credential_list
        )
        label = '{}_{}'.format(
            TEST_STORED_CREDENTIAL_LABEL, total_test_stored_credential_count
        )

        if backend_data is None:
            backend_data = self._test_stored_credential_backend_data

        backend_data_serialized = json.dumps(
            obj=backend_data
        )

        self._test_stored_credential = StoredCredential.objects.create(
            backend_data=backend_data_serialized,
            backend_path=self._test_stored_credential_backend_path,
            internal_name=TEST_STORED_CREDENTIAL_INTERNAL_NAME, label=label
        )
        self._test_stored_credential_list.append(
            self._test_stored_credential
        )


class StoredCredentialPasswordUsernameTestMixin(StoredCredentialTestMixin):
    _test_stored_credential_backend_data = {
        'password': TEST_STORED_CREDENTIAL_BACKEND_DATA_PASSWORD,
        'username': TEST_STORED_CREDENTIAL_BACKEND_DATA_USERNAME
    }
    _test_stored_credential_backend_path = 'mayan.apps.credentials.credential_backends.CredentialBackendUsernamePassword'

    def _create_test_stored_credential(self, *args, **kwargs):
        super()._create_test_stored_credential(*args, **kwargs)

        self._test_stored_credential._password = self._test_stored_credential_backend_data['password']
        self._test_stored_credential._username = self._test_stored_credential_backend_data['username']


class StoredCredentialViewTestMixin:
    def _request_test_stored_credential_backend_selection_view(self):
        return self.post(
            viewname='credentials:stored_credential_backend_selection',
            data={
                'backend': TEST_STORED_CREDENTIAL_BACKEND_PATH,
            }
        )

    def _request_test_stored_credential_create_view(self):
        pk_list = list(
            StoredCredential.objects.values_list('pk', flat=True)
        )

        backend_data = json.dumps(
            obj=TEST_STORED_CREDENTIAL_BACKEND_DATA_FIELDS
        )

        data = {
            'backend_data': backend_data,
            'internal_name': TEST_STORED_CREDENTIAL_INTERNAL_NAME,
            'label': TEST_STORED_CREDENTIAL_LABEL
        }

        response = self.post(
            viewname='credentials:stored_credential_create', kwargs={
                'backend_path': TEST_STORED_CREDENTIAL_BACKEND_PATH,
            }, data=data
        )

        try:
            self._test_stored_credential = StoredCredential.objects.get(
                ~Q(pk__in=pk_list)
            )
        except StoredCredential.DoesNotExist:
            self._test_stored_credential = None

        return response

    def _request_test_stored_credential_delete_view(self):
        return self.post(
            viewname='credentials:stored_credential_delete', kwargs={
                'stored_credential_id': self._test_stored_credential.pk
            }
        )

    def _request_test_stored_credential_edit_view(self):
        return self.post(
            viewname='credentials:stored_credential_edit', kwargs={
                'stored_credential_id': self._test_stored_credential.pk
            }, data={
                'label': TEST_STORED_CREDENTIAL_LABEL_EDITED,
                'internal_name': self._test_stored_credential.internal_name
            }
        )

    def _request_test_stored_credential_list_view(self):
        return self.get(viewname='credentials:stored_credential_list')
