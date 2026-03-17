from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    age = models.FloatField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    hypertension = models.IntegerField(default=0)
    heart_disease = models.IntegerField(default=0)
    ever_married = models.CharField(max_length=5, null=True, blank=True)
    work_type = models.CharField(max_length=20, null=True, blank=True)
    residence_type = models.CharField(max_length=10, null=True, blank=True)
    smoking_status = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.user.username

class PredictionHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    gender = models.CharField(max_length=10)
    age = models.FloatField()
    hypertension = models.IntegerField()
    heart_disease = models.IntegerField()
    ever_married = models.CharField(max_length=5)
    work_type = models.CharField(max_length=20)
    residence_type = models.CharField(max_length=10)
    avg_glucose_level = models.FloatField()
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    bmi = models.FloatField()
    bmi_category = models.CharField(max_length=20, null=True, blank=True)
    smoking_status = models.CharField(max_length=20)
    prediction = models.IntegerField()
    prediction_probability = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction for Age {self.age} - Result: {'Stroke' if self.prediction == 1 else 'No Stroke'}"

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='doctors/', null=True, blank=True)
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    hospital = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.user.last_name or self.user.username} ({self.specialization})"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='doctor_appointments')
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment: {self.patient.username} with {self.doctor.user.last_name} on {self.date}"
