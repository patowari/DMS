from datetime import datetime

from mayan.apps.testing.tests.base import BaseTestCase

from .mixins import TemplateTestMixin


class TemplateTagDateParseTestCase(TemplateTestMixin, BaseTestCase):
    def test_basic_functionality(self):
        now = datetime.now()

        result = self._render_test_template(
            template_string='{{% set "{}"|date_parse as date_object %}}{{{{ date_object.year }}}}'.format(
                now.isoformat()
            )
        )
        self.assertEqual(
            result, str(now.year)
        )


class TemplateTagTimeDeltaTestCase(TemplateTestMixin, BaseTestCase):
    def test_basic_functionality(self):
        now = datetime.now()

        result = self._render_test_template(
            template_string='{{% set "{}"|date_parse as date_object %}}{{% timedelta date_object days=366 as date_new %}}{{{{ date_new.year }}}}'.format(
                now.isoformat()
            )
        )
        self.assertEqual(
            result, str(now.year + 1)
        )
