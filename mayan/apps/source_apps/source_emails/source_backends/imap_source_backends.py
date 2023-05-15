import imaplib
import logging

from django.utils.translation import ugettext_lazy as _

from mayan.apps.source_apps.sources.classes import SourceBackend
from mayan.apps.source_apps.sources.exceptions import SourceException
from mayan.apps.source_apps.sources.source_backends.source_backend_mixins import SourceBackendMixinCompressedPeriodic

from .literals import (
    DEFAULT_EMAIL_IMAP_MAILBOX, DEFAULT_EMAIL_IMAP_SEARCH_CRITERIA,
    DEFAULT_EMAIL_IMAP_STORE_COMMANDS
)
from .mixins import SourceBackendEmailMixin

logger = logging.getLogger(name=__name__)


class SourceBackendIMAPEmail(
    SourceBackendMixinCompressedPeriodic, SourceBackendEmailMixin,
    SourceBackend
):
    label = _('IMAP email')

    @classmethod
    def get_form_field_widgets(cls):
        widgets = super().get_form_field_widgets()

        widgets.update(
            {
                'search_criteria': {
                    'class': 'django.forms.widgets.Textarea'
                },
                'store_commands': {
                    'class': 'django.forms.widgets.Textarea'
                }
            }
        )

        return widgets

    @classmethod
    def get_form_fields(cls):
        fields = super().get_form_fields()

        fields.update(
            {
                'mailbox': {
                    'class': 'django.forms.fields.CharField',
                    'default': DEFAULT_EMAIL_IMAP_MAILBOX,
                    'help_text': _(
                        'IMAP Mailbox from which to check for messages.'
                    ),
                    'kwargs': {
                        'max_length': 64,
                    },
                    'label': _('Mailbox')
                },
                'search_criteria': {
                    'blank': True,
                    'class': 'django.forms.fields.CharField',
                    'default': DEFAULT_EMAIL_IMAP_SEARCH_CRITERIA,
                    'help_text': _(
                        'Criteria to use when searching for messages to '
                        'process. Use the format specified in '
                        'https://tools.ietf.org/html/rfc2060.html#section-6.4.4'
                    ),
                    'label': _('Search criteria'),
                    'null': True,
                },
                'store_commands': {
                    'blank': True,
                    'class': 'django.forms.fields.CharField',
                    'default': DEFAULT_EMAIL_IMAP_STORE_COMMANDS,
                    'help_text': _(
                        'IMAP STORE command to execute on messages after '
                        'they are processed. One command per line. Use '
                        'the commands specified in '
                        'https://tools.ietf.org/html/rfc2060.html#section-6.4.6 or '
                        'the custom commands for your IMAP server.'
                    ),
                    'label': _('Store commands'),
                    'null': True, 'required': False
                },
                'execute_expunge': {
                    'class': 'django.forms.fields.BooleanField',
                    'default': True,
                    'help_text': _(
                        'Execute the IMAP expunge command after processing '
                        'each email message.'
                    ),
                    'label': _('Execute expunge'),
                    'required': False
                },
                'mailbox_destination': {
                    'blank': True,
                    'class': 'django.forms.fields.CharField',
                    'help_text': _(
                        'IMAP Mailbox to which processed messages will '
                        'be copied.'
                    ),
                    'label': _('Destination mailbox'),
                    'max_length': 96,
                    'null': True,
                    'required': False
                }
            }
        )

        return fields

    @classmethod
    def get_form_fieldsets(cls):
        fieldsets = super().get_form_fieldsets()

        fieldsets += (
            (
                _('IMAP protocol'), {
                    'fields': (
                        'mailbox', 'search_criteria', 'store_commands',
                        'execute_expunge', 'mailbox_destination'
                    )
                }
            ),
        )

        return fieldsets

    def get_shared_uploaded_files(self):
        dry_run = self.process_kwargs.get('dry_run', False)

        logger.debug(msg='Starting IMAP email fetch')
        logger.debug(
            'host: %s', self.kwargs['host']
        )
        logger.debug(
            'ssl: %s', self.kwargs['ssl']
        )

        if self.kwargs['ssl']:
            imap_module_name = 'IMAP4_SSL'
        else:
            imap_module_name = 'IMAP4'

        imap_module = getattr(imaplib, imap_module_name)

        imap_module_kwargs = {
            'host': self.kwargs['host'], 'port': self.kwargs['port']
        }

        with imap_module(**imap_module_kwargs) as server:
            credential = self.get_credential()
            password = credential.get('password')
            username = credential.get('username')

            server.login(password=password, user=username)

            try:
                server.select(
                    mailbox=self.kwargs['mailbox']
                )
            except Exception as exception:
                raise SourceException(
                    'Error selecting mailbox: {}; {}'.format(
                        self.kwargs['mailbox'], exception
                    )
                )
            else:
                try:
                    status, data = server.uid(
                        'SEARCH', None,
                        *self.kwargs['search_criteria'].strip().split()
                    )
                except Exception as exception:
                    raise SourceException(
                        'Error executing search command; {}'.format(
                            exception
                        )
                    )
                else:
                    if data:
                        # data is a space separated sequence of message uids.
                        uids = data[0].split()
                        logger.debug(
                            'messages count: %s', len(uids)
                        )
                        logger.debug('message uids: %s', uids)

                        for uid in uids:
                            logger.debug('message uid: %s', uid)

                            try:
                                status, data = server.uid(
                                    'FETCH', uid, '(RFC822)'
                                )
                            except Exception as exception:
                                raise SourceException(
                                    'Error fetching message uid: {}; {}'.format(
                                        uid, exception
                                    )
                                )
                            else:
                                try:
                                    shared_uploaded_files = self.process_message(
                                        message=data[0][1]
                                    )
                                except Exception as exception:
                                    raise SourceException(
                                        'Error processing message uid: {}; {}'.format(
                                            uid, exception
                                        )
                                    )
                                else:
                                    if not dry_run:
                                        if self.kwargs['store_commands']:
                                            for command in self.kwargs['store_commands'].split('\n'):
                                                try:
                                                    args = [uid]
                                                    args.extend(
                                                        command.strip().split(' ')
                                                    )
                                                    server.uid('STORE', *args)
                                                except Exception as exception:
                                                    raise SourceException(
                                                        'Error executing IMAP store command "{}" '
                                                        'on message uid {}; {}'.format(
                                                            command, uid, exception
                                                        )
                                                    )

                                        if self.kwargs['mailbox_destination']:
                                            try:
                                                server.uid(
                                                    'COPY', uid,
                                                    self.kwargs[
                                                        'mailbox_destination'
                                                    ]
                                                )
                                            except Exception as exception:
                                                raise SourceException(
                                                    'Error copying message uid {} to mailbox {}; '
                                                    '{}'.format(
                                                        uid, self.kwargs[
                                                            'mailbox_destination'
                                                        ], exception
                                                    )
                                                )

                                        if self.kwargs['execute_expunge']:
                                            server.expunge()

                                    return shared_uploaded_files
