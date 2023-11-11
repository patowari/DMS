from django.urls import re_path

from .views import (
    SettingEditView, SettingNamespaceDetailView, SettingNamespaceListView
)

urlpatterns = [
    re_path(
        route=r'^namespaces/settings/(?P<setting_global_name>\w+)/edit/$',
        name='setting_edit_view', view=SettingEditView.as_view()
    ),
    re_path(
        route=r'^namespaces/$', name='setting_namespace_list',
        view=SettingNamespaceListView.as_view()
    ),
    re_path(
        route=r'^namespaces/(?P<namespace_name>\w+)/$',
        name='setting_namespace_detail',
        view=SettingNamespaceDetailView.as_view()
    )
]
