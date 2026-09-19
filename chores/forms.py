from django import forms
from django.contrib.auth import get_user_model

from chores.models import Household, Task


class CreateHouseholdForm(forms.ModelForm):
    class Meta:
        model = Household
        fields = ('name',)
        labels = {'name': 'Nombre del hogar'}


class JoinHouseholdForm(forms.Form):
    access_code = forms.CharField(
        label='Código de acceso',
        max_length=12,
    )

    def clean_access_code(self):
        return self.cleaned_data['access_code'].strip().upper()


class CreateTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            'title',
            'description',
            'assignee',
            'due_date',
            'recurrence',
        )
        labels = {
            'title': 'Título',
            'description': 'Descripción',
            'assignee': 'Responsable',
            'due_date': 'Fecha de vencimiento',
            'recurrence': 'Repetición',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, household, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assignee'].queryset = get_user_model().objects.filter(
            membership__household=household,
        ).order_by('username')
