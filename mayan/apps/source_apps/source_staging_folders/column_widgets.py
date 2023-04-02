from mayan.apps.documents.column_widgets import ThumbnailWidget


class StagingSourceFileThumbnailWidget(ThumbnailWidget):
    gallery_name = 'sources:staging_source_file_list'

    def disable_condition(self, instance):
        return True
