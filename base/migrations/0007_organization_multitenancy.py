# Generated manually for organization multi-tenancy

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def forwards_populate_organizations(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Organization = apps.get_model('base', 'Organization')
    OrganizationMembership = apps.get_model('base', 'OrganizationMembership')
    UserProfile = apps.get_model('base', 'UserProfile')
    Task = apps.get_model('base', 'Task')
    ActivityLog = apps.get_model('base', 'ActivityLog')
    Conversation = apps.get_model('base', 'Conversation')

    default_org, _ = Organization.objects.get_or_create(
        slug='default',
        defaults={'name': 'Default Organization'},
    )
    if default_org.created_by_id is None:
        first_user = User.objects.order_by('pk').first()
        if first_user:
            default_org.created_by = first_user
            default_org.save(update_fields=['created_by'])

    for user in User.objects.all():
        profile = UserProfile.objects.filter(user=user).first()
        role = profile.role if profile else 'member'
        OrganizationMembership.objects.get_or_create(
            user=user,
            defaults={
                'organization': default_org,
                'role': role,
            },
        )

    Task.objects.filter(organization__isnull=True).update(organization=default_org)
    ActivityLog.objects.filter(organization__isnull=True).update(organization=default_org)
    Conversation.objects.filter(organization__isnull=True).update(organization=default_org)


def backwards_clear_organizations(apps, schema_editor):
    OrganizationMembership = apps.get_model('base', 'OrganizationMembership')
    OrganizationMembership.objects.all().delete()
    Organization = apps.get_model('base', 'Organization')
    Organization.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_conversation_message_conversationparticipant'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=220, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='created_organizations', to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='OrganizationMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(
                    choices=[('admin', 'Admin'), ('member', 'Member')],
                    default='member', max_length=10,
                )),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('organization', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='memberships', to='base.organization',
                )),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='organization_membership', to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={'ordering': ['joined_at']},
        ),
        migrations.RemoveConstraint(
            model_name='conversation',
            name='unique_team_conversation',
        ),
        migrations.AddField(
            model_name='task',
            name='organization',
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name='tasks', to='base.organization',
            ),
        ),
        migrations.AddField(
            model_name='activitylog',
            name='organization',
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name='activity_logs', to='base.organization',
            ),
        ),
        migrations.AddField(
            model_name='conversation',
            name='organization',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name='conversations', to='base.organization',
            ),
        ),
        migrations.RunPython(forwards_populate_organizations, backwards_clear_organizations),
        migrations.AlterField(
            model_name='task',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='tasks', to='base.organization',
            ),
        ),
        migrations.AlterField(
            model_name='activitylog',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='activity_logs', to='base.organization',
            ),
        ),
        migrations.AlterField(
            model_name='conversation',
            name='organization',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='conversations', to='base.organization',
            ),
        ),
        migrations.AddConstraint(
            model_name='conversation',
            constraint=models.UniqueConstraint(
                condition=models.Q(('conversation_type', 'team')),
                fields=('organization', 'conversation_type'),
                name='unique_team_conversation_per_org',
            ),
        ),
    ]
