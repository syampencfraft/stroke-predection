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
