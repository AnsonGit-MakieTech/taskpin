from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_alter_activitylog_task'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='avatar_initials',
            field=models.CharField(
                blank=True,
                help_text='Optional override for avatar initials (max 2 characters).',
                max_length=2,
            ),
        ),
    ]
