from mayan.apps.sources.classes import DocumentCreateWizardStep


class SourceBackendMixinInteractive:
    is_interactive = True

    def callback_post_document_create(
        self, document, query_string, source_id, user_id=None,
    ):
        DocumentCreateWizardStep.post_upload_process(
            document=document, query_string=query_string,
            source_id=source_id, user_id=user_id
        )
