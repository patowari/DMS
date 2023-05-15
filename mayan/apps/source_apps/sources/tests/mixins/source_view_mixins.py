from django.db.models import Q

from ...models import Source
from ...source_backends.literals import SOURCE_UNCOMPRESS_CHOICE_NEVER

from ..literals import (
    TEST_SOURCE_BACKEND_PATH, TEST_SOURCE_LABEL, TEST_SOURCE_LABEL_EDITED
)


class SourceViewTestMixin:
    def _request_test_source_backend_selection_view(self):
        return self.get(
            viewname='sources:source_backend_selection'
        )

    def _request_test_source_create_view(
        self, backend_path=None, extra_data=None
    ):
        pk_list = list(
            Source.objects.values_list('pk', flat=True)
        )

        data = {
            'enabled': True,
            'label': TEST_SOURCE_LABEL,
            'uncompress': SOURCE_UNCOMPRESS_CHOICE_NEVER
        }

        if extra_data:
            data.update(extra_data)

        response = self.post(
            kwargs={
                'backend_path': backend_path or TEST_SOURCE_BACKEND_PATH
            }, viewname='sources:source_create', data=data
        )

        try:
            self._test_source = Source.objects.get(~Q(pk__in=pk_list))
        except Source.DoesNotExist:
            self._test_source = None

        return response

    def _request_test_source_delete_view(self):
        return self.post(
            viewname='sources:source_delete', kwargs={
                'source_id': self._test_source.pk
            }
        )

    def _request_test_source_edit_view_get(self):
        return self.get(
            viewname='sources:source_edit', kwargs={
                'source_id': self._test_source.pk
            }, data={
                'label': TEST_SOURCE_LABEL_EDITED
            }
        )

    def _request_test_source_edit_view(self):
        return self.post(
            viewname='sources:source_edit', kwargs={
                'source_id': self._test_source.pk
            }, data={
                'label': TEST_SOURCE_LABEL_EDITED
            }
        )

    def _request_test_source_list_view(self):
        return self.get(viewname='sources:source_list')

    def _request_test_source_test_get_view(self):
        return self.get(
            viewname='sources:source_test', kwargs={
                'source_id': self._test_source.pk
            }
        )

    def _request_test_source_test_post_view(self):
        return self.post(
            viewname='sources:source_test', kwargs={
                'source_id': self._test_source.pk
            }
        )
