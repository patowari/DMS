from mayan.apps.credentials.tests.mixins import StoredCredentialPasswordUsernameTestMixin
from mayan.apps.source_apps.sources.source_backends.literals import (
    DEFAULT_PERIOD_INTERVAL, SOURCE_UNCOMPRESS_CHOICE_NEVER
)
from mayan.apps.source_apps.sources.tests.mixins.source_view_mixins import SourceViewTestMixin
from mayan.apps.source_apps.sources.tests.mixins.base import SourceTestMixin

from ..source_backends.imap_source_backends import SourceBackendIMAPEmail
from ..source_backends.literals import (
    DEFAULT_EMAIL_IMAP_MAILBOX, DEFAULT_EMAIL_IMAP_SEARCH_CRITERIA,
    DEFAULT_EMAIL_IMAP_STORE_COMMANDS, DEFAULT_EMAIL_POP3_TIMEOUT,
    DEFAULT_EMAIL_METADATA_ATTACHMENT_NAME
)
from ..source_backends.pop3_source_backends import SourceBackendPOP3Email

from .literals import (
    TEST_EMAIL_ATTACHMENT_AND_INLINE, TEST_EMAIL_SOURCE_PASSWORD,
    TEST_EMAIL_SOURCE_USERNAME, TEST_SOURCE_BACKEND_EMAIL_PATH
)


class CredentialSourceTestMixin(StoredCredentialPasswordUsernameTestMixin):
    _test_stored_credential_backend_data = {
        'password': TEST_EMAIL_SOURCE_PASSWORD,
        'username': TEST_EMAIL_SOURCE_USERNAME
    }


class EmailSourceBackendTestMixin(
    SourceTestMixin, CredentialSourceTestMixin
):
    _create_source_method = '_create_test_email_source_backend'
    _test_email_source_content = None

    def _create_test_email_source_backend(self, extra_data=None):
        backend_data = {
            '_test_content': TEST_EMAIL_ATTACHMENT_AND_INLINE,
            'document_type_id': self._test_document_type.pk,
            'host': '',
            'interval': DEFAULT_PERIOD_INTERVAL,
            'metadata_attachment_name': DEFAULT_EMAIL_METADATA_ATTACHMENT_NAME,
            'port': '',
            'ssl': True,
            'store_body': False,
            'stored_credential_id': self._test_stored_credential.pk
        }

        if extra_data:
            backend_data.update(extra_data)

        self._create_test_source(
            backend_path=TEST_SOURCE_BACKEND_EMAIL_PATH,
            backend_data=backend_data
        )


class IMAPEmailSourceTestMixin(SourceTestMixin, CredentialSourceTestMixin):
    _create_source_method = '_create_test_imap_email_source'

    def _create_test_imap_email_source(self, extra_data=None):
        backend_data = {
            'document_type_id': self._test_document_type.pk,
            'execute_expunge': True,
            'host': '',
            'interval': DEFAULT_PERIOD_INTERVAL,
            'mailbox': DEFAULT_EMAIL_IMAP_MAILBOX,
            'mailbox_destination': '',
            'metadata_attachment_name': DEFAULT_EMAIL_METADATA_ATTACHMENT_NAME,
            'port': '',
            'search_criteria': DEFAULT_EMAIL_IMAP_SEARCH_CRITERIA,
            'ssl': True,
            'store_body': False,
            'store_commands': DEFAULT_EMAIL_IMAP_STORE_COMMANDS,
            'stored_credential_id': self._test_stored_credential.pk,
            'uncompress': SOURCE_UNCOMPRESS_CHOICE_NEVER,
        }

        if extra_data:
            backend_data.update(extra_data)

        self._create_test_source(
            backend_path=SourceBackendIMAPEmail.get_class_path(),
            backend_data=backend_data
        )


class POP3EmailSourceTestMixin(SourceTestMixin, CredentialSourceTestMixin):
    _create_source_method = '_create_test_pop3_email_source'

    def _create_test_pop3_email_source(self, extra_data=None):
        backend_data = {
            'document_type_id': self._test_document_type.pk,
            'host': '',
            'interval': DEFAULT_PERIOD_INTERVAL,
            'metadata_attachment_name': DEFAULT_EMAIL_METADATA_ATTACHMENT_NAME,
            'port': '',
            'ssl': True,
            'store_body': False,
            'stored_credential_id': self._test_stored_credential.pk,
            'timeout': DEFAULT_EMAIL_POP3_TIMEOUT,
            'uncompress': SOURCE_UNCOMPRESS_CHOICE_NEVER
        }

        if extra_data:
            backend_data.update(extra_data)

        self._create_test_source(
            backend_path=SourceBackendPOP3Email.get_class_path(),
            backend_data=backend_data
        )


class EmailSourceBackendViewTestMixin(
    SourceViewTestMixin, CredentialSourceTestMixin
):
    def _request_test_email_source_create_view(self, extra_data=None):
        data = {
            'document_type_id': self._test_document_type.pk,
            'host': '127.0.0.1',
            'interval': DEFAULT_PERIOD_INTERVAL,
            'metadata_attachment_name': DEFAULT_EMAIL_METADATA_ATTACHMENT_NAME,
            'port': '0',
            'ssl': True,
            'store_body': False,
            'stored_credential_id': self._test_stored_credential.pk
        }

        if extra_data:
            data.update(extra_data)

        return self._request_test_source_create_view(
            backend_path=TEST_SOURCE_BACKEND_EMAIL_PATH, extra_data=data
        )
