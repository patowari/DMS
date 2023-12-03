from django.utils.translation import gettext_lazy as _

from mayan.apps.credentials.models import StoredCredential
from mayan.apps.credentials.permissions import permission_credential_use

from .classes import MailerBackendBaseEmail


class DjangoSMTP(MailerBackendBaseEmail):
    """
    Backend that wraps Django's SMTP backend
    """
    class_path = 'django.core.mail.backends.smtp.EmailBackend'
    label = _(message='Django SMTP backend')

    @classmethod
    def get_form_fields(cls):
        fields = super().get_form_fields()

        fields.update(
            {
                'host': {
                    'label': _(message='Host'),
                    'class': 'django.forms.CharField',
                    'default': 'localhost',
                    'help_text': _(
                        message='The host to use for sending email.'
                    ),
                    'kwargs': {
                        'max_length': 48
                    }, 'required': True
                }, 'port': {
                    'label': _(message='Port'),
                    'class': 'django.forms.IntegerField', 'default': 25,
                    'help_text': _(
                        message='Port to use for the SMTP server.'
                    ),
                    'required': True
                }, 'use_tls': {
                    'label': _(message='Use TLS'),
                    'class': 'django.forms.BooleanField', 'default': False,
                    'help_text': _(
                        message='Whether to use a TLS (secure) '
                        'connection when talking to the SMTP server. This '
                        'is used for explicit TLS connections, generally '
                        'on port 587.'
                    ), 'required': False
                }, 'use_ssl': {
                    'label': _(message='Use SSL'),
                    'class': 'django.forms.BooleanField', 'default': False,
                    'help_text': _(
                        message='Whether to use an implicit TLS (secure) '
                        'connection when talking to the SMTP server. In '
                        'most email documentation this type of TLS '
                        'connection is referred to as SSL. It is generally '
                        'used on port 465. If you are experiencing '
                        'problems, see the explicit TLS setting '
                        '"Use TLS". Note that "Use TLS" and "Use SSL" '
                        'are mutually exclusive, so only set one of those '
                        'settings to True.'
                    ), 'required': False
                }, 'stored_credential_id': {
                    'class': 'mayan.apps.views.fields.FormFieldFilteredModelChoice',
                    'help_text': _(
                        message='The credential entry to use to '
                        'authenticate against the email server.'
                    ),
                    'kwargs': {
                        'source_model': StoredCredential,
                        'permission': permission_credential_use
                    },
                    'label': _(message='Credential'),
                    'required': True
                }
            }
        )

        return fields

    @classmethod
    def get_form_fieldsets(cls):
        fieldsets = super().get_form_fieldsets()

        fieldsets += (
            (
                _(message='Server'), {
                    'fields': ('host', 'port', 'use_tls', 'use_ssl')
                }
            ), (
                _(message='Authentication'), {
                    'fields': ('stored_credential_id',)
                }
            )
        )

        return fieldsets


class DjangoFileBased(MailerBackendBaseEmail):
    """
    Mailing backend that wraps Django's file based email backend
    """
    class_path = 'django.core.mail.backends.filebased.EmailBackend'
    label = _(message='Django file based backend')

    @classmethod
    def get_form_fields(cls):
        fields = super().get_form_fields()
        fields.update(
            {
                'file_path': {
                    'label': _(message='File path'),
                    'class': 'django.forms.CharField', 'kwargs': {
                        'max_length': 48
                    }
                }
            }
        )

        return fields

    @classmethod
    def get_form_fieldsets(cls):
        fieldsets = super().get_form_fieldsets()

        fieldsets += (
            (
                _(message='Storage'), {
                    'fields': ('file_path',)
                }
            ),
        )

        return fieldsets
