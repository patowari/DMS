import glob
import os
import random
import time

import psutil
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import connection, connections, models
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.urls import reverse

from mayan.apps.acls.classes import ModelPermission
from mayan.apps.permissions.tests.mixins import PermissionTestMixin
from mayan.apps.storage.settings import setting_temporary_directory

from .utils import RandomSeedIdempotent


class ConnectionsCheckTestCaseMixin:
    _open_connections_check_enable = True

    def _get_open_connections_count(self):
        return len(
            connections.all()
        )

    def setUp(self):
        super().setUp()
        self._connections_count = self._get_open_connections_count()

    def tearDown(self):
        if self._open_connections_check_enable:

            self.assertEqual(
                self._connections_count, self._get_open_connections_count(),
                msg='Database connection leak. The number of database '
                'connections at the start and at the end of the test '
                'are not the same.'
            )

        super().tearDown()


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


class ContentTypeTestCaseMixin:
    def _inject_test_object_content_type(self):
        self._test_object_content_type = ContentType.objects.get_for_model(
            model=self._test_object
        )

        self._test_object_view_kwargs = {
            'app_label': self._test_object_content_type.app_label,
            'model_name': self._test_object_content_type.model,
            'object_id': self._test_object.pk
        }


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


class ModelTestCaseMixin:
    def _model_instance_to_dictionary(self, instance):
        return instance._meta.model._default_manager.filter(
            pk=instance.pk
        ).values()[0]


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


class RandomPrimaryKeyModelMonkeyPatchMixin:
    random_primary_key_enable = True
    random_primary_key_maximum_attempts = 100
    random_primary_key_random_ceiling = 10000
    random_primary_key_random_floor = 100

    @staticmethod
    def get_unique_primary_key(model):
        manager = model._meta.default_manager

        attempts = 0
        while True:
            primary_key = random.randint(
                RandomPrimaryKeyModelMonkeyPatchMixin.random_primary_key_random_floor,
                RandomPrimaryKeyModelMonkeyPatchMixin.random_primary_key_random_ceiling
            )

            if not manager.filter(pk=primary_key).exists():
                break

            attempts += 1

            if attempts > RandomPrimaryKeyModelMonkeyPatchMixin.random_primary_key_maximum_attempts:
                raise ValueError(
                    'Maximum number of retries for an unique random primary '
                    'key reached.'
                )

        return primary_key

    @classmethod
    def setUpClass(cls):
        RandomSeedIdempotent.seed()
        super().setUpClass()

    def setUp(self):
        if self.random_primary_key_enable:
            self.method_original_save = models.Model.save

            def method_new_save(instance, *args, **kwargs):
                if instance.pk:
                    return self.method_original_save(
                        instance, *args, **kwargs
                    )
                else:
                    # Set meta.auto_created to True to have the original save_base
                    # not send the pre_save signal which would normally send
                    # the instance without a primary key. Since we assign a random
                    # primary key any pre_save signal handler that relies on an
                    # empty primary key will fail.
                    # The meta.auto_created and manual pre_save sending emulates
                    # the original behavior. Since meta.auto_created also disables
                    # the post_save signal we must also send it ourselves.
                    # This hack work with Django 1.11 .save_base() but can break
                    # in future versions if that method is updated.
                    pre_save.send(
                        sender=instance.__class__, instance=instance,
                        raw=False, update_fields=None
                    )
                    instance._meta.auto_created = True
                    instance.pk = RandomPrimaryKeyModelMonkeyPatchMixin.get_unique_primary_key(
                        model=instance._meta.model
                    )
                    instance.id = instance.pk

                    kwargs['force_insert'] = True

                    result = instance.save_base(*args, **kwargs)
                    instance._meta.auto_created = False

                    post_save.send(
                        created=True, instance=instance, raw=False,
                        sender=instance.__class__, update_fields=None
                    )

                    return result

            setattr(models.Model, 'save', method_new_save)

        super().setUp()

    def tearDown(self):
        if self.random_primary_key_enable:
            models.Model.save = self.method_original_save
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


class TestModelTestCaseMixin(ContentTypeTestCaseMixin, PermissionTestMixin):
    auto_create_test_object = False
    auto_create_test_object_fields = None
    auto_create_test_object_instance_kwargs = None
    auto_create_test_object_model = False
    auto_create_test_object_permission = False

    @staticmethod
    def _delete_test_model(model):
        ModelPermission.deregister(model=model)

        content_type = ContentType.objects.get_for_model(model=model)
        if content_type.pk:
            content_type.delete()

        # Only attempt to deleted if the model was not deleted as part
        # of the previous main test model deletion.
        if model in apps.all_models[model._meta.app_label] or model in apps.app_configs[model._meta.app_label].models:
            if not model._meta.proxy:
                with connection.schema_editor() as schema_editor:
                    schema_editor.delete_model(model=model)

        # Only attempt to delete if the model was not deleted as part
        # of the previous main test model deletion.
        TestModelTestCaseMixin._unregister_model(
            app_label=model._meta.app_label,
            model_name=model._meta.model_name
        )

        ContentType.objects.clear_cache()
        apps.clear_cache()

    @staticmethod
    def _unregister_model(app_label, model_name):
        try:
            del apps.all_models[app_label][model_name]
            del apps.app_configs[app_label].models[model_name]
        except KeyError:
            """
            Non fatal. Means the model was deleted in the first attempt.
            """

    @classmethod
    def setUpClass(cls):
        if connection.vendor == 'sqlite':
            connection.disable_constraint_checking()

        super().setUpClass()

    def _delete_test_models(self):
        # Delete the test models' content type entries and deregister the
        # permissions, this avoids their Content Type from being looked up
        # in subsequent tests where they don't exists due to the database
        # transaction rollback.

        # Clear previous model registration before re-registering it again to
        # avoid conflict with test models with the same name, in the same app
        # but from another test module.
        self._test_model_list.reverse()

        for model in self._test_model_list:
            model.objects.all().delete()

        for model in self._test_model_list:
            TestModelTestCaseMixin._delete_test_model(model=model)

        for model in self._test_model_list_extra:
            TestModelTestCaseMixin._delete_test_model(model=model)

    def setUp(self):
        self._test_model_list = []
        self._test_model_list_extra = set()
        self._test_object_list = []

        super().setUp()

        if self.auto_create_test_object or self.auto_create_test_object_model:
            self._TestModel = self._create_test_model(
                fields=self.auto_create_test_object_fields
            )

            if self.auto_create_test_object_permission:
                self._create_test_permission()

                ModelPermission.register(
                    model=self._TestModel, permissions=(
                        self._test_permission,
                    )
                )

        if self.auto_create_test_object:
            self._create_test_object(
                instance_kwargs=self.auto_create_test_object_instance_kwargs
            )

        self._create_test_models()

    def _create_test_models(self):
        """
        Optional test class method to have all of its test models created
        in the proper order.
        """

    def tearDown(self):
        self._delete_test_models()
        super().tearDown()

    def _create_test_model(
        self, base_class=None, fields=None, model_name=None,
        options=None
    ):
        base_class = base_class or models.Model
        test_model_count = len(self._test_model_list)
        self._test_model_name = model_name or '{}_{}'.format(
            '_TestModel', test_model_count
        )

        self.options = options
        # Obtain the app_config and app_label from the test's module path.
        self.app_config = apps.get_containing_app_config(
            object_name=self.__class__.__module__
        )

        if connection.vendor == 'mysql':
            self.skipTest(
                reason='MySQL doesn\'t support schema changes inside an '
                'atomic block.'
            )

        attrs = {
            '__module__': self.__class__.__module__,
            'Meta': self._get_test_model_meta()
        }

        if fields:
            attrs.update(fields)

        model_list_previous = set(
            apps.app_configs[self.app_config.label].models.values()
        )

        model = type(
            self._test_model_name, (base_class,), attrs
        )

        if not model._meta.proxy:
            with connection.schema_editor() as schema_editor:
                schema_editor.create_model(model=model)

        self._test_model_list_extra.update(
            set(
                apps.app_configs[self.app_config.label].models.values()
            ) - model_list_previous - {model}
        )

        self._test_model_list.append(model)

        ContentType.objects.clear_cache()
        apps.clear_cache()

        return model

    def _create_test_object(self, instance_kwargs=None):
        instance_kwargs = instance_kwargs or {}

        if not getattr(self, '_TestModel', None):
            self._TestModel = self._create_test_model()

        self._test_object = self._TestModel.objects.create(**instance_kwargs)
        self._inject_test_object_content_type()

        self._test_object_list.append(self._test_object)

    def _get_test_model_meta(self):
        self._test_db_table = '{}_{}'.format(
            self.app_config.label, self._test_model_name.lower()
        )

        class Meta:
            app_label = self.app_config.label
            db_table = self._test_db_table
            ordering = ('id',)
            verbose_name = self._test_model_name

        if self.options:
            for key, value in self.options.items():
                setattr(Meta, key, value)

        return Meta


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
