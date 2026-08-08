from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('owner', 'Owner'),
    )

    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta(UserCreationForm.Meta):
         model = User
         fields = UserCreationForm.Meta.fields + ('role',)