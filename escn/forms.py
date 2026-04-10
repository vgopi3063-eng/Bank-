from django import forms
from .models import Account

class RegisterationForm(forms.ModelForm):
    class Meta:
        model=Account
        fields='__all__'
        exclude=['pin','balance']