from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.generics import get_object_or_404 as rest_get_object_or_404
from rest_framework.response import Response

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.permissions import permission_document_file_new
from mayan.apps.documents.serializers.document_serializers import DocumentSerializer
from mayan.apps.documents.tasks import (
    task_document_file_create, task_document_upload
)

from ..interfaces import (
    SourceBackendActionInterface, SourceBackendActionInterfaceRequestRESTAPI,
    SourceBackendActionInterfaceRequestViewForm,
    SourceBackendActionInterfaceTask
)

from .arguments import (
    argument_document, argument_document_id, argument_document_id_optional
)
from .document_description_mixins import SourceBackendActionMixinDocumentDescriptionInteractive
from .document_label_mixins import SourceBackendActionMixinLabelInteractive
from .document_language_mixins import SourceBackendActionMixinLanguageInteractive
from .literals import DEFAULT_IMMEDIATE_MODE
from .user_mixins import SourceBackendActionMixinUserInteractive


class SourceBackendActionMixinDocumentInteractive:
    class Interface:
        class Model(SourceBackendActionInterface):
            class Argument:
                document = argument_document

            def process_interface_context(self):
                super().process_interface_context()

                self.action_kwargs['document'] = self.context['document']

        class RESTAPI(SourceBackendActionInterfaceRequestRESTAPI):
            class Argument:
                document_id = argument_document_id

            def process_interface_context(self):
                super().process_interface_context()

                queryset = AccessControlList.objects.restrict_queryset(
                    queryset=Document.valid.all(),
                    permission=permission_document_file_new,
                    user=self.context['request'].user
                )

                self.action_kwargs['document'] = rest_get_object_or_404(
                    queryset=queryset, pk=self.context['document_id']
                )

        class Task(SourceBackendActionInterfaceTask):
            class Argument:
                document_id = argument_document_id

            def process_interface_context(self):
                super().process_interface_context()

                self.action_kwargs['document'] = Document.valid.get(
                    pk=self.context['document_id']
                )

        class View(SourceBackendActionInterfaceRequestViewForm):
            class Argument:
                document = argument_document

            def process_interface_context(self):
                super().process_interface_context()

                queryset = AccessControlList.objects.restrict_queryset(
                    queryset=Document.valid.all(),
                    permission=permission_document_file_new,
                    user=self.context['request'].user
                )

                self.action_kwargs['document'] = get_object_or_404(
                    klass=queryset, pk=self.context['document'].pk
                )

    def _background_task(self, document, **kwargs):
        result = super()._background_task(**kwargs)

        result['document'] = document

        return result

    def get_task_kwargs(self, document, **kwargs):
        result = super().get_task_kwargs(**kwargs)

        result['action_interface_kwargs']['document_id'] = document.pk

        return result


class SourceBackendActionMixinDocumentOptionalTaskOnly:
    class Interface:
        class Task(SourceBackendActionInterfaceTask):
            class Argument:
                document_id = argument_document_id_optional

            def process_interface_context(self):
                super().process_interface_context()

                document_id = self.context['document_id']

                if document_id:
                    self.action_kwargs['document'] = Document.valid.get(
                        pk=document_id
                    )

    def _background_task(self, document=None, **kwargs):
        result = super()._background_task(**kwargs)

        result['document'] = document

        return result

    def get_task_kwargs(self, document=None, **kwargs):
        result = super().get_task_kwargs(**kwargs)

        if document:
            result['action_interface_kwargs']['document_id'] = document.pk

        return result


class SourceBackendActionMixinDocumentUploadBase(SourceBackendActionMixinDocumentOptionalTaskOnly):
    class Interface:
        class RESTAPI(SourceBackendActionInterfaceRequestRESTAPI):
            def process_action_data(self):
                super().process_action_data()

                immediate_mode = self.action_kwargs.get(
                    'immediate_mode', DEFAULT_IMMEDIATE_MODE
                )

                if immediate_mode:
                    request = self.context['view'].request

                    serializer = DocumentSerializer(
                        context={'request': request},
                        instance=self.action_data
                    )

                    self.interface_result = Response(
                        data=serializer.data, status=status.HTTP_201_CREATED
                    )

    def _background_task(self, **kwargs):
        result = super()._background_task(**kwargs)

        immediate_mode = result.get('immediate_mode', DEFAULT_IMMEDIATE_MODE)

        if immediate_mode:
            document = result['document']

            document_task_kwargs = self.get_document_file_task_kwargs(**kwargs)
            document_task_kwargs.update(
                {
                    'document_id': document.pk,
                    'is_document_upload_sequence': True
                }
            )

            document_task_kwargs['shared_uploaded_file_id'] = result['shared_uploaded_file_id_list'][0]

            task_document_file_create.apply_async(
                kwargs=document_task_kwargs
            )
        else:
            document_type = result['document_type']

            base_document_task_kwargs = self.get_document_task_kwargs(**kwargs)
            base_document_task_kwargs.update(
                {
                    'document_type_id': document_type.pk
                }
            )

            for shared_uploaded_file_id in result['shared_uploaded_file_id_list']:
                document_task_kwargs = base_document_task_kwargs.copy()

                document_task_kwargs['shared_uploaded_file_id'] = shared_uploaded_file_id

                task_document_upload.apply_async(
                    kwargs=document_task_kwargs
                )

    def _execute(self, immediate_mode=DEFAULT_IMMEDIATE_MODE, **kwargs):
        if immediate_mode:
            document = kwargs['document_type'].documents_create(
                description=kwargs['description'], label=kwargs['label'],
                language=kwargs['language'], user=kwargs['user']
            )

            kwargs['document'] = document

            super()._execute(immediate_mode=immediate_mode, **kwargs)
            return document
        else:
            return super()._execute(**kwargs)


class SourceBackendActionMixinDocumentUploadInteractive(
    SourceBackendActionMixinDocumentDescriptionInteractive,
    SourceBackendActionMixinLabelInteractive,
    SourceBackendActionMixinLanguageInteractive,
    SourceBackendActionMixinUserInteractive,
    SourceBackendActionMixinDocumentUploadBase
):
    """
    Mixin for a complete action that uploads documents.
    """
