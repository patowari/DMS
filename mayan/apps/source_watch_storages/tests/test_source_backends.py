from pathlib import Path

from mayan.apps.documents.events import (
    event_document_created, event_document_file_created,
    event_document_file_edited, event_document_version_created,
    event_document_version_page_created
)
from mayan.apps.documents.models import Document
from mayan.apps.documents.tests.base import GenericDocumentTestCase
from mayan.apps.documents.tests.literals import (
    TEST_DOCUMENT_SMALL_CHECKSUM, TEST_FILE_COMPRESSED_PATH,
    TEST_FILE_SMALL_PATH
)
from mayan.apps.source_compressed.source_backends.literals import (
    SOURCE_UNCOMPRESS_CHOICE_ALWAYS, SOURCE_UNCOMPRESS_CHOICE_NEVER
)
from mayan.apps.sources.exceptions import SourceActionException

from .mixins import WatchStorageSourceTestMixin


class WatchStorageSourceBackendActionDocumentUploadTestCase(
    WatchStorageSourceTestMixin, GenericDocumentTestCase
):
    _test_source_create_auto = False
    auto_upload_test_document = False

    def test_basic(self):
        self._test_source_create()

        document_count = Document.objects.count()

        self.copy_test_source_file()

        self._clear_events()

        self._execute_test_source_action(action_name='document_upload')

        self.assertEqual(Document.objects.count(), document_count + 1)
        self.assertEqual(
            Document.objects.first().file_latest.checksum,
            TEST_DOCUMENT_SMALL_CHECKSUM
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 5)

        test_document = Document.objects.first()
        test_document_file = test_document.file_latest
        test_document_version = test_document.version_active
        test_document_version_page = test_document_version.pages.first()

        self.assertEqual(events[0].action_object, self._test_document_type)
        self.assertEqual(events[0].actor, test_document)
        self.assertEqual(events[0].target, test_document)
        self.assertEqual(events[0].verb, event_document_created.id)

        self.assertEqual(events[1].action_object, test_document)
        self.assertEqual(events[1].actor, test_document_file)
        self.assertEqual(events[1].target, test_document_file)
        self.assertEqual(events[1].verb, event_document_file_created.id)

        self.assertEqual(events[2].action_object, test_document)
        self.assertEqual(events[2].actor, test_document_file)
        self.assertEqual(events[2].target, test_document_file)
        self.assertEqual(events[2].verb, event_document_file_edited.id)

        self.assertEqual(events[3].action_object, test_document)
        self.assertEqual(events[3].actor, test_document_version)
        self.assertEqual(events[3].target, test_document_version)
        self.assertEqual(events[3].verb, event_document_version_created.id)

        self.assertEqual(events[4].action_object, test_document_version)
        self.assertEqual(events[4].actor, test_document_version_page)
        self.assertEqual(events[4].target, test_document_version_page)
        self.assertEqual(
            events[4].verb, event_document_version_page_created.id
        )

    def test_compressed_always(self):
        self._test_source_create(
            extra_data={'uncompress': SOURCE_UNCOMPRESS_CHOICE_ALWAYS}
        )

        self.copy_test_source_file(
            source_path=TEST_FILE_COMPRESSED_PATH
        )

        test_document_count = Document.objects.count()

        self._clear_events()

        self._execute_test_source_action(action_name='document_upload')

        self.assertEqual(Document.objects.count(), test_document_count + 2)

        events = self._get_test_events()
        self.assertEqual(events.count(), 11)

        test_documents = Document.objects.all()

        self.assertEqual(events[0].action_object, self._test_document_type)
        self.assertEqual(events[0].actor, test_documents[0])
        self.assertEqual(events[0].target, test_documents[0])
        self.assertEqual(events[0].verb, event_document_created.id)

        self.assertEqual(events[1].action_object, test_documents[0])
        self.assertEqual(events[1].actor, test_documents[0].file_latest)
        self.assertEqual(events[1].target, test_documents[0].file_latest)
        self.assertEqual(events[1].verb, event_document_file_created.id)

        self.assertEqual(events[2].action_object, test_documents[0])
        self.assertEqual(events[2].actor, test_documents[0].file_latest)
        self.assertEqual(events[2].target, test_documents[0].file_latest)
        self.assertEqual(events[2].verb, event_document_file_edited.id)

        self.assertEqual(events[3].action_object, test_documents[0])
        self.assertEqual(events[3].actor, test_documents[0].version_active)
        self.assertEqual(events[3].target, test_documents[0].version_active)
        self.assertEqual(events[3].verb, event_document_version_created.id)

        self.assertEqual(
            events[4].action_object, test_documents[0].version_active
        )
        self.assertEqual(
            events[4].actor, test_documents[0].version_active.pages.first()
        )
        self.assertEqual(
            events[4].target, test_documents[0].version_active.pages.first()
        )
        self.assertEqual(
            events[4].verb, event_document_version_page_created.id
        )

        self.assertEqual(events[5].action_object, self._test_document_type)
        self.assertEqual(events[5].actor, test_documents[1])
        self.assertEqual(events[5].target, test_documents[1])
        self.assertEqual(events[5].verb, event_document_created.id)

        self.assertEqual(events[6].action_object, test_documents[1])
        self.assertEqual(events[6].actor, test_documents[1].file_latest)
        self.assertEqual(events[6].target, test_documents[1].file_latest)
        self.assertEqual(events[6].verb, event_document_file_created.id)

        self.assertEqual(events[7].action_object, test_documents[1])
        self.assertEqual(events[7].actor, test_documents[1].file_latest)
        self.assertEqual(events[7].target, test_documents[1].file_latest)
        self.assertEqual(events[7].verb, event_document_file_edited.id)

        self.assertEqual(events[8].action_object, test_documents[1])
        self.assertEqual(events[8].actor, test_documents[1].version_active)
        self.assertEqual(events[8].target, test_documents[1].version_active)
        self.assertEqual(events[8].verb, event_document_version_created.id)

        self.assertEqual(
            events[9].action_object, test_documents[1].version_active
        )
        self.assertEqual(
            events[9].actor, test_documents[1].version_active.pages.first()
        )
        self.assertEqual(
            events[9].target, test_documents[1].version_active.pages.first()
        )
        self.assertEqual(
            events[9].verb, event_document_version_page_created.id
        )

        self.assertEqual(
            events[10].action_object, test_documents[1].version_active
        )
        self.assertEqual(
            events[10].actor, test_documents[1].version_active.pages.last()
        )
        self.assertEqual(
            events[10].target, test_documents[1].version_active.pages.last()
        )
        self.assertEqual(
            events[10].verb, event_document_version_page_created.id
        )

    def test_compressed_never(self):
        self._silence_logger(name='mayan.apps.converter.backends')

        self._test_source_create(
            extra_data={'uncompress': SOURCE_UNCOMPRESS_CHOICE_NEVER}
        )

        self.copy_test_source_file(
            source_path=TEST_FILE_COMPRESSED_PATH
        )

        test_document_count = Document.objects.count()

        self._clear_events()

        self._execute_test_source_action(action_name='document_upload')

        self.assertEqual(Document.objects.count(), test_document_count + 1)

        events = self._get_test_events()
        self.assertEqual(events.count(), 3)

        test_document = Document.objects.first()
        test_document_file = test_document.file_latest
        test_document_version = test_document.version_active

        self.assertEqual(events[0].action_object, self._test_document_type)
        self.assertEqual(events[0].actor, test_document)
        self.assertEqual(events[0].target, test_document)
        self.assertEqual(events[0].verb, event_document_created.id)

        self.assertEqual(events[1].action_object, test_document)
        self.assertEqual(events[1].actor, test_document_file)
        self.assertEqual(events[1].target, test_document_file)
        self.assertEqual(events[1].verb, event_document_file_created.id)

        self.assertEqual(events[2].action_object, test_document)
        self.assertEqual(events[2].actor, test_document_version)
        self.assertEqual(events[2].target, test_document_version)
        self.assertEqual(events[2].verb, event_document_version_created.id)

    def test_regular_expression_exclude_false(self):
        path = Path(TEST_FILE_SMALL_PATH)

        self._test_source_create(
            extra_data={'exclude_regex': path.name}
        )

        document_count = Document.objects.count()

        self.copy_test_source_file()

        self._clear_events()

        self._execute_test_source_action(action_name='document_upload')

        self.assertEqual(Document.objects.count(), document_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_regular_expression_exclude_true(self):
        self._test_source_create(
            extra_data={'exclude_regex': ''}
        )

        document_count = Document.objects.count()

        self.copy_test_source_file()

        self._clear_events()

        self._execute_test_source_action(action_name='document_upload')

        self.assertEqual(Document.objects.count(), document_count + 1)

        events = self._get_test_events()
        self.assertEqual(events.count(), 5)

        test_document = Document.objects.first()
        test_document_file = test_document.file_latest
        test_document_version = test_document.version_active
        test_document_version_page = test_document_version.pages.first()

        self.assertEqual(events[0].action_object, self._test_document_type)
        self.assertEqual(events[0].actor, test_document)
        self.assertEqual(events[0].target, test_document)
        self.assertEqual(events[0].verb, event_document_created.id)

        self.assertEqual(events[1].action_object, test_document)
        self.assertEqual(events[1].actor, test_document_file)
        self.assertEqual(events[1].target, test_document_file)
        self.assertEqual(events[1].verb, event_document_file_created.id)

        self.assertEqual(events[2].action_object, test_document)
        self.assertEqual(events[2].actor, test_document_file)
        self.assertEqual(events[2].target, test_document_file)
        self.assertEqual(events[2].verb, event_document_file_edited.id)

        self.assertEqual(events[3].action_object, test_document)
        self.assertEqual(events[3].actor, test_document_version)
        self.assertEqual(events[3].target, test_document_version)
        self.assertEqual(events[3].verb, event_document_version_created.id)

        self.assertEqual(events[4].action_object, test_document_version)
        self.assertEqual(events[4].actor, test_document_version_page)
        self.assertEqual(events[4].target, test_document_version_page)
        self.assertEqual(
            events[4].verb, event_document_version_page_created.id
        )

    def test_regular_expression_include_false(self):
        self._test_source_create(
            extra_data={'include_regex': '_____.*'}
        )

        document_count = Document.objects.count()

        self.copy_test_source_file()

        self._clear_events()

        self._execute_test_source_action(action_name='document_upload')

        self.assertEqual(Document.objects.count(), document_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_regular_expression_include_true(self):
        path = Path(TEST_FILE_SMALL_PATH)

        self._test_source_create(
            extra_data={'include_regex': path.name}
        )

        document_count = Document.objects.count()

        self.copy_test_source_file()

        self._clear_events()

        self._execute_test_source_action(action_name='document_upload')

        self.assertEqual(Document.objects.count(), document_count + 1)

        events = self._get_test_events()
        self.assertEqual(events.count(), 5)

        test_document = Document.objects.first()
        test_document_file = test_document.file_latest
        test_document_version = test_document.version_active
        test_document_version_page = test_document_version.pages.first()

        self.assertEqual(events[0].action_object, self._test_document_type)
        self.assertEqual(events[0].actor, test_document)
        self.assertEqual(events[0].target, test_document)
        self.assertEqual(events[0].verb, event_document_created.id)

        self.assertEqual(events[1].action_object, test_document)
        self.assertEqual(events[1].actor, test_document_file)
        self.assertEqual(events[1].target, test_document_file)
        self.assertEqual(events[1].verb, event_document_file_created.id)

        self.assertEqual(events[2].action_object, test_document)
        self.assertEqual(events[2].actor, test_document_file)
        self.assertEqual(events[2].target, test_document_file)
        self.assertEqual(events[2].verb, event_document_file_edited.id)

        self.assertEqual(events[3].action_object, test_document)
        self.assertEqual(events[3].actor, test_document_version)
        self.assertEqual(events[3].target, test_document_version)
        self.assertEqual(events[3].verb, event_document_version_created.id)

        self.assertEqual(events[4].action_object, test_document_version)
        self.assertEqual(events[4].actor, test_document_version_page)
        self.assertEqual(events[4].target, test_document_version_page)
        self.assertEqual(
            events[4].verb, event_document_version_page_created.id
        )


class WatchStorageSourceBackendActionFileDeleteTestCase(
    WatchStorageSourceTestMixin, GenericDocumentTestCase
):
    _test_source_create_auto = False
    auto_upload_test_document = False

    def test_basic(self):
        self._test_source_create()

        self.copy_test_source_file()

        test_source_backend_instance = self._test_source.get_backend_instance()

        test_staging_file_count = len(
            list(
                test_source_backend_instance.get_stored_file_list()
            )
        )

        self._clear_events()

        self._execute_test_source_action(action_name='file_delete')

        self.assertEqual(
            len(
                list(
                    test_source_backend_instance.get_stored_file_list()
                )
            ), test_staging_file_count - 1
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_nonexistent_file(self):
        self._test_source_create()

        self.copy_test_source_file()

        self._test_source_stored_test_file.unlink()

        test_source_backend_instance = self._test_source.get_backend_instance()

        test_staging_file_count = len(
            list(
                test_source_backend_instance.get_stored_file_list()
            )
        )

        self._clear_events()

        with self.assertRaises(expected_exception=SourceActionException):
            self._execute_test_source_action(action_name='file_delete')

        self.assertEqual(
            len(
                list(
                    test_source_backend_instance.get_stored_file_list()
                )
            ), test_staging_file_count
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)


class WatchStorageSourceBackendActionFileListTestCase(
    WatchStorageSourceTestMixin, GenericDocumentTestCase
):
    _test_source_create_auto = False
    auto_upload_test_document = False

    def test_basic(self):
        self._test_source_create()

        self.copy_test_source_file()

        self._clear_events()

        result = self._execute_test_source_action(action_name='file_list')

        self.assertEqual(
            list(result), [
                {
                    'encoded_filename': self._test_source_stored_file.encoded_filename,
                    'filename': self._test_source_stored_file.filename,
                    'size': self._test_source_stored_file.get_size()
                }
            ]
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_empty_list(self):
        self._test_source_create()

        self._clear_events()

        result = self._execute_test_source_action(action_name='file_list')

        self.assertEqual(
            list(result), []
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)
