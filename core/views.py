from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
import joblib
import pandas as pd
import os
from .models import PredictionHistory, UserProfile, DoctorProfile, Appointment
from .forms import UserRegistrationForm, UserProfileForm, DoctorRegistrationForm, DoctorProfileForm, AppointmentForm

# Load the model and components
MODEL_PATH = os.path.join('data', 'best_stroke_model.pkl')
try:
    model_data = joblib.load(MODEL_PATH)
    MODEL = model_data['model']
    SCALER = model_data['scaler']
    LE_DICT = model_data['le_dict']
    FEATURES = model_data['feature_names']
except Exception as e:
    print(f"Error loading model: {e}")
    MODEL = None

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        u_form = UserRegistrationForm(request.POST)
        p_form = UserProfileForm(request.POST, request.FILES)
        if u_form.is_valid() and p_form.is_valid():
            user = u_form.save(commit=False)
            user.set_password(u_form.cleaned_data['password'])
            user.save()
            profile = p_form.save(commit=False)
            profile.user = user
            profile.save()
            login(request, user)
            return redirect('login')
    else:
        u_form = UserRegistrationForm()
        p_form = UserProfileForm()
    return render(request, 'register.html', {'u_form': u_form, 'p_form': p_form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Check if user is a doctor
            if hasattr(user, 'doctorprofile'):
                if not user.doctorprofile.is_verified:
                    messages.warning(request, "Your doctor account is pending admin approval. Please wait for verification.")
                    return redirect('login')
                else:
                    login(request, user)
                    return redirect('doctor_dashboard')
            
            # Regular user / Admin
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def doctor_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Check if user is a doctor
            if hasattr(user, 'doctorprofile'):
                if not user.doctorprofile.is_verified:
                    messages.warning(request, "Your doctor account is pending admin approval. Please wait for verification.")
                    return redirect('login')
                else:
                    login(request, user)
                    return redirect('doctor_dashboard')
            
            # Regular user / Admin login through dr portal? Allow but redirect normally
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'doctor_login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    # If doctor, redirect to doctor profile
    if hasattr(request.user, 'doctorprofile'):
        return redirect('doctor_profile')
        
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Create a profile if it doesn't exist (e.g. for superusers or migration edge cases)
        return redirect('home')
    if request.method == 'POST':
        p_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if p_form.is_valid():
            p_form.save()
            return redirect('profile')
    else:
        p_form = UserProfileForm(instance=user_profile)
    return render(request, 'profile.html', {'p_form': p_form, 'profile': user_profile})

@login_required
def predict(request):
    if request.method == 'POST':
        # Get data from POST request
        data = {
            'gender': request.POST.get('gender'),
            'age': float(request.POST.get('age')),
            'hypertension': int(request.POST.get('hypertension')),
            'heart_disease': int(request.POST.get('heart_disease')),
            'ever_married': request.POST.get('ever_married'),
            'work_type': request.POST.get('work_type'),
            'Residence_type': request.POST.get('residence_type'),
            'avg_glucose_level': float(request.POST.get('avg_glucose_level')),
            'height': float(request.POST.get('height')),
            'weight': float(request.POST.get('weight')),
            'smoking_status': request.POST.get('smoking_status'),
        }

        # Calculate BMI: weight (kg) / [height (m)]^2
        height_m = data['height'] / 100
        bmi = data['weight'] / (height_m * height_m)
        data['bmi'] = round(bmi, 2)
        
        # Determine BMI Category
        if bmi < 18.5:
            data['bmi_category'] = 'Underweight'
        elif 18.5 <= bmi < 25:
            data['bmi_category'] = 'Normal'
        elif 25 <= bmi < 30:
            data['bmi_category'] = 'Overweight'
        else:
            data['bmi_category'] = 'Obese'

        # Preprocess input for model
        input_df = pd.DataFrame([data])
        # Drop height and weight as model doesn't expect them
        input_df = input_df.drop(['height', 'weight', 'bmi_category'], axis=1)
        
        # Apply Label Encoding using the saved encoders
        for col, le in LE_DICT.items():
            input_df[col] = le.transform(input_df[col])
        
        # Reorder columns to match training features
        input_df = input_df[FEATURES]
        
        # Scaling
        input_scaled = SCALER.transform(input_df)
        
        # Prediction
        prediction = int(MODEL.predict(input_scaled)[0])
        prob = MODEL.predict_proba(input_scaled)[0][1]

        # Save to history
        history = PredictionHistory(
            user=request.user,
            gender=data['gender'],
            age=data['age'],
            hypertension=data['hypertension'],
            heart_disease=data['heart_disease'],
            ever_married=data['ever_married'],
            work_type=data['work_type'],
            residence_type=data['Residence_type'],
            avg_glucose_level=data['avg_glucose_level'],
            height=data['height'],
            weight=data['weight'],
            bmi=data['bmi'],
            bmi_category=data['bmi_category'],
            smoking_status=data['smoking_status'],
            prediction=prediction,
            prediction_probability=prob
        )
        history.save()

        context = {
            'prediction': prediction,
            'probability': prob * 100,
            'data': data
        }
        return render(request, 'result.html', context)

    # If GET, pre-populate with user profile data if available
    initial_data = {}
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            initial_data = {
                'gender': user_profile.gender,
                'age': user_profile.age,
                'hypertension': user_profile.hypertension,
                'heart_disease': user_profile.heart_disease,
                'ever_married': user_profile.ever_married,
                'work_type': user_profile.work_type,
                'residence_type': user_profile.residence_type,
                'smoking_status': user_profile.smoking_status,
            }
        except UserProfile.DoesNotExist:
            pass
            
    return render(request, 'predict.html', {'initial_data': initial_data})

@login_required
def history(request):
    predictions = PredictionHistory.objects.filter(user=request.user).order_by('-created_at')
    # Add percentage for display
    for p in predictions:
        p.prob_percent = p.prediction_probability * 100 if p.prediction_probability else 0
    return render(request, 'history.html', {'predictions': predictions})

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def doctor_register(request):
    if request.method == 'POST':
        u_form = DoctorRegistrationForm(request.POST)
        d_form = DoctorProfileForm(request.POST, request.FILES)
        if u_form.is_valid() and d_form.is_valid():
            user = u_form.save(commit=False)
            user.set_password(u_form.cleaned_data['password'])
            user.save()
            profile = d_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.info(request, "Registration successful! Please wait for admin approval before logging in.")
            return redirect('login')
    else:
        u_form = DoctorRegistrationForm()
        d_form = DoctorProfileForm()
    return render(request, 'doctor_register.html', {'u_form': u_form, 'd_form': d_form})


@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    patients = UserProfile.objects.all()
    doctors = DoctorProfile.objects.all()
    context = {
        'patients': patients,
        'doctors': doctors
    }
    return render(request, 'admin_dashboard.html', context)

@user_passes_test(lambda u: u.is_superuser)
def approve_doctor(request, pk):
    doctor = get_object_or_404(DoctorProfile, pk=pk)
    doctor.is_verified = not doctor.is_verified
    doctor.save()
    return redirect('admin_dashboard')

@login_required
def book_appointment(request):
    # Doctors shouldn't book appointments through this patient-focused view
    if hasattr(request.user, 'doctorprofile'):
        return redirect('doctor_dashboard')
        
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.save()
            return redirect('my_appointments')
    else:
        # Pre-select doctor if pk is in GET
        doctor_id = request.GET.get('doctor')
        initial_data = {}
        if doctor_id:
            initial_data['doctor'] = doctor_id
        form = AppointmentForm(initial=initial_data)
    
    doctors = DoctorProfile.objects.filter(is_verified=True)
    return render(request, 'book_appointment.html', {'form': form, 'doctors': doctors})

@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(patient=request.user).order_by('-created_at')
    return render(request, 'my_appointments.html', {'appointments': appointments})

@login_required
def doctor_dashboard(request):
    # Only allow doctors to access their dashboard
    if not hasattr(request.user, 'doctorprofile'):
        return redirect('home')
    
    doctor = request.user.doctorprofile
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-date', '-time')
    return render(request, 'doctor_dashboard.html', {'appointments': appointments, 'doctor': doctor})

@login_required
def handle_appointment(request, pk, action):
    appointment = get_object_or_404(Appointment, pk=pk)
    # Security: check if the doctor owns this appointment
    if not hasattr(request.user, 'doctorprofile') or appointment.doctor != request.user.doctorprofile:
        return redirect('home')
    
    if action == 'approve':
        appointment.status = 'Approved'
    elif action == 'reject':
        appointment.status = 'Rejected'
    
    appointment.save()
    return redirect('doctor_dashboard')

@login_required
def doctor_profile(request):
    if not hasattr(request.user, 'doctorprofile'):
        return redirect('home')
    doctor = request.user.doctorprofile
    # Stats for the profile card
    appointments = Appointment.objects.filter(doctor=doctor)
    stats = {
        'total': appointments.count(),
        'approved': appointments.filter(status='Approved').count(),
        'pending': appointments.filter(status='Pending').count()
    }
    return render(request, 'doctor_profile.html', {'doctor': doctor, 'stats': stats})

@login_required
def edit_doctor_profile(request):
    if not hasattr(request.user, 'doctorprofile'):
        return redirect('home')
    doctor = request.user.doctorprofile
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('doctor_profile')
    else:
        form = DoctorProfileForm(instance=doctor)
    return render(request, 'edit_doctor_profile.html', {'form': form, 'doctor': doctor})

def view_doctor_profile(request, pk):
    doctor = get_object_or_404(DoctorProfile, pk=pk)
    if not doctor.is_verified:
        return redirect('home')
    return render(request, 'view_doctor.html', {'doctor': doctor})
