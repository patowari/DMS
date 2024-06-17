from django.apps import apps

from .settings import setting_auto_process


def handler_initialize_new_document_type_file_metadata_driver_configuration(
    sender, instance, **kwargs
):
    DocumentTypeDriverConfiguration = apps.get_model(
        app_label='file_metadata', model_name='DocumentTypeDriverConfiguration'
    )
    StoredDriver = apps.get_model(
        app_label='file_metadata', model_name='StoredDriver'
    )

    if kwargs['created']:
        for stored_driver in StoredDriver.objects.all():
            DocumentTypeDriverConfiguration.objects.create(
                document_type=instance, enabled=setting_auto_process.value,
                stored_driver=stored_driver
            )


def handler_post_document_file_upload(sender, instance, **kwargs):
    instance.submit_for_file_metadata_processing()
