from django import forms
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Task, UserProfile

DATETIME_LOCAL_FORMAT = '%Y-%m-%dT%H:%M'


class TaskCreateForm(forms.ModelForm):
    assign_to = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        empty_label='— Leave unassigned —',
        label='Assign to',
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'due_date', 'assign_to']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'What needs to be done?',
                'autofocus': True,
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Optional details…',
                'rows': 3,
            }),
            'due_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format=DATETIME_LOCAL_FORMAT,
            ),
        }
        labels = {
            'title': 'Task title',
            'description': 'Description',
            'priority': 'Priority',
            'due_date': 'Due date & time',
        }

    def __init__(self, *args, organization=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.organization = organization
        if organization is not None:
            self.fields['assign_to'].queryset = (
                User.objects
                .filter(
                    organization_membership__organization=organization,
                    is_active=True,
                )
                .order_by('first_name', 'username')
            )
        self.fields['due_date'].required = False
        self.fields['due_date'].input_formats = [
            DATETIME_LOCAL_FORMAT,
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
        ]
        self.fields['assign_to'].label_from_instance = lambda u: (
            u.get_full_name() or u.username
        )
        if self.instance and self.instance.pk and self.instance.due_date:
            local_due = timezone.localtime(self.instance.due_date)
            self.initial.setdefault(
                'due_date',
                local_due.strftime(DATETIME_LOCAL_FORMAT),
            )


class InviteMemberForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. juan', 'autofocus': True}),
    )
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, initial='member')
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Temporary password'}),
        min_length=6,
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username


class RegisterForm(forms.Form):
    organization_name = forms.CharField(
        max_length=200,
        label='Organization name',
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Acme Station'}),
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Choose a username'}),
    )
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Create a password'}),
        min_length=6,
    )
    password2 = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repeat your password'}),
    )

    def clean_organization_name(self):
        name = self.cleaned_data['organization_name'].strip()
        if not name:
            raise forms.ValidationError('Organization name is required.')
        return name

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned


class ProfileSettingsForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        required=False,
        label='First name',
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label='Last name',
    )
    avatar_initials = forms.CharField(
        max_length=2,
        required=False,
        label='Avatar initials',
        help_text='Optional. Leave blank to use your name initials.',
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. JD',
            'maxlength': '2',
            'style': 'text-transform: uppercase;',
        }),
    )

    def __init__(self, *args, user=None, profile=None, **kwargs):
        self.user = user
        self.profile = profile
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
        if profile is not None:
            self.fields['avatar_initials'].initial = profile.avatar_initials

    def clean_avatar_initials(self):
        value = self.cleaned_data.get('avatar_initials', '').strip().upper()
        if value and not value.isalnum():
            raise forms.ValidationError('Use letters or numbers only.')
        return value

    def save(self):
        self.user.first_name = self.cleaned_data['first_name'].strip()
        self.user.last_name = self.cleaned_data['last_name'].strip()
        self.user.save(update_fields=['first_name', 'last_name'])
        self.profile.avatar_initials = self.cleaned_data['avatar_initials']
        self.profile.save(update_fields=['avatar_initials'])
