import json
import logging
import re

import yaml

from django import forms
from django.apps import apps
from django.core.exceptions import ValidationError
from django.utils.encoding import force_text
from django.utils.module_loading import import_string
from django.utils.translation import ugettext, ugettext_lazy as _

from mayan.apps.common.serialization import yaml_load
from mayan.apps.documents.models.document_type_models import DocumentType

from ..classes import DocumentCreateWizardStep

from .literals import (
    DEFAULT_PERIOD_INTERVAL, DEFAULT_STORAGE_BACKEND,
    DEFAULT_STORAGE_BACKEND_ARGUMENTS, REGULAR_EXPRESSION_MATCH_EVERYTHING,
    REGULAR_EXPRESSION_MATCH_NOTHING, SOURCE_UNCOMPRESS_CHOICE_ALWAYS,
    SOURCE_UNCOMPRESS_CHOICE_ASK, SOURCE_UNCOMPRESS_INTERACTIVE_CHOICES,
    SOURCE_UNCOMPRESS_INTERVAL_CHOICES
)

logger = logging.getLogger(name=__name__)


class SourceBackendCompressedMixin:
    uncompress_choices = SOURCE_UNCOMPRESS_INTERACTIVE_CHOICES

    @classmethod
    def get_setup_form_field_widgets(cls):
        widgets = super().get_setup_form_field_widgets()

        widgets.update(
            {
                'uncompress': {
                    'class': 'django.forms.widgets.Select', 'kwargs': {
                        'attrs': {'class': 'select2'}
                    }
                }
            }
        )
        return widgets

    @classmethod
    def get_setup_form_fields(cls):
        fields = super().get_setup_form_fields()
        fields.update(
            {
                'uncompress': {
                    'label': _('Uncompress'),
                    'class': 'django.forms.ChoiceField',
                    'default': SOURCE_UNCOMPRESS_CHOICE_ASK,
                    'help_text': _(
                        'Whether to expand or not compressed archives.'
                    ),
                    'kwargs': {
                        'choices': cls.uncompress_choices
                    },
                    'required': True
                }
            }
        )

        return fields

    @classmethod
    def get_setup_form_fieldsets(cls):
        fieldsets = super().get_setup_form_fieldsets()

        fieldsets += (
            (
                _('Decompression'), {
                    'fields': ('uncompress')
                },
            ),
        )

        return fieldsets

    @classmethod
    def get_upload_form_class(cls):
        class CompressedSourceUploadForm(
            super().get_upload_form_class()
        ):
            expand = forms.BooleanField(
                label=_('Expand compressed files'), required=False,
                help_text=ugettext(
                    'Upload a compressed file\'s contained files as '
                    'individual documents.'
                )
            )

            def __init__(self, *args, **kwargs):
                self.field_order = ['expand']
                super().__init__(*args, **kwargs)

        return CompressedSourceUploadForm

    def get_expand(self):
        if self.kwargs['uncompress'] == SOURCE_UNCOMPRESS_CHOICE_ASK:
            return self.process_kwargs['forms']['source_form'].cleaned_data.get('expand')
        else:
            if self.kwargs['uncompress'] == SOURCE_UNCOMPRESS_CHOICE_ALWAYS:
                return True
            else:
                return False

    def get_task_extra_kwargs(self):
        results = super().get_task_extra_kwargs()

        results.update(
            {
                'expand': self.get_expand()
            }
        )

        return results


class SourceBackendInteractiveMixin:
    is_interactive = True

    def callback(
        self, document_file, source_id, user_id, query_string=None,
        extra_data=None, **kwargs
    ):
        super().callback(
            document_file=document_file, extra_data=extra_data,
            query_string=query_string, source_id=source_id, user_id=user_id,
            **kwargs
        )

        DocumentCreateWizardStep.post_upload_process(
            document=document_file.document,
            extra_data=extra_data,
            query_string=query_string,
            source_id=source_id,
            user_id=user_id
        )

    def get_callback_kwargs(self):
        callback_kwargs = super().get_callback_kwargs()

        query_string = ''

        query_dict = self.process_kwargs['request'].GET.copy()
        query_dict.update(self.process_kwargs['request'].POST)

        # Convert into a string. Make sure it is a QueryDict object from a
        # request and not just a simple dictionary.
        if hasattr(query_dict, 'urlencode'):
            query_string = query_dict.urlencode()

        callback_kwargs.update(
            {
                'query_string': query_string
            }
        )

        return callback_kwargs

    def get_document(self):
        return self.process_kwargs['document']

    def get_document_description(self):
        return self.process_kwargs['forms']['document_form'].cleaned_data.get('description')

    def get_document_file_action(self):
        return int(
            self.process_kwargs['forms']['document_form'].cleaned_data.get('action')
        )

    def get_document_file_comment(self):
        return self.process_kwargs['forms']['document_form'].cleaned_data.get('comment')

    def get_document_label(self):
        return self.process_kwargs['forms']['document_form'].get_final_label(
            filename=force_text(self.shared_uploaded_file)
        )

    def get_document_language(self):
        return self.process_kwargs['forms']['document_form'].cleaned_data.get('language')

    def get_document_type(self):
        return self.process_kwargs['document_type']

    def get_user(self):
        if not self.process_kwargs['request'].user.is_anonymous:
            return self.process_kwargs['request'].user
        else:
            return None


class SourceBackendPeriodicMixin:
    @classmethod
    def get_setup_form_fields(cls):
        fields = super().get_setup_form_fields()
        fields.update(
            {
                'document_type_id': {
                    'class': 'django.forms.ChoiceField',
                    'default': '',
                    'help_text': _(
                        'Assign a document type to documents uploaded from this '
                        'source.'
                    ),
                    'kwargs': {
                        'choices': [
                            (document_type.id, document_type) for document_type in DocumentType.objects.all()
                        ],
                    },
                    'label': _('Document type'),
                    'required': True
                },
                'interval': {
                    'class': 'django.forms.IntegerField',
                    'default': DEFAULT_PERIOD_INTERVAL,
                    'help_text': _(
                        'Interval in seconds between checks for new '
                        'documents.'
                    ),
                    'kwargs': {
                        'min_value': 0
                    },
                    'label': _('Interval'),
                    'required': True
                }
            }
        )

        return fields

    @classmethod
    def get_setup_form_fieldsets(cls):
        fieldsets = super().get_setup_form_fieldsets()

        fieldsets += (
            (
                _('Unattended'), {
                    'fields': ('document_type_id', 'interval')
                },
            ),
        )

        return fieldsets

    @classmethod
    def get_setup_form_widgets(cls):
        widgets = super().get_setup_form_widgets()

        widgets.update(
            {
                'document_type_id': {
                    'class': 'django.forms.widgets.Select', 'kwargs': {
                        'attrs': {'class': 'select2'}
                    }
                }
            }
        )

        return widgets

    def create(self):
        IntervalSchedule = apps.get_model(
            app_label='django_celery_beat', model_name='IntervalSchedule'
        )
        PeriodicTask = apps.get_model(
            app_label='django_celery_beat', model_name='PeriodicTask'
        )

        # Create a new interval or use an existing one.
        interval_instance, created = IntervalSchedule.objects.get_or_create(
            every=self.kwargs['interval'], period='seconds'
        )

        PeriodicTask.objects.create(
            interval=interval_instance,
            kwargs=json.dumps(
                obj={'source_id': self.model_instance_id}
            ),
            name=self.get_periodic_task_name(),
            task='mayan.apps.source_apps.sources.tasks.task_source_process_document'
        )

    def delete(self):
        self.delete_periodic_task(pk=self.model_instance_id)

    def get_document_type(self):
        return DocumentType.objects.get(
            pk=self.kwargs['document_type_id']
        )

    def delete_periodic_task(self, pk=None):
        PeriodicTask = apps.get_model(
            app_label='django_celery_beat', model_name='PeriodicTask'
        )

        try:
            periodic_task = PeriodicTask.objects.get(
                name=self.get_periodic_task_name(pk=pk)
            )

            interval_instance = periodic_task.interval

            if tuple(interval_instance.periodictask_set.values_list('id', flat=True)) == (periodic_task.pk,):
                # Only delete the interval if nobody else is using it.
                interval_instance.delete()
            else:
                periodic_task.delete()
        except PeriodicTask.DoesNotExist:
            logger.warning(
                'Tried to delete non existent periodic task "%s"',
                self.get_periodic_task_name(pk=pk)
            )

    def get_periodic_task_name(self, pk=None):
        return 'check_interval_source-{}'.format(
            pk or self.model_instance_id
        )

    def save(self):
        self.delete_periodic_task()
        self.create()


class SourceBackendCompressedPeriodicMixin(
    SourceBackendCompressedMixin, SourceBackendPeriodicMixin
):
    uncompress_choices = SOURCE_UNCOMPRESS_INTERVAL_CHOICES


class SourceBackendRegularExpressionMixin:
    @classmethod
    def get_setup_form_fields(cls):
        fields = super().get_setup_form_fields()

        fields.update(
            {
                'include_regex': {
                    'class': 'django.forms.CharField',
                    'default': '',
                    'help_text': _(
                        'Regular expression used to select which files '
                        'to upload.'
                    ),
                    'label': _('Include regular expression'),
                    'required': False
                },
                'exclude_regex': {
                    'class': 'django.forms.CharField',
                    'default': '',
                    'help_text': _(
                        'Regular expression used to exclude which files '
                        'to upload.'
                    ),
                    'label': _('Exclude regular expression'),
                    'required': False
                }
            }
        )

        return fields

    @classmethod
    def get_setup_form_fieldsets(cls):
        fieldsets = super().get_setup_form_fieldsets()

        fieldsets += (
            (
                _('Content selection'), {
                    'fields': ('include_regex', 'exclude_regex')
                },
            ),
        )

        return fieldsets

    def get_regex_exclude(self):
        return re.compile(
            pattern=self.kwargs.get(
                'exclude_regex', REGULAR_EXPRESSION_MATCH_NOTHING
            ) or REGULAR_EXPRESSION_MATCH_NOTHING
        )

    def get_regex_include(self):
        return re.compile(
            pattern=self.kwargs.get(
                'include_regex', REGULAR_EXPRESSION_MATCH_EVERYTHING
            )
        )


class SourceBackendStorageBackendMixin:
    @classmethod
    def get_setup_form_fields(cls):
        fields = super().get_setup_form_fields()

        fields.update(
            {
                'storage_backend': {
                    'class': 'django.forms.CharField',
                    'default': DEFAULT_STORAGE_BACKEND,
                    'help_text': _(
                        'Python path to the Storage subclass used to '
                        'access the source files.'
                    ),
                    'kwargs': {
                        'max_length': 255,
                    },
                    'label': _('Storage backend'),
                    'required': True
                },
                'storage_backend_arguments': {
                    'class': 'django.forms.CharField',
                    'default': DEFAULT_STORAGE_BACKEND_ARGUMENTS,
                    'help_text': _(
                        'Arguments to pass to the storage backend. Use '
                        'YAML format.'
                    ),
                    'kwargs': {
                        'max_length': 255,
                    },
                    'label': _('Storage backend arguments'),
                    'required': True
                }
            }
        )

        return fields

    @classmethod
    def get_setup_form_fieldsets(cls):
        fieldsets = super().get_setup_form_fieldsets()

        fieldsets += (
            (
                _('Storage'), {
                    'fields': (
                        'storage_backend', 'storage_backend_arguments'
                    )
                },
            ),
        )

        return fieldsets

    def get_storage_backend_arguments(self):
        arguments = self.kwargs.get('storage_backend_arguments', '{}')

        try:
            return yaml_load(stream=arguments)
        except yaml.YAMLError:
            raise ValidationError(
                _(
                    'Unable to initialize storage. Check the storage '
                    'backend arguments.'
                )
            )

    def get_storage_backend_class(self):
        try:
            return import_string(
                dotted_path=self.kwargs.get('storage_backend')
            )
        except Exception as exception:
            message = _(
                'Unable to initialize storage. Check the storage '
                'backend dotted path.'
            )
            raise ValueError(message) from exception

    def get_storage_backend_instance(self):
        storage_backend_arguments = self.get_storage_backend_arguments()
        storage_backend_class = self.get_storage_backend_class()

        try:
            return storage_backend_class(**storage_backend_arguments)
        except Exception as exception:
            message = _(
                'Unable to initialize storage; %s'
            ) % exception

            logger.fatal(message)
            raise TypeError(message) from exception
