from mayan.apps.common.utils import get_class_full_name
from mayan.apps.sources.models import Source


class SourceBackendActionMixinCallbackBase:
    def get_callback_kwargs(self, **kwargs):
        return {
            'source_id': self.source.pk
        }


class SourceBackendActionMixinCallbackPostDocumentUploadBase:
    def get_post_document_upload_kwargs_callback_kwargs(self, kwargs):
        return {}

    def get_document_task_kwargs(self, **kwargs):
        result = super().get_document_task_kwargs(**kwargs)

        callback_kwargs = self.get_callback_kwargs()
        callback_post_document_create_kwargs = self.get_post_document_upload_kwargs_callback_kwargs(kwargs=kwargs)
        callback_kwargs.update(**callback_post_document_create_kwargs)

        result['callback_post_document_create_dotted_path'] = get_class_full_name(klass=Source)
        result['callback_post_document_create_function_name'] = 'callback_post_document_create'
        result['callback_post_document_create_kwargs'] = callback_kwargs

        return result


class SourceBackendActionMixinCallbackPostDocumentFileUploadBase:
    def get_post_document_file_upload_kwargs_callback_kwargs(self, kwargs):
        return {}

    def get_document_task_kwargs(self, **kwargs):
        result = super().get_document_task_kwargs(**kwargs)

        callback_kwargs = self.get_callback_kwargs()
        callback_post_document_file_upload_kwargs = self.get_post_document_file_upload_kwargs_callback_kwargs(kwargs=kwargs)
        callback_kwargs.update(**callback_post_document_file_upload_kwargs)

        result['callback_post_document_file_upload_dotted_path'] = get_class_full_name(klass=Source)
        result['callback_post_document_file_upload_function_name'] = 'callback_post_document_file_upload'
        result['callback_post_document_file_upload_kwargs'] = callback_kwargs

        return result

    def get_document_file_task_kwargs(self, **kwargs):
        result = super().get_document_task_kwargs(**kwargs)

        callback_kwargs = self.get_callback_kwargs()
        callback_post_document_file_upload_kwargs = self.get_post_document_file_upload_kwargs_callback_kwargs(kwargs=kwargs)
        callback_kwargs.update(**callback_post_document_file_upload_kwargs)

        result['callback_dotted_path'] = get_class_full_name(klass=Source)
        result['callback_function_name'] = 'callback_post_document_file_upload'
        result['callback_kwargs'] = callback_kwargs

        return result


class SourceBackendActionMixinCallbackPostDocumentUpload(
    SourceBackendActionMixinCallbackPostDocumentUploadBase,
    SourceBackendActionMixinCallbackPostDocumentFileUploadBase,
    SourceBackendActionMixinCallbackBase
):
    pass


class SourceBackendActionMixinCallbackPostDocumentFileUpload(
    SourceBackendActionMixinCallbackPostDocumentFileUploadBase,
    SourceBackendActionMixinCallbackBase
):
    pass
