from django import forms

class NameForm(forms.Form):
    name=forms.CharField(label='name',max_length=100)
    rollnumber = forms.CharField(label='roll', max_length=100)
    email = forms.CharField(label='email', max_length=100)
    Password= forms.CharField(label='pass', max_length=100)