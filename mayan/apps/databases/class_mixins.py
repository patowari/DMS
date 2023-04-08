class DynamicFormBackendMixin:
    """
    The fields attribute is a list of dictionaries with the format:
    {
        'name': ''  # Field internal name
        'label': ''  # Label to show to users
        'initial': ''  # Field initial value
        'default': ''  # Default value.
    }
    """
    @classmethod
    def get_setup_form_field_order(cls):
        return getattr(
            cls, 'field_order', ()
        )

    @classmethod
    def get_setup_form_field_widgets(cls):
        return getattr(
            cls, 'widgets', {}
        )

    @classmethod
    def get_setup_form_fields(cls):
        return getattr(
            cls, 'fields', {}
        )

    @classmethod
    def get_setup_form_fieldsets(cls):
        return getattr(
            cls, 'fieldset', {}
        )

    @classmethod
    def get_setup_form_schema(cls):
        fields = cls.get_setup_form_fields()

        result = {
            'fields': fields,
            'widgets': cls.get_setup_form_field_widgets()
        }

        field_order = cls.get_setup_form_field_order() or tuple(
            fields.keys()
        )

        result['field_order'] = field_order

        return result
