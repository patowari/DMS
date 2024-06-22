from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mayan.apps.views.model_mixins


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('views', '0001_initial')
    ]

    operations = [
        migrations.CreateModel(
            bases=(
                mayan.apps.views.model_mixins.ModelMixinUserViewModeBusinessLogic,
                models.Model
            ), fields=[
                (
                    'id', models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'app_label', models.CharField(
                        db_index=True, max_length=200,
                        verbose_name='App label'
                    )
                ),
                (
                    'name', models.CharField(
                        db_index=True, help_text='Full name of the view '
                        'including the namespace.', max_length=200,
                        verbose_name='Name'
                    )
                ),
                (
                    'value', models.CharField(
                        db_index=True, help_text='Stored value used to '
                        'identify the display mode of the view.',
                        max_length=4, verbose_name='Value'
                    )
                ),
                (
                    'user', models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='view_modes',
                        to=settings.AUTH_USER_MODEL, verbose_name='User'
                    )
                )
            ],
            name='UserViewMode', options={
                'verbose_name': 'User view mode',
                'verbose_name_plural': 'User view modes',
                'ordering': ('user__username', 'name'),
                'unique_together': {
                    ('user', 'name')
                }
            }
        ),
        migrations.DeleteModel(
            name='UserViewSettings'
        )
    ]
