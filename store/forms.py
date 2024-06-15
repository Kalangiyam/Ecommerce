
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User

class UserRegisterForm(UserCreationForm):
    
    email = forms.EmailField()
    class meta:
        model = User,
        fields = ['username','email','password1','password2']

    

