import logging

from django.apps import apps

from mayan.celery import app

logger = logging.getLogger(name=__name__)


@app.task(ignore_result=True)
def task_download_files_stale_delete():
    logger.debug(msg='Executing')

    DownloadFile = apps.get_model(
        app_label='storage', model_name='DownloadFile'
    )

    logger.debug('Start')

    DownloadFile.objects.stale_delete()

    logger.debug('Finished')


@app.task(ignore_result=True)
def task_shared_upload_stale_delete():
    logger.debug('Executing')

    SharedUploadedFile = apps.get_model(
        app_label='storage', model_name='SharedUploadedFile'
    )

    logger.debug('Start')

    SharedUploadedFile.objects.stale_delete()

    logger.debug('Finished')
