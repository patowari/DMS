import logging
from pathlib import Path

from django.utils.translation import ugettext_lazy as _

from mayan.apps.appearance.classes import Icon
from mayan.apps.navigation.classes import SourceColumn
from mayan.apps.source_apps.sources.classes import SourceBackend
from mayan.apps.source_apps.sources.source_backends.source_backend_mixins import (
    SourceBackendCompressedMixin, SourceBackendInteractiveMixin,
    SourceBackendRegularExpressionMixin
)

from .staging_source_mixins import SourceBackendMixinFileList
from .staging_source_files import StagingFolderFile

__all__ = ('SourceBackendStagingFolder',)
logger = logging.getLogger(name=__name__)


class SourceBackendStagingFolder(
    SourceBackendCompressedMixin, SourceBackendInteractiveMixin,
    SourceBackendRegularExpressionMixin, SourceBackendMixinFileList,
    SourceBackend
):
    icon = Icon(driver_name='fontawesome', symbol='file')
    label = _('Staging folder')
    staging_source_file_class = StagingFolderFile

    @classmethod
    def get_setup_form_fields(cls):
        fields = super().get_setup_form_fields()

        fields.update(
            {
                'folder_path': {
                    'class': 'django.forms.CharField',
                    'default': '',
                    'help_text': _(
                        'Server side filesystem path.'
                    ),
                    'kwargs': {
                        'max_length': 255,
                    },
                    'label': _('Folder path'),
                    'required': True
                }, 'include_subdirectories': {
                    'class': 'django.forms.BooleanField',
                    'default': '',
                    'help_text': _(
                        'If checked, not only will the folder path be scanned for '
                        'files but also its subdirectories.'
                    ),
                    'label': _('Include subdirectories?'),
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
                _('Storage'), {
                    'fields': (
                        'folder_path', 'include_subdirectories'
                    )
                },
            ),
        )

        return fieldsets

    @classmethod
    def intialize(cls):
        super().intialize()

        SourceColumn(
            func=lambda context: context['object'].get_date_time_created(),
            label=_('Created'), source=cls.staging_source_file_class
        )

    def get_files(self):
        exclude_regex = self.get_regex_exclude()
        include_regex = self.get_regex_include()

        path = Path(
            self.kwargs['folder_path']
        )

        # Force path check to trigger any error.
        path.lstat()

        if self.kwargs.get('include_subdirectories', False):
            iterator = path.rglob(pattern='*')
        else:
            iterator = path.glob(pattern='*')

        for entry in sorted(iterator):
            if entry.is_file() and include_regex.match(string=entry.name) and not exclude_regex.match(string=entry.name):
                relative_filename = str(
                    entry.relative_to(
                        self.kwargs['folder_path']
                    )
                )
                yield self.get_file(
                    filename=relative_filename
                )
