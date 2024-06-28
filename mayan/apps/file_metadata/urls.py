from django.urls import re_path

from .views.document_file_views import (
    DocumentFileMetadataDriverAttributeListView,
    DocumentFileMetadataDriverListView, DocumentFileMetadataSubmitView
)
from .views.document_type_views import (
    DocumentTypeFileMetadataDriverConfigurationEditView,
    DocumentTypeFileMetadataDriverConfigurationListView,
    DocumentTypeFileMetadataSubmitView,
)
from .views.tool_views import FileMetadataDriverListView

urlpatterns_document_types = [
    re_path(
        route=r'^document_types/(?P<document_type_id>\d+)/file_metadata/drivers/$',
        name='document_type_file_metadata_driver_configuration_list',
        view=DocumentTypeFileMetadataDriverConfigurationListView.as_view()
    ),
    re_path(
        route=r'^document_types/(?P<document_type_id>\d+)/file_metadata/drivers/(?P<stored_driver_id>\d+)/edit/$',
        name='document_type_file_metadata_driver_configuration_edit',
        view=DocumentTypeFileMetadataDriverConfigurationEditView.as_view()
    ),
    re_path(
        route=r'^document_types/submit/$',
        name='document_type_file_metadata_submit',
        view=DocumentTypeFileMetadataSubmitView.as_view()
    )
]

urlpatterns_documents = [
    re_path(
        route=r'^documents/files/drivers/(?P<document_file_driver_id>\d+)/attributes/$',
        name='document_file_metadata_driver_attribute_list',
        view=DocumentFileMetadataDriverAttributeListView.as_view()
    ),
    re_path(
        route=r'^documents/files/(?P<document_file_id>\d+)/drivers/$',
        name='document_file_metadata_driver_list',
        view=DocumentFileMetadataDriverListView.as_view()
    ),
    re_path(
        route=r'^documents/files/(?P<document_file_id>\d+)/submit/$',
        name='document_file_metadata_single_submit',
        view=DocumentFileMetadataSubmitView.as_view()
    ),
    re_path(
        route=r'^documents/files/multiple/submit/$',
        name='document_file_metadata_multiple_submit',
        view=DocumentFileMetadataSubmitView.as_view()
    )
]

urlpatterns_drivers = [
    re_path(
        route=r'^driver/list/$', name='file_metadata_driver_list',
        view=FileMetadataDriverListView.as_view()
    )
]

urlpatterns = []
urlpatterns.extend(urlpatterns_document_types)
urlpatterns.extend(urlpatterns_documents)
urlpatterns.extend(urlpatterns_drivers)
