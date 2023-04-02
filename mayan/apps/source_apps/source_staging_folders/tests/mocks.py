from .literals import TEST_STAGING_PREVIEW_WIDTH


class MockStagingFolder:
    """Mock of a StagingFolder model."""
    kwargs = {
        'preview_height': None,
        'preview_width': TEST_STAGING_PREVIEW_WIDTH
    }
    model_instance_id = 1
    pk = 1
