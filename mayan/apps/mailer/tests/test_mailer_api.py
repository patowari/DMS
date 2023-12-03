from rest_framework import status

from mayan.apps.rest_api.tests.base import BaseAPITestCase

from ..events import event_profile_created, event_profile_edited
from ..models import UserMailer
from ..permissions import (
    permission_user_mailer_create, permission_user_mailer_delete,
    permission_user_mailer_edit, permission_user_mailer_view
)

from .mixins import MailerAPIViewTestMixin


class MailerAPIViewTestCase(MailerAPIViewTestMixin, BaseAPITestCase):
    def test_mailer_create_api_view_no_permission(self):
        mailer_count = UserMailer.objects.count()

        self._clear_events()

        response = self._request_test_mailer_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(UserMailer.objects.count(), mailer_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_mailer_create_api_view_with_permission(self):
        self.grant_permission(permission=permission_user_mailer_create)

        mailer_count = UserMailer.objects.count()

        self._clear_events()

        response = self._request_test_mailer_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(UserMailer.objects.count(), mailer_count + 1)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_user_mailer)
        self.assertEqual(events[0].verb, event_profile_created.id)

    def test_mailer_delete_api_view_no_permission(self):
        self._create_test_user_mailer()

        mailer_count = UserMailer.objects.count()

        self._clear_events()

        response = self._request_test_mailer_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(UserMailer.objects.count(), mailer_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_mailer_delete_api_view_with_access(self):
        self._create_test_user_mailer()

        self.grant_access(
            obj=self._test_user_mailer,
            permission=permission_user_mailer_delete
        )

        mailer_count = UserMailer.objects.count()

        self._clear_events()

        response = self._request_test_mailer_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(UserMailer.objects.count(), mailer_count - 1)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_mailer_detail_api_view_no_permission(self):
        self._create_test_user_mailer()

        self._clear_events()

        response = self._request_test_mailer_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_mailer_detail_api_view_with_access(self):
        self._create_test_user_mailer()
        self.grant_access(
            obj=self._test_user_mailer,
            permission=permission_user_mailer_view
        )

        self._clear_events()

        response = self._request_test_mailer_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.data['label'], self._test_user_mailer.label
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_mailer_edit_api_view_via_patch_no_permission(self):
        self._create_test_user_mailer()

        mailer_label = self._test_user_mailer.label

        self._clear_events()

        response = self._request_test_mailer_edit_api_view(verb='patch')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self._test_user_mailer.refresh_from_db()
        self.assertEqual(self._test_user_mailer.label, mailer_label)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_mailer_edit_api_view_via_patch_with_access(self):
        self._create_test_user_mailer()

        self.grant_access(
            obj=self._test_user_mailer,
            permission=permission_user_mailer_edit
        )

        mailer_label = self._test_user_mailer.label

        self._clear_events()

        response = self._request_test_mailer_edit_api_view(verb='patch')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self._test_user_mailer.refresh_from_db()
        self.assertNotEqual(self._test_user_mailer.label, mailer_label)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_user_mailer)
        self.assertEqual(events[0].verb, event_profile_edited.id)

    def test_mailer_edit_api_view_via_put_no_permission(self):
        self._create_test_user_mailer()

        mailer_label = self._test_user_mailer.label

        self._clear_events()

        response = self._request_test_mailer_edit_api_view(verb='put')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self._test_user_mailer.refresh_from_db()
        self.assertEqual(self._test_user_mailer.label, mailer_label)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_mailer_edit_api_view_via_put_with_access(self):
        self._create_test_user_mailer()

        self.grant_access(
            obj=self._test_user_mailer,
            permission=permission_user_mailer_edit
        )

        mailer_label = self._test_user_mailer.label

        self._clear_events()

        response = self._request_test_mailer_edit_api_view(verb='put')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self._test_user_mailer.refresh_from_db()
        self.assertNotEqual(self._test_user_mailer.label, mailer_label)

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, None)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self._test_user_mailer)
        self.assertEqual(events[0].verb, event_profile_edited.id)

    def test_mailer_list_api_view_no_permission(self):
        self._create_test_user_mailer()

        self._clear_events()

        response = self._request_test_mailer_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_mailer_list_api_view_with_access(self):
        self._create_test_user_mailer()
        self.grant_access(
            obj=self._test_user_mailer,
            permission=permission_user_mailer_view
        )

        self._clear_events()

        response = self._request_test_mailer_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['label'],
            self._test_user_mailer.label
        )

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)
