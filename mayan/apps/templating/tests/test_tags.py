from mayan.apps.testing.tests.base import BaseTestCase

from .literals import TEST_TEMPLATE_TAG_RESULT
from .mixins import TemplateTestMixin


class TemplateFilterDictGetTestCase(TemplateTestMixin, BaseTestCase):
    def test_filter_dict_get_valid(self):
        result = self._render_test_template(
            template_string='{{ dict|dict_get:1 }}', context={
                'dict': {1: 'a'}
            }
        )
        self.assertEqual(result, 'a')

    def test_filter_dict_get_invalid(self):
        result = self._render_test_template(
            template_string='{{ dict|dict_get:2 }}', context={
                'dict': {1: 'a'}
            }
        )
        self.assertEqual(result, '')


class TemplateFilterSplitTestCase(TemplateTestMixin, BaseTestCase):
    def test_filter_split_valid(self):
        result = self._render_test_template(
            template_string='{% with x|split:"," as result %}{{ result.0 }}-{{ result.1 }}-{{ result.2 }}{% endwith %}', context={'x': '1,2,3'}
        )
        self.assertEqual(result, '1-2-3')


class TemplateTagLoadingTestCase(TemplateTestMixin, BaseTestCase):
    def test_user_template_tag_loading(self):
        result = self._render_test_template(
            template_string='{% load templating_test_tags %}{% templating_test_tag %}'
        )
        self.assertEqual(result, TEST_TEMPLATE_TAG_RESULT)


class TemplateTagSetTestCase(TemplateTestMixin, BaseTestCase):
    def test_tag_set_string(self):
        result = self._render_test_template(
            template_string='{% set "string" as result %}{{ result }}'
        )
        self.assertEqual(result, 'string')

    def test_tag_set_number(self):
        result = self._render_test_template(
            template_string='{% set 99 as result %}{{ result }}'
        )
        self.assertEqual(result, '99')

    def test_tag_set_logical(self):
        result = self._render_test_template(
            template_string='{% set True as result %}{{ result }}'
        )
        self.assertEqual(result, 'True')

    def test_tag_set_nonexistant(self):
        result = self._render_test_template(
            template_string='{% set nonexistent as result %}{{ result }}'
        )
        self.assertEqual(result, '')
