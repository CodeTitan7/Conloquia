# Generated by Django 5.0.7 on 2024-08-08 18:28

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailer', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='email',
            name='timestamp',
        ),
        migrations.AddField(
            model_name='email',
            name='category',
            field=models.CharField(choices=[('inbox', 'Inbox'), ('sent', 'Sent'), ('draft', 'Draft'), ('trash', 'Trash')], default='inbox', max_length=20),
        ),
        migrations.AddField(
            model_name='email',
            name='sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='email',
            name='starred',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='email',
            name='subject',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='email',
            name='tracking_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='emailtracking',
            name='email',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='mailer.email'),
        ),
        migrations.AddIndex(
            model_name='email',
            index=models.Index(fields=['recipient'], name='mailer_emai_recipie_d5ee24_idx'),
        ),
        migrations.AddIndex(
            model_name='email',
            index=models.Index(fields=['sent_at'], name='mailer_emai_sent_at_887421_idx'),
        ),
    ]
