from django.db.models import Q

from ...models import Source

from ..literals import (
    TEST_SOURCE_BACKEND_PATH, TEST_SOURCE_LABEL, TEST_SOURCE_LABEL_EDITED
)


class SourceAPIViewTestMixin:
    def _request_test_source_create_api_view(
        self, backend_path=None, extra_data=None
    ):
        pk_list = list(
            Source.objects.values_list('pk', flat=True)
        )

        data = {
            'backend_path': backend_path or TEST_SOURCE_BACKEND_PATH,
            'enabled': True,
            'label': TEST_SOURCE_LABEL
        }

        if extra_data:
            data.update(extra_data)

        response = self.post(viewname='rest_api:source-list', data=data)

        try:
            self._test_source = Source.objects.get(
                ~Q(pk__in=pk_list)
            )
        except Source.DoesNotExist:
            self._test_source = None

        return response

    def _request_test_source_delete_api_view(self):
        return self.delete(
            viewname='rest_api:source-detail', kwargs={
                'source_id': self._test_source.pk
            }
        )

    def _request_test_source_edit_api_view_via_patch(self):
        return self.patch(
            viewname='rest_api:source-detail', kwargs={
                'source_id': self._test_source.pk
            }, data={'label': TEST_SOURCE_LABEL_EDITED}
        )

    def _request_test_source_edit_api_view_via_put(self):
        data = {
            'backend_path': self._test_source.backend_path,
            'enabled': self._test_source.enabled,
            'label': TEST_SOURCE_LABEL_EDITED
        }

        return self.put(
            viewname='rest_api:source-detail', kwargs={
                'source_id': self._test_source.pk
            }, data=data
        )

    def _request_test_source_list_api_view(self):
        return self.get(viewname='rest_api:source-list')
