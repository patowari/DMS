from django.utils.translation import gettext_lazy as _

from mayan.apps.task_manager.classes import CeleryQueue
from mayan.apps.task_manager.workers import worker_b

queue_file_metadata = CeleryQueue(
    label=_(message='File metadata'), name='file_metadata', worker=worker_b
)

queue_file_metadata.add_task_type(
    label=_(message='Process document file'),
    dotted_path='mayan.apps.file_metadata.tasks.task_process_document_file'
)
