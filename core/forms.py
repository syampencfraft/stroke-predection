from django import forms
import datetime
from django.contrib.auth.models import User
from .models import UserProfile, DoctorProfile, Appointment, ContactMessage

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Password', 'required': 'required', 'minlength': '8'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Confirm Password', 'required': 'required'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Email', 'required': 'required'}), required=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'First Name', 'required': 'required'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Last Name', 'required': 'required'}),
            'username': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Username', 'required': 'required', 'minlength': '4'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already taken. Please choose another.")
        return email

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
            'age': forms.NumberInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Age', 'required': 'required', 'min': '1', 'max': '120'}),
            'gender': forms.Select(attrs={'class': 'form-select rounded-pill', 'required': 'required'}, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]),
            'hypertension': forms.Select(attrs={'class': 'form-select rounded-pill', 'required': 'required'}, choices=[(0, 'No'), (1, 'Yes')]),
            'heart_disease': forms.Select(attrs={'class': 'form-select rounded-pill', 'required': 'required'}, choices=[(0, 'No'), (1, 'Yes')]),
            'ever_married': forms.Select(attrs={'class': 'form-select rounded-pill', 'required': 'required'}, choices=[('Yes', 'Yes'), ('No', 'No')]),
            'work_type': forms.Select(attrs={'class': 'form-select rounded-pill', 'required': 'required'}, choices=[('Private', 'Private'), ('Self-employed', 'Self-employed'), ('Govt_job', 'Govt Job'), ('children', 'Children'), ('Never_worked', 'Never Worked')]),
            'residence_type': forms.Select(attrs={'class': 'form-select rounded-pill', 'required': 'required'}, choices=[('Urban', 'Urban'), ('Rural', 'Rural')]),
            'smoking_status': forms.Select(attrs={'class': 'form-select rounded-pill', 'required': 'required'}, choices=[('never smoked', 'Never Smoked'), ('formerly smoked', 'Formerly Smoked'), ('smokes', 'Smokes'), ('Unknown', 'Unknown')]),
        }

class DoctorRegistrationForm(UserRegistrationForm):
    pass # Inherits username, email, password logic

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['profile_image', 'specialization', 'license_number', 'hospital', 'phone']
        widgets = {
            'profile_image': forms.FileInput(attrs={'class': 'form-control rounded-pill', 'required': 'required'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Specialization (e.g. Neurologist)', 'required': 'required'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'License Number', 'required': 'required'}),
            'hospital': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Hospital Name', 'required': 'required'}),
            'phone': forms.TextInput(attrs={'class': 'form-control rounded-pill', 'placeholder': 'Phone Number', 'required': 'required', 'pattern': '^\+?[0-9]{10,15}$', 'title': 'Enter a valid 10-15 digit phone number'}),
        }

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'date', 'time', 'reason']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-select rounded-pill'}),
            'date': forms.DateInput(attrs={'class': 'form-control rounded-pill', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control rounded-pill', 'type': 'time'}),
            'reason': forms.Textarea(attrs={'class': 'form-control rounded-3', 'placeholder': 'Reason for appointment', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only list verified doctors
        doctor_qs = DoctorProfile.objects.filter(is_verified=True)
        self.fields['doctor'].queryset = doctor_qs
        # Display both Name and Specialization for clear identification
        self.fields['doctor'].label_from_instance = lambda obj: f"Dr. {(obj.user.first_name + ' ' + obj.user.last_name).strip() or obj.user.username} — {obj.specialization}"

    def clean_date(self):
        appointment_date = self.cleaned_data.get('date')
        if appointment_date < datetime.date.today():
            raise forms.ValidationError("You cannot book an appointment for a past date.")
        return appointment_date

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'john@example.com'}),
            'subject': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', 'Select Subject'),
                ('AI Model Inquiry', 'AI Model Inquiry'),
                ('Clinical Partnering', 'Clinical Partnering'),
                ('Technical Support', 'Technical Support'),
                ('Other', 'Other')
            ]),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your message here...', 'rows': 5}),
        }
