from ...forms import NewDocumentForm

from ..mocks import MockRequest


class InteractiveSourceBackendTestMixin:
    class MockSourceForm:
        def __init__(self, **kwargs):
            self.cleaned_data = kwargs

    def setUp(self):
        super().setUp()
        self._test_document_form = self.get_test_document_form()

    def get_test_document_form(self):
        document_form = NewDocumentForm(
            data={}, document_type=self._test_document_type
        )
        document_form.full_clean()

        return document_form

    def get_test_request(self):
        return MockRequest(user=self._test_case_user)
