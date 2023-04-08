from pathlib import Path
import shutil

from mayan.apps.documents.tests.literals import TEST_FILE_NON_ASCII_PATH
from mayan.apps.storage.utils import mkdtemp
from mayan.apps.testing.tests.base import BaseTestCase

from ..source_backends.staging_folder_backends import StagingFolderFile

from .mocks import MockStagingFolder


class StagingFolderFileTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.temporary_directory = mkdtemp()
        shutil.copy(
            src=TEST_FILE_NON_ASCII_PATH, dst=self.temporary_directory
        )
        self.test_filename = Path(TEST_FILE_NON_ASCII_PATH).name
        self._test_staging_folder = MockStagingFolder()
        self._test_staging_folder.kwargs['folder_path'] = self.temporary_directory
        self._test_staging_folder_files = []

    def tearDown(self):
        for test_staging_folder_file in self._test_staging_folder_files:
            try:
                test_staging_folder_file.delete()
            except FileNotFoundError:
                """Ignore file not found errors."""

        shutil.rmtree(path=self.temporary_directory)
        super().tearDown()

    def test_unicode_staging_folder_file(self):
        self._test_staging_folder_files.append(
            StagingFolderFile(
                filename=self.test_filename,
                staging_source=self._test_staging_folder
            )
        )

        self._test_staging_folder_files.append(
            StagingFolderFile(
                encoded_filename=self._test_staging_folder_files[0].encoded_filename,
                staging_source=self._test_staging_folder
            )
        )

        self.assertEqual(
            self._test_staging_folder_files[1].filename, self.test_filename
        )

    def test_staging_folder_file_generate_image_method(self):
        self._test_staging_folder_files.append(
            StagingFolderFile(
                filename=self.test_filename,
                staging_source=self._test_staging_folder
            )
        )

        self.assertNotEqual(
            self._test_staging_folder_files[0].generate_image(), ''
        )
