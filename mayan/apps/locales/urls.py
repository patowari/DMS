from django.urls import re_path
from django.views.i18n import JavaScriptCatalog

from .views import UserLocaleProfileDetailView, UserLocaleProfileEditView

urlpatterns = [
    re_path(
        route=r'^jsi18n/$', name='javascript_catalog',
        view=JavaScriptCatalog.as_view()
    ),
    re_path(
        route=r'^jsi18n/(?P<packages>\S+?)/$', name='javascript_catalog',
        view=JavaScriptCatalog.as_view()
    ),
    re_path(
        route=r'^user/(?P<user_id>\d+)/locale/$',
        name='user_locale_profile_detail',
        view=UserLocaleProfileDetailView.as_view()
    ),
    re_path(
        route=r'^user/(?P<user_id>\d+)/locale/edit/$',
        name='user_locale_profile_edit',
        view=UserLocaleProfileEditView.as_view()
    )
]
