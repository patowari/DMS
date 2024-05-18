from mayan.apps.forms import forms

from .models import UserLocaleProfile


class LocaleProfileForm(forms.ModelForm):
    class Meta:
        fields = ('language', 'timezone')
        model = UserLocaleProfile
        widgets = {
            'language': forms.Select(
                attrs={
                    'class': 'select2'
                }
            ),
            'timezone': forms.Select(
                attrs={
                    'class': 'select2'
                }
            )
        }


class LocaleProfileForm_view(forms.DetailForm):
    class Meta:
        fields = ('language', 'timezone')
        model = UserLocaleProfile
