from mayan.apps.testing.tests.base import GenericViewTestCase
from mayan.apps.user_management.permissions import permission_user_view

from .mixins import UserViewModeViewTestMixin


class CurrentUserViewTestCase(
    UserViewModeViewTestMixin, GenericViewTestCase
):
    def test_current_user_view_modes_view_no_permission(self):
        self._clear_events()

        response = self._request_test_current_user_view_modes_view()
        self.assertEqual(response.status_code, 200)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)


class SuperUserThemeSettingsViewTestCase(
    UserViewModeViewTestMixin, GenericViewTestCase
):
    def setUp(self):
        super().setUp()
        self._create_test_super_user()

    def test_super_user_view_modes_view_no_permission(self):
        self._clear_events()

        response = self._request_test_super_user_view_modes_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_super_user_view_modes_view_with_access(self):
        self.grant_access(
            obj=self._test_super_user, permission=permission_user_view
        )

        self._clear_events()

        response = self._request_test_super_user_view_modes_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)


class UserThemeSettingsViewTestCase(
    UserViewModeViewTestMixin, GenericViewTestCase
):
    auto_create_test_user = True

    def test_user_view_modes_view_no_permission(self):
        self._clear_events()

        response = self._request_test_user_view_modes_view()
        self.assertEqual(response.status_code, 404)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_user_view_modes_view_with_access(self):
        self.grant_access(
            obj=self._test_user, permission=permission_user_view
        )

        self._clear_events()

        response = self._request_test_user_view_modes_view()
        self.assertEqual(response.status_code, 200)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)
