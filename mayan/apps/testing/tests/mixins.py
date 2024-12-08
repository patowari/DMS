import glob
import os
import time

import psutil
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver

from django.conf import settings
from django.db.models import Q
from django.urls import reverse

from mayan.apps.storage.settings import setting_temporary_directory


class ContentTypeCheckTestCaseMixin:
    expected_content_types = ('text/html', 'text/html; charset=utf-8')

    def _pre_setup(self):
        super()._pre_setup()
        test_instance = self

        class CustomClient(self.client_class):
            def request(self, *args, **kwargs):
                response = super().request(*args, **kwargs)

                content_type = response.headers.get('content-type', '')
                if test_instance.expected_content_types:
                    test_instance.assertTrue(
                        content_type in test_instance.expected_content_types,
                        msg='Unexpected response content type: {}, expected: {}.'.format(
                            content_type, ' or '.join(
                                test_instance.expected_content_types
                            )
                        )
                    )

                return response

        self.client = CustomClient()


class DelayTestCaseMixin:
    def _test_delay(self, seconds=0.1):
        time.sleep(seconds)


class DescriptorLeakCheckTestCaseMixin:
    _skip_file_descriptor_test = False

    def _get_process_descriptor_count(self):
        process = psutil.Process()
        return process.num_fds()

    def _get_process_descriptors(self):
        process = psutil.Process()._proc
        return os.listdir(
            path='{}/{}/fd'.format(process._procfs_path, process.pid)
        )

    def setUp(self):
        super().setUp()
        self._process_descriptor_count = self._get_process_descriptor_count()
        self._process_descriptors = self._get_process_descriptors()

    def tearDown(self):
        if not self._skip_file_descriptor_test:
            if self._get_process_descriptor_count() > self._process_descriptor_count:
                raise ValueError(
                    'File descriptor leak. The number of file descriptors '
                    'at the end are higher than at the start of the test.'
                )

            for descriptor in self._get_process_descriptors():
                if descriptor not in self._process_descriptors:
                    raise ValueError(
                        'File descriptor leak. A descriptor was found at '
                        'the end of the test that was not present at the '
                        'start of the test.'
                    )

        super().tearDown()


class EnvironmentTestCaseMixin:
    def setUp(self):
        super().setUp()
        self._test_environment_variable_list = []

    def tearDown(self):
        for name in self._test_environment_variable_list:
            os.environ.pop(name)

        super().tearDown()

    def _set_environment_variable(self, name, value):
        self._test_environment_variable_list.append(name)
        os.environ[name] = value


class OpenFileCheckTestCaseMixin:
    _skip_open_file_leak_test = False

    def _get_open_files(self):
        process = psutil.Process()
        return process.open_files()

    def setUp(self):
        super().setUp()

        self._open_files = self._get_open_files()

    def tearDown(self):
        if not self._skip_open_file_leak_test:
            for new_open_file in self._get_open_files():
                if new_open_file not in self._open_files:
                    raise ValueError(
                        'File left open: {}'.format(new_open_file)
                    )

        super().tearDown()


class SeleniumTestMixin:
    SKIP_VARIABLE_NAME = 'TESTS_SELENIUM_SKIP'

    @staticmethod
    def _get_skip_variable_value():
        return os.environ.get(
            SeleniumTestMixin._get_skip_variable_environment_name(),
            getattr(settings, SeleniumTestMixin.SKIP_VARIABLE_NAME, False)
        )

    @staticmethod
    def _get_skip_variable_environment_name():
        return 'MAYAN_{}'.format(SeleniumTestMixin.SKIP_VARIABLE_NAME)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.webdriver = None
        if not SeleniumTestMixin._get_skip_variable_value():
            options = Options()
            options.add_argument('--headless')
            cls.webdriver = WebDriver(
                firefox_options=options, log_path='/dev/null'
            )

    @classmethod
    def tearDownClass(cls):
        if cls.webdriver:
            cls.webdriver.quit()
        super().tearDownClass()

    def setUp(self):
        if SeleniumTestMixin._get_skip_variable_value():
            self.skipTest(reason='Skipping selenium test')
        super().setUp()

    def _open_url(self, fragment=None, path=None, viewname=None):
        url = '{}{}{}'.format(
            self.live_server_url, path or reverse(viewname=viewname),
            fragment or ''
        )

        self.webdriver.get(url=url)


class TempfileCheckTestCasekMixin:
    # Ignore the jvmstat instrumentation and GitLab's CI .config files.
    # Ignore LibreOffice fontconfig cache dir.
    ignore_globs = ('hsperfdata_*', '.config', '.cache')

    def _get_temporary_entries(self):
        ignored_result = []

        # Expand globs by joining the temporary directory and then flattening
        # the list of lists into a single list.
        for item in self.ignore_globs:
            ignored_result.extend(
                glob.glob(
                    os.path.join(setting_temporary_directory.value, item)
                )
            )

        # Remove the path and leave only the expanded filename.
        ignored_result = map(lambda x: os.path.split(x)[-1], ignored_result)

        return set(
            os.listdir(setting_temporary_directory.value)
        ) - set(ignored_result)

    def setUp(self):
        super().setUp()
        if getattr(settings, 'COMMON_TEST_TEMP_FILES', False):
            self._temporary_items = self._get_temporary_entries()

    def tearDown(self):
        if getattr(settings, 'COMMON_TEST_TEMP_FILES', False):
            final_temporary_items = self._get_temporary_entries()
            self.assertEqual(
                self._temporary_items, final_temporary_items,
                msg='Orphan temporary file. The number of temporary '
                'files and/or directories at the start and at the end of '
                'the test are not the same. Orphan entries: {}'.format(
                    ','.join(final_temporary_items - self._temporary_items)
                )
            )
        super().tearDown()


class TestMixinObjectCreationTrack:
    _test_object_list_name = None
    _test_object_model = None
    _test_object_name = None

    def _test_object_get_object_list_name(self, test_object_list_name=None):
        test_object_list_name = test_object_list_name or self._test_object_list_name or '{}_list'.format(
            self._test_object_name
        )

        return test_object_list_name

    def _test_object_list_set(self, test_object_list_name=None):
        self._test_object_list_name = self._test_object_get_object_list_name(
            test_object_list_name=test_object_list_name
        )

        _test_object_list = self._test_object_model.objects.filter(
            ~Q(pk__in=self._test_object_pk_list)
        )

        setattr(
            self, self._test_object_list_name, _test_object_list
        )

    def _test_object_set(self, test_object_name=None):
        test_object_name = test_object_name or self._test_object_name

        try:
            _test_object = self._test_object_model.objects.get(
                ~Q(pk__in=self._test_object_pk_list)
            )
        except self._test_object_model.DoesNotExist:
            _test_object = None

        setattr(self, test_object_name, _test_object)

    def _test_object_track(self):
        self._test_object_pk_list = list(
            self._test_object_model.objects.values_list('pk', flat=True)
        )
