from django.db.models import Q

from ...models import DocumentTypeMetadataType


class DocumentTypeMetadataTypeAPIViewTestMixin:
    def _request_document_type_metadata_type_create_api_view(self):
        pk_list = list(
            DocumentTypeMetadataType.objects.values_list('pk', flat=True)
        )

        response = self.post(
            viewname='rest_api:documenttypemetadatatype-list',
            kwargs={'document_type_id': self._test_document_type.pk}, data={
                'metadata_type_id': self._test_metadata_type.pk,
                'required': False
            }
        )

        try:
            self._test_document_type_metadata_type = DocumentTypeMetadataType.objects.get(
                ~Q(pk__in=pk_list)
            )
        except DocumentTypeMetadataType.DoesNotExist:
            self._test_document_type_metadata_type = None

        return response

    def _request_document_type_metadata_type_delete_api_view(self):
        return self.delete(
            viewname='rest_api:documenttypemetadatatype-detail',
            kwargs={
                'document_type_id': self._test_document_type.pk,
                'metadata_type_id': self._test_document_type_metadata_type.pk
            }
        )

    def _request_document_type_metadata_type_list_api_view(self):
        return self.get(
            viewname='rest_api:documenttypemetadatatype-list', kwargs={
                'document_type_id': self._test_document_type.pk
            }
        )

    def _request_document_type_metadata_type_edit_api_view_via_patch(self):
        return self.patch(
            viewname='rest_api:documenttypemetadatatype-detail',
            kwargs={
                'document_type_id': self._test_document_type.pk,
                'metadata_type_id': self._test_document_type_metadata_type.pk
            }, data={
                'required': True
            }
        )

    def _request_document_type_metadata_type_edit_api_view_via_put(self):
        return self.put(
            viewname='rest_api:documenttypemetadatatype-detail',
            kwargs={
                'document_type_id': self._test_document_type.pk,
                'metadata_type_id': self._test_document_type_metadata_type.pk
            }, data={
                'required': True
            }
        )


class DocumentTypeMetadataTypeTestMixin:
    def _create_test_document_type_metadata_type(self):
        self._test_document_type_metadata_type = self._test_document_type.metadata.create(
            metadata_type=self._test_metadata_type, required=False
        )
