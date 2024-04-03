import json

from django.db import models

from .literals import DOCUMENT_FILE_SOURCE_METADATA_BATCH_SIZE


class DocumentFileSourceMetadataManager(models.Manager):
    def create_bulk(self):
        batch = []
        count = 0

        try:
            while True:
                kwargs = (yield)
                model_instance = self.model(**kwargs)
                batch.append(model_instance)
                count += 1

                if count >= DOCUMENT_FILE_SOURCE_METADATA_BATCH_SIZE:
                    count = 0

                    self.bulk_create(
                        batch_size=DOCUMENT_FILE_SOURCE_METADATA_BATCH_SIZE,
                        objs=batch
                    )
                    batch = []

        except GeneratorExit:
            self.bulk_create(
                batch_size=DOCUMENT_FILE_SOURCE_METADATA_BATCH_SIZE,
                objs=batch
            )


class SourceManager(models.Manager):
    def create_backend(self, label, backend_path, backend_data=None):
        self.create(
            backend_path=backend_path, backend_data=json.dumps(
                obj=backend_data or {}
            ), label=label
        )
