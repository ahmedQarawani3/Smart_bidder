# Generated by Django 5.2.1 on 2025-06-14 10:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investor', '0004_negotiation_is_read'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='negotiation',
            name='investor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='investor_negotiations', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
