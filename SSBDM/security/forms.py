from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import UserProfile, Role, SecuritySettings

class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)
    department = forms.CharField(max_length=100, required=False)
    phone_number = forms.CharField(max_length=20, required=False)
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('This email address is already in use.'))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile = UserProfile.objects.create(
                user=user,
                department=self.cleaned_data.get('department', ''),
                phone_number=self.cleaned_data.get('phone_number', '')
            )
            if self.cleaned_data.get('roles'):
                user.groups.add(*self.cleaned_data['roles'])
        return user

class UserUpdateForm(UserChangeForm):
    department = forms.CharField(max_length=100, required=False)
    phone_number = forms.CharField(max_length=20, required=False)
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            try:
                profile = self.instance.profile
                self.fields['department'].initial = profile.department
                self.fields['phone_number'].initial = profile.phone_number
            except UserProfile.DoesNotExist:
                pass
            self.fields['roles'].initial = self.instance.groups.all()

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.department = self.cleaned_data.get('department', '')
            profile.phone_number = self.cleaned_data.get('phone_number', '')
            profile.save()
            if self.cleaned_data.get('roles'):
                user.groups.set(self.cleaned_data['roles'])
        return user

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'description', 'permissions']
        widgets = {
            'permissions': forms.CheckboxSelectMultiple,
        }

class SecuritySettingsForm(forms.ModelForm):
    class Meta:
        model = SecuritySettings
        fields = [
            'enable_two_factor',
            'password_expiry_days',
            'max_login_attempts',
            'lockout_duration_minutes',
            'session_timeout_minutes'
        ]
        widgets = {
            'password_expiry_days': forms.NumberInput(attrs={'min': 1}),
            'max_login_attempts': forms.NumberInput(attrs={'min': 1}),
            'lockout_duration_minutes': forms.NumberInput(attrs={'min': 1}),
            'session_timeout_minutes': forms.NumberInput(attrs={'min': 1}),
        }

    def clean_password_expiry_days(self):
        days = self.cleaned_data.get('password_expiry_days')
        if days < 1:
            raise ValidationError(_('Password expiry days must be at least 1'))
        return days

    def clean_max_login_attempts(self):
        attempts = self.cleaned_data.get('max_login_attempts')
        if attempts < 1:
            raise ValidationError(_('Maximum login attempts must be at least 1'))
        return attempts

    def clean_lockout_duration_minutes(self):
        minutes = self.cleaned_data.get('lockout_duration_minutes')
        if minutes < 1:
            raise ValidationError(_('Lockout duration must be at least 1 minute'))
        return minutes

    def clean_session_timeout_minutes(self):
        minutes = self.cleaned_data.get('session_timeout_minutes')
        if minutes < 1:
            raise ValidationError(_('Session timeout must be at least 1 minute'))
        return minutes 