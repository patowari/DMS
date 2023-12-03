from mayan.apps.rest_api import generics

from .models import UserMailer
from .permissions import (
    permission_user_mailer_create, permission_user_mailer_delete,
    permission_user_mailer_edit, permission_user_mailer_view
)
from .serializers import UserMailerSerializer


class APIUserMailerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    delete: Delete the selected mailer.
    get: Return the details of the selected mailer.
    patch: Edit the selected mailer.
    put: Edit the selected mailer.
    """
    lookup_url_kwarg = 'mailer_id'
    mayan_object_permissions = {
        'DELETE': (permission_user_mailer_delete,),
        'GET': (permission_user_mailer_view,),
        'PATCH': (permission_user_mailer_edit,),
        'PUT': (permission_user_mailer_edit,)
    }
    serializer_class = UserMailerSerializer
    source_queryset = UserMailer.objects.all()

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user
        }


class APIUserMailerListView(generics.ListCreateAPIView):
    """
    get: Returns a list of all the mailers.
    post: Create a new mailer.
    """
    mayan_object_permissions = {
        'GET': (permission_user_mailer_view,)
    }
    mayan_view_permissions = {
        'POST': (permission_user_mailer_create,)
    }
    ordering_fields = ('default', 'enabled', 'id', 'label')
    serializer_class = UserMailerSerializer
    source_queryset = UserMailer.objects.all()

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user
        }
