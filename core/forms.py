from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Confirm Password'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Email'}),
        }

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return confirm_password

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_image', 'age', 'gender', 'hypertension', 'heart_disease', 'ever_married', 'work_type', 'residence_type', 'smoking_status']
        widgets = {
            'profile_image': forms.FileInput(attrs={'class': 'form-control rounded-pill'}),
            'age': forms.NumberInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Age'}),
            'gender': forms.Select(attrs={'class': 'form-select rounded-pill'}, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]),
            'hypertension': forms.Select(attrs={'class': 'form-select rounded-pill'}, choices=[(0, 'No'), (1, 'Yes')]),
            'heart_disease': forms.Select(attrs={'class': 'form-select rounded-pill'}, choices=[(0, 'No'), (1, 'Yes')]),
            'ever_married': forms.Select(attrs={'class': 'form-select rounded-pill'}, choices=[('Yes', 'Yes'), ('No', 'No')]),
            'work_type': forms.Select(attrs={'class': 'form-select rounded-pill'}, choices=[('Private', 'Private'), ('Self-employed', 'Self-employed'), ('Govt_job', 'Govt Job'), ('children', 'Children'), ('Never_worked', 'Never Worked')]),
            'residence_type': forms.Select(attrs={'class': 'form-select rounded-pill'}, choices=[('Urban', 'Urban'), ('Rural', 'Rural')]),
            'smoking_status': forms.Select(attrs={'class': 'form-select rounded-pill'}, choices=[('never smoked', 'Never Smoked'), ('formerly smoked', 'Formerly Smoked'), ('smokes', 'Smokes'), ('Unknown', 'Unknown')]),
        }
