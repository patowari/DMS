from django.utils.translation import gettext_lazy as _

from mayan.apps.navigation.menus import Menu

menu_sources = Menu(
    label=_(message='Sources'), name='sources'
)
