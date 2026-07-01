from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_userprofile_avatar_initials'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='due_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
