from django import forms
from django.contrib.auth.models import User

from .models import Task


class TaskCreateForm(forms.ModelForm):
    assign_to = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('first_name', 'username'),
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
            'due_date': forms.DateInput(attrs={
                'type': 'date',
            }),
        }
        labels = {
            'title': 'Task title',
            'description': 'Description',
            'priority': 'Priority',
            'due_date': 'Due date',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show full name in the assign_to dropdown when available
        self.fields['assign_to'].label_from_instance = lambda u: (
            u.get_full_name() or u.username
        )
