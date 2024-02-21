# import some stuff
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate


# import our actual account model
from account.models import Account


# make the form for registering an account
class RegistrationForm(UserCreationForm):
    # reference premade django email form
    email = forms.EmailField(max_length=60, help_text='Required. Add a valid email address.')

    class Meta:
        model = Account
        # requires these fields
        fields = ("email", "username", "password1", "password2")


# make the form for logging in
class AccountAuthenticationForm(forms.ModelForm):
    # grab the password
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    # rquires these fields for log in
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
    # require these fields for saving which class user wants
    class Meta:
        model = Account
        # this is how the input field is
        fields = ('subject', 'term', 'crn')

    # clean the inputted data
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

        
    

