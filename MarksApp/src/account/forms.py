from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate

from account.models import Account

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=60, help_text='Required. Add a valid email address.')

    class Meta:
        model = Account
        fields = ("email", "username", "password1", "password2")


class AccountAuthenticationForm(forms.ModelForm):

    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ('email', 'password')

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email, password=password):
                raise forms.ValidationError("Invalid Login")
            

class AccountUpdateForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = ('subject', 'term', 'crn')

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        if email:
            account = Account.objects.get(email=email)
            account.subject = cleaned_data.get('subject')
            account.term = cleaned_data.get('term')
            account.crn = cleaned_data.get('crn')
            account.save()

        return cleaned_data

    # def clean_subject(self):
    #     if self.is_valid():
    #         email = self.cleaned_data['email']
    #         subject = self.cleaned_data['subject']
    #         account = Account.objects.get(email=email)
    #         account.subject = subject  # Set the new value for the 'subject' field
    #         account.save()  # Save the changes to the database
        
    # def clean_term(self):
    #     if self.is_valid():
    #         email = self.cleaned_data['email']
    #         term = self.cleaned_data['term']
    #         account = Account.objects.get(email=email)
    #         account.term = term  # Set the new value for the 'subject' field
    #         account.save()  # Save the changes to the database
        
    # def clean_crn(self):
    #     if self.is_valid():
    #         email = self.cleaned_data['email']
    #         crn = self.cleaned_data['crn']
    #         account = Account.objects.get(email=email)
    #         account.crn = crn  # Set the new value for the 'subject' field
    #         account.save()  # Save the changes to the database


    # def clean_email(self):
    #     if self.is_valid():
    #         subject = self.cleaned_data['subject']
    #         account = Account.objects.get(subject=subject)
        
        
    # def clean_username(self):
    #     if self.is_valid():
    #         username = self.cleaned_data['username']
    #         try:
    #             account = Account.objects.exclude(pk=self.instance.pk).get(username=username)
    #         except Account.DoesNotExist:
    #             return username
    #         raise forms.ValidationError('Username ' "%s" ' is already in use.' % username)
        
    

