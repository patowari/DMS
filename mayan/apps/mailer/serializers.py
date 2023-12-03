from django.utils.translation import gettext_lazy as _

from mayan.apps.rest_api import serializers

from .models import UserMailer


class UserMailerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        extra_kwargs = {
            'url': {
                'label': _(message='URL'),
                'lookup_url_kwarg': 'mailer_id',
                'view_name': 'rest_api:mailer-detail'
            }
        }
        fields = (
            'backend_data', 'backend_path', 'default', 'enabled', 'id',
            'label', 'url'
        )
        model = UserMailer
