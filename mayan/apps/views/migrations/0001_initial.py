from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL)
    ]

    operations = [
        migrations.CreateModel(
            fields=[
                (
                    'id', models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'view_name', models.CharField(
                        db_index=True, max_length=200, verbose_name='Name'
                    )
                ),
                (
                    'mode', models.CharField(
                        max_length=4, verbose_name='Mode'
                    )
                ),
                (
                    'user', models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='view_settings',
                        to=settings.AUTH_USER_MODEL, verbose_name='User'
                    )
                )
            ], name='UserViewSettings', options={
                'verbose_name': 'User view configuration',
                'verbose_name_plural': 'User view configurations',
                'ordering': ('user__username',)
            }
        )
    ]
