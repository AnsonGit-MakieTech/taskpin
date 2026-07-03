from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_alter_task_due_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='completion_remarks',
            field=models.TextField(
                blank=True,
                help_text='Optional notes added when the task was marked done.',
            ),
        ),
    ]
