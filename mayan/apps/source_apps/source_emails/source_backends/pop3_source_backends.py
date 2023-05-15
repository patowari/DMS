import logging
import poplib

from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from mayan.apps.source_apps.sources.classes import SourceBackend
from mayan.apps.source_apps.sources.source_backends.source_backend_mixins import SourceBackendMixinCompressedPeriodic

from .literals import DEFAULT_EMAIL_POP3_TIMEOUT
from .mixins import SourceBackendEmailMixin

logger = logging.getLogger(name=__name__)


class SourceBackendPOP3Email(
    SourceBackendMixinCompressedPeriodic, SourceBackendEmailMixin,
    SourceBackend
):
    label = _('POP3 email')

    @classmethod
    def get_form_fields(cls):
        fields = super().get_form_fields()

        fields.update(
            {
                'timeout': {
                    'class': 'django.forms.fields.IntegerField',
                    'default': DEFAULT_EMAIL_POP3_TIMEOUT,
                    'kwargs': {
                        'min_value': 0
                    },
                    'label': _('Timeout')
                }
            }
        )

        return fields

    @classmethod
    def get_form_fieldsets(cls):
        fieldsets = super().get_form_fieldsets()

        fieldsets += (
            (
                _('POP3 protocol'), {
                    'fields': ('timeout',)
                }
            ),
        )

        return fieldsets

    def get_shared_uploaded_files(self):
        dry_run = self.process_kwargs.get('dry_run', False)

        logger.debug(msg='Starting POP3 email fetch')
        logger.debug(
            'host: %s', self.kwargs['host']
        )
        logger.debug(
            'ssl: %s', self.kwargs['ssl']
        )

        if self.kwargs['ssl']:
            pop3_module_name = 'POP3_SSL'
        else:
            pop3_module_name = 'POP3'

        pop3_module = getattr(poplib, pop3_module_name)

        kwargs = {
            'host': self.kwargs['host'], 'port': self.kwargs['port'],
            'timeout': self.kwargs['timeout']
        }

        server = pop3_module(**kwargs)
        try:
            credential = self.get_credential()
            password = credential.get('password')
            username = credential.get('username')

            server.getwelcome()
            server.user(username)
            server.pass_(password)

            messages_info = server.list()

            logger.debug(msg='messages_info:')
            logger.debug(msg=messages_info)
            logger.debug(
                'messages count: %s', len(
                    messages_info[1]
                )
            )

            for message_info in messages_info[1]:
                message_number, message_size = message_info.split()
                message_number = int(message_number)

                logger.debug('message_number: %s', message_number)
                logger.debug('message_size: %s', message_size)

                message_lines = server.retr(which=message_number)[1]
                message_complete = force_text(
                    s=b'\n'.join(message_lines)
                )

                shared_uploaded_files = self.process_message(
                    message=message_complete
                )
                if not dry_run:
                    server.dele(which=message_number)

                return shared_uploaded_files
        finally:
            server.quit()
