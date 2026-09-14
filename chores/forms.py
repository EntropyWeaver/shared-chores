from django import forms

from chores.models import Household


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
