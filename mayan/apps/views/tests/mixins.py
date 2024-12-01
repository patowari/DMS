from django.urls import resolve, reverse

from ..models import UserConfirmView


class UserConfirmViewPropertyTestMixin:
    _auto_create_test_user_confirm_view_property = True
    _test_user_confirm_view_property_kwargs = {'user_confirmation_view_id': 1}
    _test_user_confirm_view_property_viewname = 'views:user_views_confirm_delete_single'

    def setUp(self):
        super().setUp()

        if self._auto_create_test_user_confirm_view_property:
            self._create_test_user_confirm_view_property()

    def _create_test_user_confirm_view_property(self):
        path = reverse(
            kwargs=self._test_user_confirm_view_property_kwargs,
            viewname=self._test_user_confirm_view_property_viewname
        )

        resolver_match = resolve(path=path)

        view_name = '{}:{}'.format(
            resolver_match.namespace, resolver_match.url_name
        )

        self._test_confirm_view, created = UserConfirmView.objects.update_or_create(
            defaults={
                'namespace': resolver_match.namespace,
                'remember': True
            }, name=view_name, user=self._test_case_user
        )


class UserConfirmViewPropertyViewTestMixin(UserConfirmViewPropertyTestMixin):
    def _request_user_confirm_property_delete_view(self, remember=None):
        return self.post(
            kwargs={'user_confirmation_view_id': self._test_confirm_view.pk},
            viewname='views:user_views_confirm_delete_single'
        )

    def _request_user_confirm_property_list_view(self):
        return self.get(
            kwargs={'user_id': self._test_case_user.pk},
            viewname='views:user_views_confirm_list'
        )


class UserViewModeViewTestMixin:
    def _request_test_current_user_view_modes_view(self):
        return self._request_test_user_view_modes_view(
            user=self._test_case_user
        )

    def _request_test_super_user_view_modes_view(self):
        return self._request_test_user_view_modes_view(
            user=self._test_super_user
        )

    def _request_test_user_view_modes_view(self, user=None):
        user = user or self._test_user

        return self.get(
            viewname='views:user_view_modes', kwargs={'user_id': user.pk}
        )
