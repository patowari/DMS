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


class IconsApp(MayanAppConfig):
    app_namespace = 'icons'
    app_url = 'icons'
    has_static_media = True
    has_tests = True
    name = 'mayan.apps.icons'
    static_media_ignore_patterns = (
        'icons/node_modules/@fortawesome/fontawesome-free/less/*',
        'icons/node_modules/@fortawesome/fontawesome-free/metadata/*',
        'icons/node_modules/@fortawesome/fontawesome-free/sprites/*',
        'icons/node_modules/@fortawesome/fontawesome-free/svgs/*',
    )
    verbose_name = _(message='Icons')
