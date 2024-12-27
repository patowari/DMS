import html

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


class TemplateFilterDictionaryFlattenTestCase(TemplateTestMixin, BaseTestCase):
    def test_template_filter(self):
        test_dictionary_source = {'a': 1, 'b': 2, 'c': {'d': 3}}
        test_dictionary_result = {'a': 1, 'b': 2, 'c__d': 3}

        result = self._render_test_template(
            template_string='{{ dict|dictionary_flatten }}', context={
                'dict': test_dictionary_source
            }
        )
        self.assertEqual(
            result, html.escape(
                str(test_dictionary_result)
            )
        )


class TemplateFilterObjectFlattenTestCase(TemplateTestMixin, BaseTestCase):
    def test_template_dictionary(self):
        test_obj = {
            'a': {
                'b': [1, 2, {'c': 3}],
                'd': 4
            },
            'e': 5,
            'f': [
                {'g': 6},
                {'h': {'i': 7}}
            ],
            'j': {'k': {'l': 8, 'm': 9}}
        }
        test_result = {
            'a__b__0': 1,
            'a__b__1': 2,
            'a__b__2__c': 3,
            'a__d': 4,
            'e': 5,
            'f__0__g': 6,
            'f__1__h__i': 7,
            'j__k__l': 8,
            'j__k__m': 9
        }

        result = self._render_test_template(
            template_string='{{ obj|object_flatten }}', context={
                'obj': test_obj
            }
        )
        self.assertEqual(
            result, html.escape(
                str(test_result)
            )
        )

    def test_template_list(self):
        test_obj = [
            {
                'a': {
                    'b': [1, 2, {'c': 3}],
                    'd': 4
                },
                'e': 5,
                'f': [
                    {'g': 6},
                    {'h': {'i': 7}}
                ],
                'j': {'k': {'l': 8, 'm': 9}}
            }
        ]
        test_result = {
            '0__a__b__0': 1,
            '0__a__b__1': 2,
            '0__a__b__2__c': 3,
            '0__a__d': 4,
            '0__e': 5,
            '0__f__0__g': 6,
            '0__f__1__h__i': 7,
            '0__j__k__l': 8,
            '0__j__k__m': 9
        }

        result = self._render_test_template(
            template_string='{{ obj|object_flatten }}', context={
                'obj': test_obj
            }
        )
        self.assertEqual(
            result, html.escape(
                str(test_result)
            )
        )


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
