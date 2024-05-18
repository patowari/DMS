from mayan.apps.forms import form_widgets, forms

from .models import Comment


class DocumentCommentDetailForm(forms.DetailForm):

    class Meta:
        fields = ('text',)
        extra_fields = (
            {'field': 'submit_date', 'widget': form_widgets.DateTimeInput},
            {'field': 'user'}
        )
        model = Comment
