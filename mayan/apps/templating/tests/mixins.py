from mayan.apps.databases.tests.mixins import ContentTypeTestCaseMixin

from ..classes import Template

from .literals import TEST_TEMPLATE


class ObjectTemplateSandboxViewTestMixin(ContentTypeTestCaseMixin):
    def _request_object_template_sandbox_get_view(self):
        return self.get(
            kwargs=self._test_object_view_kwargs,
            viewname='templating:object_template_sandbox'
        )

    def _request_object_template_sandbox_post_view(self):
        return self.post(
            data={'template_template': TEST_TEMPLATE},
            kwargs=self._test_object_view_kwargs,
            viewname='templating:object_template_sandbox'
        )


class TemplateTestMixin:
    def _render_test_template(self, template_string, context=None):
        template = Template(template_string=template_string)
        return template.render(context=context)
