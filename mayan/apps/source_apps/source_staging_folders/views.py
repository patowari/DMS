from django.views.generic.list import MultipleObjectMixin

from mayan.apps.views.settings import setting_paginate_by


class SourceBackendStagingSourceFileListView(MultipleObjectMixin):
    def get_paginate_by(self, queryset):
        return setting_paginate_by.value
