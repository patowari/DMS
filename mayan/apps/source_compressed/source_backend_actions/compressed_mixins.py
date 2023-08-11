import logging

from django.apps import apps
from django.core.files import File

from mayan.apps.storage.compressed_files import Archive
from mayan.apps.storage.exceptions import NoMIMETypeMatch
from mayan.apps.storage.tasks import task_shared_upload_delete
from mayan.apps.sources.source_backend_actions.interfaces import (
    SourceBackendActionInterface, SourceBackendActionInterfaceRequestRESTAPI,
    SourceBackendActionInterfaceRequestView,
    SourceBackendActionInterfaceRequestViewForm,
    SourceBackendActionInterfaceTask
)

from .arguments import argument_expand
from .literals import (
    SOURCE_UNCOMPRESS_CHOICE_ALWAYS, SOURCE_UNCOMPRESS_CHOICE_ASK
)

logger = logging.getLogger(name=__name__)


class SourceBackendActionMixinCompressedBase:
    def _background_task(self, expand, **kwargs):
        result = super()._background_task(**kwargs)

        if result.get('immediate_mode', False):
            expand = False

        SharedUploadedFile = apps.get_model(
            app_label='storage', model_name='SharedUploadedFile'
        )

        original_shared_uploaded_file_id_list = result.pop(
            'shared_uploaded_file_id_list'
        )

        extracted_shared_uploaded_file_id_list = []

        if expand:
            for original_shared_uploaded_file_id in original_shared_uploaded_file_id_list:
                original_shared_uploaded_file = SharedUploadedFile.objects.get(
                    pk=original_shared_uploaded_file_id
                )

                try:
                    with original_shared_uploaded_file.open(mode='rb') as shared_uploaded_file_object:
                        compressed_file = Archive.open(file_object=shared_uploaded_file_object)
                        for compressed_file_member in compressed_file.members():
                            with compressed_file.open_member(filename=compressed_file_member) as compressed_file_member_file_object:
                                shared_uploaded_file = SharedUploadedFile.objects.create(
                                    file=File(compressed_file_member_file_object)
                                )
                                extracted_shared_uploaded_file_id_list.append(
                                    shared_uploaded_file.pk
                                )
                except NoMIMETypeMatch:
                    logger.debug(msg='Not expanding; Exception: NoMIMETypeMatch')
                    extracted_shared_uploaded_file_id_list.append(
                        original_shared_uploaded_file_id
                    )
                except Exception:
                    # Cleanup on fatal errors.
                    for original_shared_uploaded_file_id in original_shared_uploaded_file_id_list:
                        task_shared_upload_delete.apply_async(
                            kwargs={
                                'shared_uploaded_file_id': original_shared_uploaded_file_id
                            }
                        )

                    for extracted_shared_uploaded_file_id in extracted_shared_uploaded_file_id_list:
                        task_shared_upload_delete.apply_async(
                            kwargs={
                                'shared_uploaded_file_id': extracted_shared_uploaded_file_id
                            }
                        )

                    raise
                else:
                    task_shared_upload_delete.apply_async(
                        kwargs={
                            'shared_uploaded_file_id': original_shared_uploaded_file.pk
                        }
                    )
        else:
            extracted_shared_uploaded_file_id_list = original_shared_uploaded_file_id_list

        result['shared_uploaded_file_id_list'] = extracted_shared_uploaded_file_id_list

        return result

    def get_task_kwargs(self, expand, **kwargs):
        result = super().get_task_kwargs(**kwargs)

        result['action_interface_kwargs'].update(
            {'expand': expand}
        )

        return result


class SourceBackendActionMixinCompressedNonInteractive(
    SourceBackendActionMixinCompressedBase
):
    class Interface:
        class Model(SourceBackendActionInterface):
            def process_interface_context(self):
                super().process_interface_context()

                source_backend = self.action.source.get_backend_instance()

                self.action_kwargs['expand'] = source_backend.kwargs.get('uncompress') == SOURCE_UNCOMPRESS_CHOICE_ALWAYS

        class RESTAPI(SourceBackendActionInterfaceRequestRESTAPI):
            def process_interface_context(self):
                super().process_interface_context()

                source_backend = self.action.source.get_backend_instance()

                self.action_kwargs['expand'] = source_backend.kwargs.get('uncompress') == SOURCE_UNCOMPRESS_CHOICE_ALWAYS

        class Task(SourceBackendActionInterfaceTask):
            def process_interface_context(self):
                super().process_interface_context()

                source_backend = self.action.source.get_backend_instance()

                self.action_kwargs['expand'] = source_backend.kwargs.get('uncompress') == SOURCE_UNCOMPRESS_CHOICE_ALWAYS

        class View(SourceBackendActionInterfaceRequestView):
            def process_interface_context(self):
                super().process_interface_context()

                source_backend = self.action.source.get_backend_instance()

                self.action_kwargs['expand'] = source_backend.kwargs.get('uncompress') == SOURCE_UNCOMPRESS_CHOICE_ALWAYS


class SourceBackendActionMixinCompressedInteractive(
    SourceBackendActionMixinCompressedBase
):
    class Interface:
        class Model(SourceBackendActionInterface):
            class Argument:
                expand = argument_expand

            def process_interface_context(self):
                super().process_interface_context()

                source_backend = self.action.source.get_backend_instance()

                if source_backend.kwargs['uncompress'] == SOURCE_UNCOMPRESS_CHOICE_ASK:
                    expand = self.context['expand']
                else:
                    if source_backend.kwargs['uncompress'] == SOURCE_UNCOMPRESS_CHOICE_ALWAYS:
                        expand = True
                    else:
                        expand = False

                self.action_kwargs['expand'] = expand

        class RESTAPI(SourceBackendActionInterfaceRequestRESTAPI):
            class Argument:
                expand = argument_expand

            def process_interface_context(self):
                super().process_interface_context()

                source_backend = self.action.source.get_backend_instance()

                if source_backend.kwargs['uncompress'] == SOURCE_UNCOMPRESS_CHOICE_ASK:
                    expand = self.context['expand']
                else:
                    if source_backend.kwargs['uncompress'] == SOURCE_UNCOMPRESS_CHOICE_ALWAYS:
                        expand = True
                    else:
                        expand = False

                self.action_kwargs['expand'] = expand

        class Task(SourceBackendActionInterfaceTask):
            class Argument:
                expand = argument_expand

            def process_interface_context(self):
                super().process_interface_context()

                self.action_kwargs['expand'] = self.context['expand']

        class View(SourceBackendActionInterfaceRequestViewForm):
            class Argument:
                expand = argument_expand

            def process_interface_context(self):
                super().process_interface_context()

                source_backend = self.action.source.get_backend_instance()

                if source_backend.kwargs['uncompress'] == SOURCE_UNCOMPRESS_CHOICE_ASK:
                    expand = self.context['forms']['source_form'].cleaned_data.get('expand')
                else:
                    if source_backend.kwargs['uncompress'] == SOURCE_UNCOMPRESS_CHOICE_ALWAYS:
                        expand = True
                    else:
                        expand = False

                self.action_kwargs['expand'] = expand
