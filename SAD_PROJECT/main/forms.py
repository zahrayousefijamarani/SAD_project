from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# Create your forms here.

class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class AddCustomInfo(forms.Form):
    # phone_number = forms.RegexField(regex=r'^\+?1?\d{9,15}$',error_messages="Wrong phone number format.")
    address = forms.CharField(max_length=50)
    city = forms.CharField(max_length=60, label="Tehran")
    state = forms.CharField(max_length=30, label="Tehran")
    country = forms.CharField(max_length=50, label="Iran")


class EditForm(forms.Form):
    address = forms.CharField(label='address', max_length=100)
    city = forms.CharField(label='city', max_length=60)
    state = forms.CharField(label='state', max_length=30)
    country = forms.CharField(label='country', max_length=50)
    phone_number = forms.CharField(label='phone number', max_length=17)


class ShareForm(forms.Form):
    address = forms.CharField(label='address', max_length=100)
    city = forms.CharField(label='city', max_length=60)
    state = forms.CharField(label='state', max_length=30)
    country = forms.CharField(label='country', max_length=50)
    date = forms.DateField(label='Date', widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    image = forms.ImageField(label='image', required=False)
    creditor = forms.ChoiceField(choices=(), label='creditor')

    def edit(self, my_choices):
        self.fields['creditor'].choices = my_choices
