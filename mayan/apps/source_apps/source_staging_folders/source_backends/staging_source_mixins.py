import logging

from django.conf import settings
from django.contrib import messages
from django.core.files import File
from django.http import Http404, StreamingHttpResponse
from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.generics import get_object_or_404 as rest_get_object_or_404
from rest_framework.response import Response
from rest_framework.reverse import reverse as rest_framework_reverse

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.menus import menu_object
from mayan.apps.converter.classes import ConverterBase
from mayan.apps.converter.utils import IndexedDictionary
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.models.document_type_models import DocumentType
from mayan.apps.documents.permissions import permission_document_create
from mayan.apps.documents.serializers.document_serializers import DocumentSerializer
from mayan.apps.documents.tasks import task_document_file_upload
from mayan.apps.navigation.classes import SourceColumn
from mayan.apps.storage.classes import DefinedStorage
from mayan.apps.storage.models import SharedUploadedFile

from mayan.apps.source_apps.sources.classes import SourceBackendAction
from mayan.apps.source_apps.sources.literals import STORAGE_NAME_SOURCE_CACHE_FOLDER
from mayan.apps.source_apps.sources.tasks import task_process_document_upload

from ..column_widgets import StagingSourceFileThumbnailWidget
from ..forms import StagingUploadForm
from ..links import (
    link_staging_source_file_delete, link_staging_source_file_select
)
from ..views import SourceBackendStagingSourceFileListView

from .staging_source_files import StagingSourceFile

logger = logging.getLogger(name=__name__)


class SourceBackendMixinFileList:
    actions = (
        SourceBackendAction(
            name='file_delete', arguments=('encoded_filename',)
        ),
        SourceBackendAction(
            name='file_image', arguments=('encoded_filename',),
            confirmation=False
        ),
        SourceBackendAction(name='file_list', confirmation=False),
        SourceBackendAction(
            name='file_upload', arguments=(
                'document_type_id', 'encoded_filename', 'expand',
                'multiple_document_mode'
            )
        )
    )
    staging_source_file_class = StagingSourceFile
    upload_form_class = StagingUploadForm

    @classmethod
    def get_setup_form_fields(cls):
        fields = super().get_setup_form_fields()

        fields.update(
            {
                'preview_width': {
                    'class': 'django.forms.IntegerField',
                    'help_text': _(
                        'Width value to be passed to the converter backend.'
                    ),
                    'kwargs': {
                        'min_value': 0
                    },
                    'label': _('Preview width'),
                    'required': True
                },
                'preview_height': {
                    'class': 'django.forms.IntegerField',
                    'help_text': _(
                        'Height value to be passed to the converter backend.'
                    ),
                    'kwargs': {
                        'min_value': 0
                    },
                    'label': _('Preview height'),
                    'required': False
                },
                'delete_after_upload': {
                    'class': 'django.forms.BooleanField',
                    'help_text': _(
                        'Delete the file after is has been successfully '
                        'uploaded.'
                    ),
                    'label': _('Delete after upload'),
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
                _('Staging files'), {
                    'fields': (
                        'preview_width', 'preview_height',
                        'delete_after_upload'
                    ),
                },
            ),
        )

        return fieldsets

    @classmethod
    def intialize(cls):
        super().intialize()

        SourceColumn(
            html_extra_classes='text-center', label=_('Thumbnail'),
            source=cls.staging_source_file_class,
            widget=StagingSourceFileThumbnailWidget
        )

        menu_object.bind_links(
            links=(
                link_staging_source_file_select,
                link_staging_source_file_delete
            ), sources=(cls.staging_source_file_class,)
        )

    def action_file_delete(self, request, encoded_filename):
        staging_source_file = self.get_file(
            encoded_filename=encoded_filename
        )
        staging_source_file.delete()

    def action_file_image(self, request, encoded_filename, **kwargs):
        encoded_filename = encoded_filename[0]

        query_dict = request.GET

        transformation_instance_list = IndexedDictionary(
            dictionary=query_dict
        ).as_instance_list()

        maximum_layer_order = request.GET.get('maximum_layer_order')
        if maximum_layer_order:
            maximum_layer_order = int(maximum_layer_order)

        staging_source_file = self.get_file(
            encoded_filename=encoded_filename
        )

        combined_transformation_list = staging_source_file.get_combined_transformation_list(
            maximum_layer_order=maximum_layer_order,
            transformation_instance_list=transformation_instance_list,
            user=request.user
        )

        cache_filename = staging_source_file.generate_image(
            transformation_instance_list=combined_transformation_list
        )

        storage_source_cache = DefinedStorage.get(
            name=STORAGE_NAME_SOURCE_CACHE_FOLDER
        ).get_storage_instance()

        def file_generator():
            with storage_source_cache.open(name=cache_filename) as file_object:
                converter = ConverterBase.get_converter_class()(
                    file_object=file_object
                )
                for transformation in combined_transformation_list or ():
                    converter.transform(transformation=transformation)

                result = converter.get_page()

                while True:
                    chunk = result.read(File.DEFAULT_CHUNK_SIZE)
                    if not chunk:
                        break
                    else:
                        yield chunk

        response = StreamingHttpResponse(
            content_type='image', streaming_content=file_generator()
        )
        return None, response

    def action_file_list(self, request):
        staging_source_files = []

        for staging_source_file in self.get_files():
            staging_source_files.append(
                {
                    'filename': staging_source_file.filename,
                    'delete-url': rest_framework_reverse(
                        viewname='rest_api:source-action', kwargs={
                            'action_name': 'file_delete',
                            'source_id': staging_source_file.staging_source.model_instance_id
                        }, request=request
                    ),
                    'encoded_filename': staging_source_file.encoded_filename,
                    'image-url': staging_source_file.get_api_image_url(
                        request=request
                    ),
                    'upload-url': rest_framework_reverse(
                        viewname='rest_api:source-action', kwargs={
                            'action_name': 'file_upload',
                            'source_id': staging_source_file.staging_source.model_instance_id
                        }, request=request
                    )
                }
            )

        return staging_source_files, None

    def action_file_upload(
        self, request, document_type_id, encoded_filename, expand=False,
        multiple_document_mode=True
    ):
        # Default multiple_document_mode to True.
        if multiple_document_mode is None:
            multiple_document_mode = True

        staging_source_file = self.get_file(
            encoded_filename=encoded_filename
        )

        queryset = AccessControlList.objects.restrict_queryset(
            queryset=DocumentType.objects.all(),
            permission=permission_document_create,
            user=request.user
        )

        document_type = rest_get_object_or_404(
            queryset=queryset, pk=document_type_id
        )

        self.process_kwargs = {
            'request': request,
            'staging_source_file_filename': staging_source_file.filename
        }

        shared_uploaded_file = SharedUploadedFile.objects.create(
            file=staging_source_file.as_file()
        )

        if multiple_document_mode:
            # Multiple document mode.
            kwargs = {
                'callback_kwargs': self.get_callback_kwargs(),
                'document_type_id': document_type.pk,
                'expand': expand,
                'shared_uploaded_file_id': shared_uploaded_file.pk,
                'source_id': self.model_instance_id,
                'user_id': request.user.pk
            }
            kwargs.update(
                self.get_task_extra_kwargs()
            )

            task_process_document_upload.apply_async(kwargs=kwargs)

            return None, Response(status=status.HTTP_202_ACCEPTED)
        else:
            # Single document mode.
            document = Document(
                document_type=document_type, label=str(staging_source_file)
            )
            document._event_actor = request.user
            document.save()

            task_document_file_upload.apply_async(
                kwargs={
                    'document_id': document.pk,
                    'shared_uploaded_file_id': shared_uploaded_file.pk,
                    'user_id': request.user.pk
                }
            )

            return (
                None, Response(
                    data=DocumentSerializer(
                        document, context={'request': request}
                    ).data, status=status.HTTP_200_OK
                )
            )

    def callback(self, **kwargs):
        super().callback(**kwargs)

        if self.kwargs.get('delete_after_upload', False):
            staging_source_file = self.get_file(
                filename=kwargs['extra_data']['staging_source_file_filename']
            )

            try:
                staging_source_file.delete()
            except Exception as exception:
                logger.error(
                    'Error deleting staging source file: %s; %s',
                    staging_source_file, exception
                )
                raise Exception(
                    _('Error deleting staging source file; %s') % exception
                )

    def get_action_file_delete_context(self, view, encoded_filename):
        staging_source_file = self.get_file(
            encoded_filename=encoded_filename
        )

        context = {
            'delete_view': True,
            'object': staging_source_file,
            'object_name': _('Staging file'),
            'title': _('Delete staging file "%s"?') % staging_source_file
        }

        view_kwargs = view.get_all_kwargs()

        if 'document_type_id' in view_kwargs:
            context['document_type'] = DocumentType.objects.get(
                pk=view_kwargs['document_type_id'][0]
            )

        return context

    def get_callback_kwargs(self):
        callback_kwargs = super().get_callback_kwargs()
        callback_kwargs.setdefault(
            'extra_data', {}
        )

        callback_kwargs['extra_data'].update(
            {
                'staging_source_file_filename': self.process_kwargs[
                    'staging_source_file_filename'
                ]
            }
        )

        return callback_kwargs

    def get_file(self, *args, **kwargs):
        try:
            return self.staging_source_file_class(
                staging_source=self, *args, **kwargs
            )
        except (KeyError, ValueError):
            raise Http404

    def get_shared_uploaded_files(self):
        staging_source_file = self.get_file(
            encoded_filename=self.process_kwargs['forms']['source_form'].cleaned_data['staging_source_file_id']
        )
        self.process_kwargs['staging_source_file_filename'] = staging_source_file.filename

        return (
            SharedUploadedFile.objects.create(
                file=staging_source_file.as_file()
            ),
        )

    def get_view_context(self, context, request):
        try:
            staging_files = list(
                self.get_files()
            )
        except Exception as exception:
            messages.error(
                message=_(
                    'Unable get list of staging files; %s'
                ) % exception, request=request
            )
            staging_files = ()
            if settings.DEBUG or settings.TESTING:
                raise

        # Instantiate a fake list view to populate the pagination data for
        # the staging source file list.
        view = SourceBackendStagingSourceFileListView()
        view.kwargs = self.kwargs
        view.object_list = staging_files
        view.request = request

        template_staging_file_list_context = {
            'hide_link': True,
            'no_results_icon': self.icon,
            'no_results_text': _(
                'This could mean that the staging source is empty. It '
                'could also mean that the operating system user account '
                'being used for Mayan EDMS doesn\'t have the necessary '
                'file system permissions to access the staging source '
                'files.'
            ),
            'no_results_title': _('No staging files available')
        }

        template_staging_file_list_context.update(
            view.get_context_data()
        )

        subtemplates_list = [
            {
                'context': {
                    'forms': context['forms']
                },
                'name': 'appearance/generic_multiform_subtemplate.html'
            },
            {
                'context': template_staging_file_list_context,
                'name': 'appearance/generic_list_subtemplate.html'
            }
        ]

        return {
            'subtemplates_list': subtemplates_list
        }
