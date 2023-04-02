import base64
import logging
import os
from pathlib import Path
import time
from urllib.parse import quote_plus, unquote_plus

from furl import furl

from django.core.files import File
from django.core.files.base import ContentFile
from django.utils.encoding import force_text
from django.utils.functional import cached_property

from rest_framework.reverse import reverse as rest_framework_reverse

from mayan.apps.converter.classes import ConverterBase
from mayan.apps.converter.exceptions import InvalidOfficeFormat
from mayan.apps.converter.transformations import TransformationResize
from mayan.apps.source_apps.sources.literals import STORAGE_NAME_SOURCE_CACHE_FOLDER
from mayan.apps.storage.classes import DefinedStorage

logger = logging.getLogger(name=__name__)


class StagingSourceFile:
    """
    Simple class to extend the File class to add preview capabilities
    files in a directory on a storage.
    """
    def __init__(self, staging_source, filename=None, encoded_filename=None):
        self.staging_source = staging_source
        if encoded_filename:
            self.encoded_filename = str(encoded_filename)

            try:
                self.filename = base64.urlsafe_b64decode(
                    s=unquote_plus(self.encoded_filename)
                ).decode('utf8')
            except UnicodeDecodeError:
                raise ValueError(
                    'Incorrect `encoded_filename` value.'
                )
        else:
            if not filename:
                raise KeyError(
                    'Supply either `encoded_filename` or `filename` when '
                    'instantiating a staging source file.'
                )
            self.filename = filename
            self.encoded_filename = quote_plus(
                base64.urlsafe_b64encode(
                    s=filename.encode('utf8')
                )
            )

    def __str__(self):
        return force_text(s=self.filename)

    def as_file(self):
        return File(
            file=self.open(
                file=self.get_full_path(), mode='rb'
            ), name=self.filename
        )

    @property
    def cache_filename(self):
        return '{}-{}'.format(
            self.staging_source.model_instance_id, self.encoded_filename
        )

    def delete(self):
        try:
            self.storage_source_cache.delete(name=self.cache_filename)
        except FileNotFoundError:
            """No preview was yet generated."""

    def generate_image(self, transformation_instance_list=None):
        # Check is transformed image is available.
        logger.debug(
            'transformations cache filename: %s', self.cache_filename
        )

        if self.storage_source_cache.exists(self.cache_filename):
            logger.debug(
                'staging file cache file "%s" found', self.cache_filename
            )
        else:
            logger.debug(
                'staging file cache file "%s" not found', self.cache_filename
            )
            image = self.get_image(
                transformation_instance_list=transformation_instance_list
            )

            # Since open "wb+" doesn't create files, check if the file
            # exists, if not then create it.
            self.storage_source_cache.save(
                content=ContentFile(content=b''), name=self.cache_filename
            )

            with self.storage_source_cache.open(name=self.cache_filename, mode='wb+') as file_object:
                file_object.write(
                    image.getvalue()
                )

        return self.cache_filename

    def get_api_image_url(
        self, maximum_layer_order=None, transformation_instance_list=None,
        request=None, user=None
    ):
        final_url = furl()
        final_url.args = {'encoded_filename': self.encoded_filename}
        final_url.path = rest_framework_reverse(
            'rest_api:source-action', kwargs={
                'action_name': 'file_image',
                'source_id': self.staging_source.model_instance_id
            }, request=request
        )

        return final_url.tostr()

    def get_combined_transformation_list(
        self, maximum_layer_order=None, transformation_instance_list=None,
        user=None
    ):
        """
        Return a list of transformation containing the server side
        transformations for this object as well as transformations
        created from the arguments as transient interactive transformation.
        """
        result = [
            TransformationResize(
                height=self.staging_source.kwargs['preview_height'],
                width=self.staging_source.kwargs['preview_width']
            )
        ]

        # Interactive transformations second.
        result.extend(
            transformation_instance_list or []
        )

        return result

    def get_image(self, transformation_instance_list=None):
        try:
            with self.open(file=self.get_full_path(), mode='rb') as file_object:
                converter = ConverterBase.get_converter_class()(
                    file_object=file_object
                )

                try:
                    with converter.to_pdf() as pdf_file_object:
                        image_converter = ConverterBase.get_converter_class()(
                            file_object=pdf_file_object
                        )
                        page_image = image_converter.get_page()
                except InvalidOfficeFormat:
                    page_image = converter.get_page()
        except Exception as exception:
            # Cleanup in case of error.
            logger.error(
                'Error getting staging file image for file "%s"; %s',
                self.get_full_path(), exception
            )
            raise
        else:
            return page_image

    @cached_property
    def storage_source_cache(self):
        return DefinedStorage.get(
            name=STORAGE_NAME_SOURCE_CACHE_FOLDER
        ).get_storage_instance()


class StagingFolderFile(StagingSourceFile):
    """
    Subclass of StagingSourceFile that works only for mounted or local
    block storages.
    """
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

        self.get_full_path().unlink()

    def get_date_time_created(self):
        return time.ctime(
            os.path.getctime(
                self.get_full_path()
            )
        )

    def get_full_path(self):
        return Path(
            self.staging_source.kwargs['folder_path'], self.filename
        )

    def open(self, file, mode):
        return open(file=file, mode=mode)
