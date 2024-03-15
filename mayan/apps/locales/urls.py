from django.conf.urls import url

from .views import (
    JavaScriptCatalogPublic, UserLocaleProfileDetailView,
    UserLocaleProfileEditView
)

urlpatterns = [
    url(
        regex=r'^jsi18n/$', name='javascript_catalog',
        view=JavaScriptCatalogPublic.as_view()
    ),
    url(
        regex=r'^jsi18n/(?P<packages>\S+?)/$', name='javascript_catalog',
        view=JavaScriptCatalogPublic.as_view()
    ),
    url(
        regex=r'^user/(?P<user_id>\d+)/locale/$',
        name='user_locale_profile_detail',
        view=UserLocaleProfileDetailView.as_view()
    ),
    url(
        regex=r'^user/(?P<user_id>\d+)/locale/edit/$',
        name='user_locale_profile_edit',
        view=UserLocaleProfileEditView.as_view()
    )
]
