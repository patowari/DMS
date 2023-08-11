from .interactive_mixins import InteractiveSourceBackendTestMixin


class SourceDocumentUploadWizardTestMixin(InteractiveSourceBackendTestMixin):
    def _request_document_upload_wizard_get_view(self):
        return self.get(
            viewname='sources:document_upload_wizard'
        )

    def _request_document_upload_wizard_post_view(self):
        return self.post(
            viewname='sources:document_upload_wizard', data={
                'document_create_wizard-current_step': 0,
                'document_type_selection-document_type': self._test_document_type.pk
            }
        )
