from ...classes import EventTypeNamespace

from ..literals import (
    TEST_EVENT_TYPE_LABEL, TEST_EVENT_TYPE_NAME,
    TEST_EVENT_TYPE_NAMESPACE_LABEL, TEST_EVENT_TYPE_NAMESPACE_NAME
)


class EventTypeTestMixin:
    def setUp(self):
        super().setUp()
        self._test_event_type_list = []

    def _create_test_event_type(self):
        total_test_event_type_count = len(self._test_event_type_list)
        test_namespace_label = '{}_{}'.format(
            TEST_EVENT_TYPE_NAMESPACE_LABEL, total_test_event_type_count
        )
        test_namespace_name = '{}_{}'.format(
            TEST_EVENT_TYPE_NAMESPACE_NAME, total_test_event_type_count
        )
        test_event_label = '{}_{}'.format(
            TEST_EVENT_TYPE_LABEL, total_test_event_type_count
        )
        test_event_name = '{}_{}'.format(
            TEST_EVENT_TYPE_NAME, total_test_event_type_count
        )

        self._test_event_type_namespace = EventTypeNamespace(
            label=test_namespace_label, name=test_namespace_name
        )
        self._test_event_type = self._test_event_type_namespace.add_event_type(
            label=test_event_label, name=test_event_name
        )
        self._test_event_type_list.append(self._test_event_type)


class EventTypeNamespaceAPITestMixin(EventTypeTestMixin):
    def _request_test_event_type_list_api_view(self):
        return self.get(viewname='rest_api:event-type-list')

    def _request_test_event_namespace_list_api_view(self):
        return self.get(viewname='rest_api:event-type-namespace-list')

    def _request_test_event_type_namespace_event_type_list_api_view(self):
        return self.get(
            viewname='rest_api:event-type-namespace-event-type-list',
            kwargs={
                'name': self._test_event_type_namespace.name
            }
        )
