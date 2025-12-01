from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='HankoUserMapping',
            fields=[
                ('hanko_user_id', models.CharField(
                    help_text='Hanko user UUID from JWT',
                    max_length=255,
                    primary_key=True,
                    serialize=False,
                )),
                ('app_user_id', models.CharField(
                    help_text='Application user ID',
                    max_length=255,
                )),
                ('app_name', models.CharField(
                    default='default',
                    help_text='Application name for multi-app deployments',
                    max_length=255,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(
                    auto_now=True,
                    null=True,
                    blank=True,
                )),
            ],
            options={
                'db_table': 'hanko_user_mappings',
            },
        ),
        migrations.AddConstraint(
            model_name='hankousermapping',
            constraint=models.UniqueConstraint(
                fields=('hanko_user_id', 'app_name'),
                name='uq_hanko_app',
            ),
        ),
        migrations.AddIndex(
            model_name='hankousermapping',
            index=models.Index(
                fields=['app_user_id', 'app_name'],
                name='idx_app_user_id',
            ),
        ),
    ]
