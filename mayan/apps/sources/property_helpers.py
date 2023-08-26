from mayan.apps.common.classes import PropertyHelper


class DocumentSourceMetadataHelper(PropertyHelper):
    @staticmethod
    @property
    def constructor(*args, **kwargs):
        return DocumentSourceMetadataHelper(*args, **kwargs)

    def get_result(self, name):
        return self.instance.file_latest.source_metadata.get(key=name).value


class DocumentFileSourceMetadataHelper(PropertyHelper):
    @staticmethod
    @property
    def constructor(*args, **kwargs):
        return DocumentFileSourceMetadataHelper(*args, **kwargs)

    def get_result(self, name):
        return self.instance.source_metadata.get(key=name).value
