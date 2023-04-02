import logging

from django import forms
from django.utils.translation import ugettext_lazy as _

from mayan.apps.source_apps.sources.forms import UploadBaseForm

logger = logging.getLogger(name=__name__)


class StagingUploadForm(UploadBaseForm):
    """
    Form that show all the files in the staging source specified by the
    StagingFolderFile class passed as 'cls' argument.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.fields['staging_source_file_id'].choices = [
                (
                    staging_source_file.encoded_filename, str(
                        staging_source_file
                    )
                ) for staging_source_file in self.source.get_backend_instance().get_files()
            ]
        except Exception as exception:
            logger.error('exception: %s', exception)

    staging_source_file_id = forms.ChoiceField(
        label=_('Staging file'), widget=forms.widgets.Select(
            attrs={'class': 'select2'}
        )
    )
