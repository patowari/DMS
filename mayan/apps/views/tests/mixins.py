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
