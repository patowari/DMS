import logging
from pathlib import Path

from django.core.files import File
from django.utils.translation import ugettext_lazy as _

from mayan.apps.storage.models import SharedUploadedFile
from mayan.apps.source_apps.sources.classes import SourceBackend
from mayan.apps.source_apps.sources.exceptions import SourceException
from mayan.apps.source_apps.sources.source_backends.source_backend_mixins import (
    SourceBackendCompressedPeriodicMixin, SourceBackendRegularExpressionMixin
)

__all__ = ('SourceBackendWatchFolder',)
logger = logging.getLogger(name=__name__)


class SourceBackendWatchFolder(
    SourceBackendCompressedPeriodicMixin,
    SourceBackendRegularExpressionMixin, SourceBackend
):
    label = _('Watch folder')

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
                },
                'include_subdirectories': {
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
                    'fields': ('folder_path', 'include_subdirectories')
                }
            ),
        )

        return fieldsets

    def get_shared_uploaded_files(self):
        dry_run = self.process_kwargs.get('dry_run', False)

        exclude_regex = self.get_regex_exclude()
        include_regex = self.get_regex_include()

        path = Path(
            self.kwargs['folder_path']
        )

        # Force testing the path and raise errors for the log.
        path.lstat()
        if not path.is_dir():
            raise SourceException(
                'Path {} is not a directory.'.format(path)
            )

        if self.kwargs.get('include_subdirectories', False):
            iterator = path.rglob(pattern='*')
        else:
            iterator = path.glob(pattern='*')

        for entry in iterator:
            if entry.is_file() or entry.is_symlink():
                if include_regex.match(string=entry.name) and not exclude_regex.match(string=entry.name):
                    with entry.open(mode='rb+') as file_object:
                        shared_uploaded_file = SharedUploadedFile.objects.create(
                            file=File(file=file_object), filename=entry.name
                        )
                        if not dry_run:
                            entry.unlink()

                        return (shared_uploaded_file,)
