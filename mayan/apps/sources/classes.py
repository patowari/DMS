import logging

from django.utils.translation import ugettext_lazy as _

from mayan.apps.backends.class_mixins import DynamicFormBackendMixin
from mayan.apps.backends.classes import ModelBaseBackend
from mayan.apps.common.class_mixins import AppsModuleLoaderMixin

from .exceptions import SourceActionExceptionUnknown

logger = logging.getLogger(name=__name__)


class DocumentCreateWizardStep(AppsModuleLoaderMixin):
    _deregistry = {}
    _loader_module_name = 'wizard_steps'
    _registry = {}

    @classmethod
    def deregister(cls, step):
        cls._deregistry[step.name] = step

    @classmethod
    def deregister_all(cls):
        for step in cls.get_all():
            cls.deregister(step=step)

    @classmethod
    def done(cls, wizard):
        return {}

    @classmethod
    def get(cls, name):
        for step in cls.get_all():
            if name == step.name:
                return step

    @classmethod
    def get_all(cls):
        return sorted(
            (
                step for step in cls._registry.values() if step.name not in cls._deregistry
            ), key=lambda x: x.number
        )

    @classmethod
    def get_choices(cls, attribute_name):
        return [
            (
                step.name, getattr(step, attribute_name)
            ) for step in cls.get_all()
        ]

    @classmethod
    def get_form_initial(cls, wizard):
        return {}

    @classmethod
    def get_form_kwargs(cls, wizard):
        return {}

    @classmethod
    def post_upload_process(
        cls, document, query_string, source_id, user_id
    ):
        for step in cls.get_all():
            step.step_post_upload_process(
                document=document, query_string=query_string,
                source_id=source_id, user_id=user_id
            )

    @classmethod
    def register(cls, step):
        if step.name in cls._registry:
            raise Exception(
                'A step with this name already exists: %s' % step.name
            )

        if step.number in [reigstered_step.number for reigstered_step in cls.get_all()]:
            raise Exception(
                'A step with this number already exists: %s' % step.name
            )

        cls._registry[step.name] = step

    @classmethod
    def reregister(cls, name):
        cls._deregistry.pop(name)

    @classmethod
    def reregister_all(cls):
        cls._deregistry = {}

    @classmethod
    def step_post_upload_process(
        cls, document, query_string, source_id, user_id
    ):
        """
        Optional method executed when the wizard ends to allow the step to
        perform its action.
        """


class SourceBackend(DynamicFormBackendMixin, ModelBaseBackend):
    """
    Base class for the source backends.
    """
    _backend_app_label = 'sources'
    _backend_model_name = 'Source'
    _loader_module_name = 'source_backends'
    action_class_list = None

    @classmethod
    def get_form_fieldsets(cls):
        fieldsets = (
            (
                _('General'), {
                    'fields': ('label', 'enabled')
                }
            ),
        )

        return fieldsets

    @classmethod
    def get_upload_form_class(cls):
        return getattr(cls, 'upload_form_class', None)

    @classmethod
    def intialize(cls):
        """
        Optional method for subclasses execute their own initialization
        code.
        """

    @classmethod
    def post_load_modules(cls):
        for source_backend in cls.get_all():
            source_backend.intialize()

    def callback_post_document_file_upload(self, document_file, **kwargs):
        """
        Callback to execute when a document file is fully uploaded.
        """
        return

    def callback_post_document_create(self, document, **kwargs):
        """
        Callback to execute when a document is created.
        """
        return

    def clean(self):
        """
        Optional method to validate backend data before saving.
        """

    def create(self):
        """
        Called after the source model's .save() method for new
        instances.
        """

    def delete(self):
        """
        Called before the source model's .delete() method.
        """

    def get_action(self, name):
        for entry in self.get_action_list():
            if entry.name == name:
                return entry

        raise SourceActionExceptionUnknown(
            'Unknown action `{}` for source `{}`.'.format(
                name, self.get_model_instance()
            )
        )

    def get_action_class_list(self):
        """
        Returns the non initialized list of action classes. This is to allow
        mixins to add their own actions to a base source backend class.
        """
        return self.action_class_list or ()

    def get_action_list(self):
        action_class_list = self.get_action_class_list() or ()

        source = self.get_model_instance()

        for action_class in action_class_list:
            yield action_class(source=source)

    def save(self):
        """
        Called after the source model's .save() method for existing
        instances.
        """


class SourceBackendNull(SourceBackend):
    label = _('Null backend')
