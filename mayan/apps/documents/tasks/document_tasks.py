import logging
from pathlib import Path

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import OperationalError
from django.utils.module_loading import import_string

from mayan.celery import app

from .document_file_tasks import task_document_file_create

logger = logging.getLogger(name=__name__)


@app.task(bind=True, ignore_results=True, retry_backoff=True)
def task_document_upload(
    self, document_type_id, shared_uploaded_file_id,
    callback_post_document_file_upload_dotted_path=None,
    callback_post_document_file_upload_function_name=None,
    callback_post_document_file_upload_kwargs=None,
    callback_post_document_create_dotted_path=None,
    callback_post_document_create_function_name=None,
    callback_post_document_create_kwargs=None,
    description=None, label=None, language=None, user_id=None
):
    DocumentType = apps.get_model(
        app_label='documents', model_name='DocumentType'
    )
    SharedUploadedFile = apps.get_model(
        app_label='storage', model_name='SharedUploadedFile'
    )
    User = get_user_model()

    try:
        document_type = DocumentType.objects.get(pk=document_type_id)
        shared_uploaded_file = SharedUploadedFile.objects.get(
            pk=shared_uploaded_file_id
        )
        if user_id:
            user = User.objects.get(pk=user_id)
        else:
            user = None
    except OperationalError as exception:
        raise self.retry(exc=exception)

    description = description or ''

    label = label or Path(
        str(shared_uploaded_file)
    ).name

    try:
        document = document_type.documents_create(
            description=description, label=label, language=language,
            user=user
        )
    except OperationalError as exception:
        logger.error(
            'Operational error creating new document of type: %s, '
            'label: %s; %s. Retrying.', document_type, label, exception
        )
        raise self.retry(exc=exception)
    except Exception as exception:
        logger.critical(
            'Unexpected exception while creating new document of type: %s, '
            'label: %s; %s', document_type, label, exception
        )
        raise
    else:
        if callback_post_document_create_dotted_path:
            callback = import_string(dotted_path=callback_post_document_create_dotted_path)
            callback_kwargs = callback_post_document_create_kwargs or {}
            function = getattr(callback, callback_post_document_create_function_name)
            function(document=document, **callback_kwargs)

        task_document_file_create.apply_async(
            kwargs={
                'callback_dotted_path': callback_post_document_file_upload_dotted_path,
                'callback_function_name': callback_post_document_file_upload_function_name,
                'callback_kwargs': callback_post_document_file_upload_kwargs,
                'document_id': document.pk,
                'filename': label,
                'is_document_upload_sequence': True,
                'shared_uploaded_file_id': shared_uploaded_file_id,
                'user_id': user_id
            }
        )
