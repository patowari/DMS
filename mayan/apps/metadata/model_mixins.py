from mayan.apps.common.utils import comma_splitter
from mayan.apps.templating.classes import Template

from .classes import MetadataLookup


class DocumentMetadataBusinessLogicMixin:
    @property
    def is_required(self):
        """
        Return a boolean value of True of this metadata instance's parent
        type is required for the stored document type.
        """
        return self.metadata_type.get_required_for(
            document_type=self.document.document_type
        )


class MetadataTypeBusinessLogicMixin:
    def get_default_value(self):
        template = Template(template_string=self.default)
        return template.render()

    def get_lookup_values(self):
        template = Template(template_string=self.lookup)

        metadata_lookup_context = MetadataLookup.get_as_context()

        template_result = template.render(context=metadata_lookup_context)

        return comma_splitter(string=template_result)

    def get_required_for(self, document_type):
        """
        Determine if the metadata type is required for the
        specified document type.
        """
        queryset = document_type.metadata.filter(
            required=True, metadata_type=self
        )

        return queryset.exists()
