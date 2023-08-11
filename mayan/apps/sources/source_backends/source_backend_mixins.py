import logging
import re

from django.utils.translation import ugettext_lazy as _

from .literals import (
    REGULAR_EXPRESSION_MATCH_EVERYTHING, REGULAR_EXPRESSION_MATCH_NOTHING
)

logger = logging.getLogger(name=__name__)


class SourceBackendMixinRegularExpression:
    @classmethod
    def get_form_fields(cls):
        fields = super().get_form_fields()

        fields.update(
            {
                'include_regex': {
                    'class': 'django.forms.CharField',
                    'default': '',
                    'help_text': _(
                        'Regular expression used to select which files '
                        'to upload.'
                    ),
                    'label': _('Include regular expression'),
                    'required': False
                },
                'exclude_regex': {
                    'class': 'django.forms.CharField',
                    'default': '',
                    'help_text': _(
                        'Regular expression used to exclude which files '
                        'to upload.'
                    ),
                    'label': _('Exclude regular expression'),
                    'required': False
                }
            }
        )

        return fields

    @classmethod
    def get_form_fieldsets(cls):
        fieldsets = super().get_form_fieldsets()

        fieldsets += (
            (
                _('Content selection'), {
                    'fields': ('include_regex', 'exclude_regex')
                },
            ),
        )

        return fieldsets

    def get_regex_exclude(self):
        return re.compile(
            pattern=self.kwargs.get(
                'exclude_regex', REGULAR_EXPRESSION_MATCH_NOTHING
            ) or REGULAR_EXPRESSION_MATCH_NOTHING
        )

    def get_regex_include(self):
        return re.compile(
            pattern=self.kwargs.get(
                'include_regex', REGULAR_EXPRESSION_MATCH_EVERYTHING
            )
        )
