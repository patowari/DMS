from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _

from mayan.apps.acls.classes import ModelPermission
from mayan.apps.acls.permissions import (
    permission_acl_edit, permission_acl_view
)
from mayan.apps.app_manager.apps import MayanAppConfig
from mayan.apps.common.classes import ModelCopy
from mayan.apps.common.menus import (
    menu_list_facet, menu_object, menu_return, menu_secondary, menu_setup,
    menu_topbar
)
from mayan.apps.events.classes import EventModelRegistry, ModelEventType
from mayan.apps.navigation.source_columns import SourceColumn

# ~ from .events import event_theme_edited, event_user_theme_settings_edited
# ~ from .handlers import handler_user_theme_setting_create
# ~ from .links import (
    # ~ link_ajax_refresh, link_theme_create, link_theme_delete, link_theme_edit,
    # ~ link_theme_list, link_theme_setup, link_user_theme_settings_detail,
    # ~ link_user_theme_settings_edit
# ~ )
# ~ from .permissions import (
    # ~ permission_theme_delete, permission_theme_edit, permission_theme_view
# ~ )


class AppearanceBootstrapApp(MayanAppConfig):
    app_namespace = 'appearance_bootstrap'
    app_url = 'appearance_bootstrap'
    #has_javascript_translations = True
    has_static_media = True
    #has_tests = True
    name = 'mayan.apps.appearance_bootstrap'
    static_media_ignore_patterns = (
        'appearance_bootstrap/node_modules/bootswatch/docs/*',
    )
    verbose_name = _(message='Appearance (Bootstrap)')

    # ~ def ready(self):
        # ~ super().ready()
