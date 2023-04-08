from ..classes import SourceBackend
from ..source_backends.source_backend_mixins import SourceBackendPeriodicMixin

__all__ = ('SourceBackendSimple', 'SourceBackendTestPeriodic')


class SourceBackendSimple(SourceBackend):
    label = 'Test source backend'

    @classmethod
    def get_setup_form_fields(cls):
        fields = super().get_setup_form_fields()

        fields.update(
            {
                'test_field': {
                    'label': 'Test field',
                    'class': 'django.forms.CharField',
                    'required': False
                }
            }
        )

        return fields

    @classmethod
    def get_setup_form_fieldsets(cls):
        fieldsets = super().get_setup_form_fieldsets()

        fieldsets += (
            (
                'Testing', {
                    'fields': ('test_field')
                },
            ),
        )

        return fieldsets

    def process_documents(self, dry_run=False):
        """Do nothing. This method is added to allow view testing."""


class SourceBackendTestPeriodic(SourceBackendPeriodicMixin, SourceBackend):
    label = 'Test periodic source backend'
