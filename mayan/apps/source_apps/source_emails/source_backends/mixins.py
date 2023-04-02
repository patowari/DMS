import itertools
import logging

from flanker import mime

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils.encoding import force_bytes
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.serialization import yaml_load
from mayan.apps.metadata.models import MetadataType
from mayan.apps.storage.models import SharedUploadedFile

from .literals import DEFAULT_EMAIL_METADATA_ATTACHMENT_NAME

__all__ = ()
logger = logging.getLogger(name=__name__)


class SourceBackendEmailMixin:
    @classmethod
    def get_setup_form_fieldsets(cls):
        fieldsets = super().get_setup_form_fieldsets()

        fieldsets += (
            (
                _('Common email options'), {
                    'fields': (
                        'host', 'ssl', 'port', 'username', 'password',
                        'store_body'
                    )
                },
            ), (
                _('Metadata'), {
                    'fields': (
                        'metadata_attachment_name', 'from_metadata_type_id',
                        'subject_metadata_type_id',
                        'message_id_metadata_type_id',
                    )
                }
            ),
        )

        return fieldsets

    @classmethod
    def get_setup_form_schema(cls):
        result = super().get_setup_form_schema()

        result['fields'].update(
            {
                'host': {
                    'class': 'django.forms.CharField',
                    'label': _('Host'),
                    'kwargs': {
                        'max_length': 128
                    },
                    'required': True
                },
                'ssl': {
                    'class': 'django.forms.BooleanField',
                    'default': True,
                    'label': _('SSL'),
                    'required': False
                },
                'port': {
                    'class': 'django.forms.IntegerField',
                    'help_text': _(
                        'Typical choices are 110 for POP3, 995 for POP3 '
                        'over SSL, 143 for IMAP, 993 for IMAP over SSL.'
                    ),
                    'kwargs': {
                        'min_value': 0
                    },
                    'label': _('Port'),
                },
                'username': {
                    'class': 'django.forms.CharField',
                    'kargs': {
                        'max_length': 128,
                    },
                    'label': _('Username'),
                },
                'password': {
                    'class': 'django.forms.CharField',
                    'kargs': {
                        'max_length': 128,
                    },
                    'label': _('Password'),
                    'required': False,
                },
                'metadata_attachment_name': {
                    'class': 'django.forms.CharField',
                    'default': DEFAULT_EMAIL_METADATA_ATTACHMENT_NAME,
                    'help_text': _(
                        'Name of the attachment that will contains the metadata type '
                        'names and value pairs to be assigned to the rest of the '
                        'downloaded attachments.'
                    ),
                    'kargs': {
                        'max_length': 128,
                    },
                    'label': _('Metadata attachment name'),
                },
                'from_metadata_type_id': {
                    'blank': True,
                    'class': 'django.forms.ChoiceField',
                    'help_text': _(
                        'Select a metadata type to store the email\'s '
                        '"from" value. Must be a valid metadata type for '
                        'the document type selected previously.'
                    ),
                    'kwargs': {
                        'choices': itertools.chain(
                            [
                                (None, '---------')
                            ], [
                                (instance.id, instance) for instance in MetadataType.objects.all()
                            ]
                        )
                    },
                    'label': _('From metadata type'),
                    'null': True,
                    'required': False
                },
                'subject_metadata_type_id': {
                    'blank': True,
                    'class': 'django.forms.ChoiceField',
                    'help_text': _(
                        'Select a metadata type to store the email\'s '
                        'subject value. Must be a valid metadata type for '
                        'the document type selected previously.'
                    ),
                    'kwargs': {
                        'choices': itertools.chain(
                            [
                                (None, '---------')
                            ],
                            [
                                (instance.id, instance) for instance in MetadataType.objects.all()
                            ]
                        )
                    },
                    'label': _('Subject metadata type'),
                    'null': True,
                    'required': False
                },
                'message_id_metadata_type_id': {
                    'blank': True,
                    'class': 'django.forms.ChoiceField',
                    'help_text': _(
                        'Select a metadata type to store the email\'s '
                        'message ID value. Must be a valid metadata type '
                        'for the document type selected previously.'
                    ),
                    'kwargs': {
                        'choices': itertools.chain(
                            [
                                (None, '---------')
                            ],
                            [
                                (instance.id, instance) for instance in MetadataType.objects.all()
                            ]
                        )
                    },
                    'label': _('Message ID metadata type'),
                    'null': True,
                    'required': False
                },
                'store_body': {
                    'class': 'django.forms.BooleanField',
                    'default': True,
                    'help_text': _(
                        'Store the body of the email as a text document.'
                    ),
                    'label': _('Store email body'),
                    'required': False
                }
            }
        )
        result['field_order'] = (
            'host', 'ssl', 'port', 'username', 'password',
            'metadata_attachment_name', 'from_metadata_type_id',
            'subject_metadata_type_id', 'message_id_metadata_type_id',
            'store_body'
        ) + result['field_order']

        result['widgets'].update(
            {
                'password': {
                    'class': 'django.forms.widgets.PasswordInput',
                    'kwargs': {
                        'render_value': True
                    }
                },
                'from_metadata_type_id': {
                    'class': 'django.forms.widgets.Select', 'kwargs': {
                        'attrs': {'class': 'select2'},
                    }
                },
                'subject_metadata_type_id': {
                    'class': 'django.forms.widgets.Select', 'kwargs': {
                        'attrs': {'class': 'select2'},
                    }
                },
                'message_id_metadata_type_id': {
                    'class': 'django.forms.widgets.Select', 'kwargs': {
                        'attrs': {'class': 'select2'},
                    }
                }
            }
        )

        return result

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.document_metadata = {}

    def process_message(self, message):
        message = mime.from_string(
            string=force_bytes(s=message)
        )

        shared_uploaded_files = self._process_message(message=message)

        # Process source metadata after messages to avoid the metadata
        # attachment to be used to override the source metadata.

        from_metadata_type = self.get_from_metadata_type()
        if from_metadata_type:
            self.document_metadata[from_metadata_type.pk] = message.headers.get('From')

        subject_metadata_type = self.get_subject_metadata_type()
        if subject_metadata_type:
            self.document_metadata[subject_metadata_type.pk] = message.headers.get('Subject')

        message_id_metadata_type = self.get_message_id_metadata_type()
        if message_id_metadata_type:
            self.document_metadata[message_id_metadata_type.pk] = message.headers.get('Message-ID')

        return shared_uploaded_files

    def _process_message(self, message):
        counter = 1
        shared_uploaded_files = []

        # Messages are tree based, do nested processing of message parts until
        # a message with no children is found, then work out way up.
        if message.parts:
            for part in message.parts:
                part_shared_uploaded_files = self._process_message(
                    message=part
                )

                shared_uploaded_files.extend(part_shared_uploaded_files)
        else:
            # Treat inlines as attachments, both are extracted and saved as
            # documents.
            if message.is_attachment() or message.is_inline():
                # Reject zero length attachments.
                if len(message.body) == 0:
                    return shared_uploaded_files

                label = message.detected_file_name or 'attachment-{}'.format(
                    counter
                )
                counter += 1

                with ContentFile(content=message.body, name=label) as file_object:
                    if label == self.kwargs['metadata_attachment_name']:
                        metadata_dictionary = yaml_load(
                            stream=file_object.read()
                        )
                        logger.debug(
                            'Got metadata dictionary: %s',
                            metadata_dictionary
                        )
                        for metadata_name, value in metadata_dictionary.items():
                            metadata = MetadataType.objects.get(
                                name=metadata_name
                            )
                            self.document_metadata[metadata.pk] = value
                    else:
                        shared_uploaded_files.append(
                            SharedUploadedFile.objects.create(
                                file=file_object, filename=label
                            )
                        )
            else:
                # If it is not an attachment then it should be a body message
                # part. Another option is to use message.is_body().
                if message.detected_content_type == 'text/html':
                    label = 'email_body.html'
                else:
                    label = 'email_body.txt'

                if self.kwargs['store_body']:
                    with ContentFile(content=force_bytes(message.body), name=label) as file_object:
                        shared_uploaded_files.append(
                            SharedUploadedFile.objects.create(
                                file=file_object, filename=label
                            )
                        )

        return shared_uploaded_files

    def callback(self, document_file, **kwargs):
        for metadata_type_id, value in kwargs['document_metadata'].items():
            metadata_type = MetadataType.objects.get(pk=metadata_type_id)

            document_file.document.metadata.create(
                metadata_type=metadata_type, value=value
            )

    def clean(self):
        document_type = self.get_document_type()

        form_metadata_type = self.get_from_metadata_type()
        subject_metadata_type = self.get_subject_metadata_type()
        message_id_metadata_type = self.get_message_id_metadata_type()

        if form_metadata_type:
            if not document_type.metadata.filter(metadata_type=form_metadata_type).exists():
                raise ValidationError(
                    message={
                        'from_metadata_type': _(
                            '"From" metadata type "%(metadata_type)s" is '
                            'not valid for the document '
                            'type: %(document_type)s'
                        ) % {
                            'metadata_type': form_metadata_type,
                            'document_type': document_type
                        }
                    }
                )

        if subject_metadata_type:
            if not document_type.metadata.filter(metadata_type=subject_metadata_type).exists():
                raise ValidationError(
                    message={
                        'subject_metadata_type': _(
                            'Subject metadata type "%(metadata_type)s" '
                            'is not valid for the document '
                            'type: %(document_type)s'
                        ) % {
                            'metadata_type': subject_metadata_type,
                            'document_type': document_type
                        }
                    }
                )

        if message_id_metadata_type:
            if not document_type.metadata.filter(metadata_type=message_id_metadata_type).exists():
                raise ValidationError(
                    message={
                        'message_id_metadata_type': _(
                            'Message ID metadata type "%(metadata_type)s" '
                            'is not valid for the document type: '
                            '%(document_type)s'
                        ) % {
                            'metadata_type': subject_metadata_type,
                            'document_type': document_type
                        }
                    }
                )

    def get_callback_kwargs(self):
        callback_kwargs = super().get_callback_kwargs()
        callback_kwargs.update(
            {'document_metadata': self.document_metadata}
        )

        return callback_kwargs

    def get_from_metadata_type(self):
        pk = self.kwargs.get('from_metadata_type_id')

        if pk:
            return MetadataType.objects.get(pk=pk)

    def get_subject_metadata_type(self):
        pk = self.kwargs.get('subject_metadata_type_id')

        if pk:
            return MetadataType.objects.get(pk=pk)

    def get_message_id_metadata_type(self):
        pk = self.kwargs.get('message_id_metadata_type_id')

        if pk:
            return MetadataType.objects.get(pk=pk)
