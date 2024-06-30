from django import forms

from . import models


class AddAccountForm(forms.ModelForm):
    class Meta:
        model = models.Account
        fields = ["platform", "email"]
