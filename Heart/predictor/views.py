import joblib
import numpy as np
from sklearn.preprocessing import StandardScaler
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import logout as auth_logout


# Load the saved model
model = joblib.load('catboost_model.pkl')
#scaler = joblib.load('scaler.pkl')


# Home view
def home(request):
    return render(request, 'home.html')


# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # If authentication is successful, login the user
            login(request, user)
            return redirect('predict_heart_disease')  # Redirect to the prediction page after successful login
        else:
            # If authentication fails, show an error message
            messages.error(request, 'Invalid username or password')
            return redirect('login')  # Stay on the login page and show error message
    
    return render(request, 'login.html')  # Render the login page if it's a GET request


# Register view
def register(request):
    if request.method == 'POST':
        # Get the data from the form (username, password, etc.)
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        
        # Ensure all fields are provided
        if not all([username, password, email, first_name, last_name]):
            messages.error(request, "Please fill in all fields.")
            return redirect('register')
        
        try:
            # Create a new user using Django's User model
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            # Log the user in after registration
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('home')  # Redirect to the home page after successful registration

        except Exception as e:
            # Handle errors if any occur (e.g., if username is already taken)
            messages.error(request, f"Error during registration: {str(e)}")
            return redirect('register')
    
    return render(request, 'register.html')


# Predict heart disease view
def predict_heart_disease(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    prediction = None
    error_message = None
    if request.method == 'POST':
        try:
            # Safely retrieve form inputs
            age = int(request.POST.get('age', 0))
            sex = int(request.POST.get('sex', 0))  # Assuming binary (0 or 1)
            chest_pain_type = int(request.POST.get('chest_pain_type', -1))  # Default to -1 if missing
            resting_bp_s = int(request.POST.get('resting_bp_s', 0))
            cholesterol = int(request.POST.get('cholesterol', 0))
            fasting_blood_sugar = int(request.POST.get('fasting_blood_sugar', 0))  # 1 or 0
            resting_ecg = int(request.POST.get('resting_ecg', 0))  # Encoded value
            max_heart_rate = int(request.POST.get('max_heart_rate', 0))
            exercise_angina = int(request.POST.get('exercise_angina', 0))  # 0 or 1
            oldpeak = float(request.POST.get('oldpeak', 0.0))
            st_slope = int(request.POST.get('st_slope', 0))  # Categorical encoding

            # Prepare the input data for prediction
            input_data = np.array([[age, sex, chest_pain_type, resting_bp_s, cholesterol,
                                    fasting_blood_sugar, resting_ecg, max_heart_rate, 
                                    exercise_angina, oldpeak, st_slope]])

            # Scale the input data using the saved scaler
            #input_data_scaled = scaler.transform(input_data)

            # Make the prediction
            prediction = model.predict(input_data)
            prediction_text = "Risk" if prediction[0] == 1 else "No Risk"

            return render(request, 'prediction_result.html', {'prediction': prediction_text})
        
        except ValueError as e:
            # Handle missing or invalid data gracefully
            error_message = f"Invalid input: {e}"

    return render(request, 'prediction_form.html', {'error': error_message})


def logout_view(request):
    auth_logout(request)  # Call the built-in logout
    return redirect('login')  
