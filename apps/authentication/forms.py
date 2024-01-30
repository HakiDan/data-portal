from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import *
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from core import validators
from apps.upload.models import UserProfile, AgencyList, MasterlistBudget, DQUser
import re

class LoginForm(forms.Form):
    """_summary_
    Login form for user

    Args:
        forms (_type_): _description_
    """
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Nama pengguna",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Kata laluan",
                "class": "form-control",
            }
        ))
        
        
class CustomSetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': ('Kata laluan yang anda masukkan pada ruangan kata laluan baru dan sahkan kata laluan tidak sama.'),
    }
    new_password1 = forms.CharField(
        label=("New password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=validators.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        validators.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
        
        
class CustomPasswordChangeForm(CustomSetPasswordForm):
    """
    A form that lets a user change their password by entering their old
    password.
    """
    error_messages = {
        **CustomSetPasswordForm.error_messages,
        'password_incorrect': ("Kata laluan anda sekarang tidak sama dengan kata laluan yang anda masukkan."),
    }
    old_password = forms.CharField(
        label=("Old password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'autofocus': True}),
    )

    field_order = ['old_password', 'new_password1', 'new_password2']

    def clean_old_password(self):
        """
        Validate that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password

    def clean(self):
        cleaned_data = super(CustomSetPasswordForm, self).clean()
        new_password1 = cleaned_data.get('new_password1')
        old_password = self.cleaned_data["old_password"]
        if old_password == new_password1:
            self.add_error('new_password1', 'Kata laluan baru sama dengan kata laluan anda sekarang.')


class NewUserForm(UserCreationForm):
    """_summary_
    User registration form

    Args:
        UserCreationForm (_type_): _description_

    Raises:
        ValidationError: _description_

    Returns:
        _type_: _description_
    """
    class Meta:
        model = User
        fields = ("username", "first_name",
                  "password1", "password2",)
        
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs) 
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'
        
    error_messages = {
        'password_mismatch': ('Kata laluan tidak sepadan'),
    }
    
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Emel pejabat pengguna",
                "class": "form-control"
            }
        ), 
        required=True, 
        # help_text='contoh: test@example.com, test@org, test@gov.my',
    )
    
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Nama penuh pengguna",
                "class": "form-control"
            }
        ), required=True)
    
    password1 = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    password2 = forms.CharField(
        widget=forms.HiddenInput()
    )
        
    def clean_username(self):
        regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        username = self.cleaned_data.get("username")
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            error_messages = {
                'username_exists': ('Nama pengguna "%s" telah didaftarkan dalam PODS' % username),
            }
            raise ValidationError(
                error_messages['username_exists'],
                code='username_exists',
            )
            
        if not(re.fullmatch(regex_email, username)):
            self._errors['username'] = self.error_class(["Kata pengguna tidak sah"])
      
        return username


class CustomMMCF(forms.ModelMultipleChoiceField):
    """_summary_
    Return list of subinitiative name

    Args:
        forms (_type_): _description_
    """       
    def label_from_instance(self, subinit_name):
        return "%s" % subinit_name.subinit_name
        
        
class ProfileUpdate(forms.ModelForm):
    """_summary_
    Form for UserProfile model (For user registration & user update form)

    Args:
        forms (_type_): _description_

    Returns:
        _type_: _description_
    """
    class Meta:
        model = UserProfile
        fields = ["agency_name", "phone_number",
                "dq_name", "init_id_assc", "is_lead"]
        # error_messages = {
        #     'first_name': {
        #         'max_length': _("This writer's name is too long."),
        #     },
        # }

    agency_name = forms.ModelChoiceField(
        queryset=AgencyList.objects.all(),
        empty_label="Nama Agensi Pengguna",
        # required=False,
    )

    init_id_assc = CustomMMCF(
        queryset=MasterlistBudget.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    
    dq_name = forms.ModelChoiceField(
        queryset=DQUser.objects.all(),
        widget=forms.Select(
            attrs={
                    "placeholder": "Emel BDA",
                    "class": "form-select mb-3"
                }
        ),
        empty_label="Nama BDA Berkaitan",
    )
    
    phone_number = forms.CharField(
        initial= "+601",  
        widget=forms.TextInput(
            attrs={
                "placeholder": "No telefon pengguna",
                "class": "form-control",
            }
        ), 
        help_text='Nombor telefon pengguna mesti dalam bentuk: +60123456789',
        required=False,
    )

    is_lead = forms.BooleanField(
        required= False,
    ) 
    
    def clean(self):
        super(ProfileUpdate, self).clean()
        phone_number = self.cleaned_data.get('phone_number')
        # regex_phone = r'^(?:[+]6)?0(([0-9]{2}((\s[0-9]{3,4}\s[0-9]{4})|(-[0-9]{3,4}\s[0-9]{4})|(-[0-9]{7,8})))|([0-9]{9,10}))$'
        regex_phone = r'^\+601[0-9]{8}$'
        
        if not(re.fullmatch(regex_phone, phone_number)):
            self._errors['phone_number'] = self.error_class(["Nombor telefon tidak sah"])
            
        return self.cleaned_data
    
    
    

class UserForm(forms.ModelForm):
    """_summary_
    User update form

    Args:
        forms (_type_): _description_
    """
    class Meta:
        model = User
        fields = ["username", "first_name", "email",]