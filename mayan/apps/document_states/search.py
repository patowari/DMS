from django.utils.translation import ugettext_lazy as _

from mayan.apps.documents.search import (
    search_model_document, search_model_document_file,
    search_model_document_file_page, search_model_document_version,
    search_model_document_version_page
)

# Document

search_model_document.add_model_field(
    field='workflows__log_entries__comment',
    label=_('Document workflow transition comment')
)
