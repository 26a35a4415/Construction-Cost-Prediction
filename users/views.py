# users/views.py
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserRegistrationModel
from .forms import UserRegistrationForm
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import matplotlib
matplotlib.use('Agg')
import os
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import numpy as np

# Load dataset (move this to a more appropriate location if needed)

# Load dataset from the project's media folder

# Load dataset
try:
    dataset_path = os.path.join(settings.MEDIA_ROOT, 'CUB_SP_R16N.csv')
    data = pd.read_csv(dataset_path)

    x = data.iloc[:, 0:-1]
    y = data.iloc[:, -1]

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )

except Exception as e:
    print(f"Error loading dataset: {e}")


    # Handle the error appropriately

def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful!')
            return redirect('UserLogin')
        else:
            messages.error(request, 'Registration failed. Please check your information.')
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})

def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        try:
            user = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            if user.status == "activated":
                request.session['id'] = user.id
                request.session['loggeduser'] = user.name
                request.session['loginid'] = loginid
                request.session['email'] = user.email
                return redirect('UserHome')
            else:
                messages.error(request, 'Your account is not activated yet.')
        except UserRegistrationModel.DoesNotExist:
            messages.error(request, 'Invalid login credentials.')
    return render(request, 'UserLogin.html')

def UserHome(request):
    return render(request, 'users/UserHomePage.html')

def analytics(request):
    # Your analytics view implementation here
    models = {
        'Random Forest': RandomForestClassifier(),
        'Decision Tree': DecisionTreeClassifier(),
        'KNN': KNeighborsClassifier(),
        'SVM': SVC()
    }
    
    results = {}
    
    for name, model in models.items():
        model.fit(x_train, y_train)
        y_pred = model.predict(x_test)
        
        results[name] = {
            'accuracy': round(accuracy_score(y_test, y_pred) * 100, 2),
            'precision': round(precision_score(y_test, y_pred, average='weighted') * 100, 2),
            'recall': round(recall_score(y_test, y_pred, average='weighted') * 100, 2),
            'f1': round(f1_score(y_test, y_pred, average='weighted') * 100, 2),
            'cm': confusion_matrix(y_test, y_pred)
        }
    
    # Generate plots (you can move this to a separate function)
    plots = {}
    plt.figure(figsize=(10, 5))
    names = list(results.keys())
    accuracies = [results[name]['accuracy'] for name in names]
    plt.bar(names, accuracies)
    plt.title('Algorithm Comparison')
    plt.ylabel('Accuracy (%)')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plots['comparison'] = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    
    context = {
        'results': results,
        'plots': plots
    }
    return render(request, 'users/analytics.html', context)

def dataset_view(request):
    # Implement your dataset view here
    return render(request, 'users/dataset.html')

def predection(request):
    if request.method == 'POST':
        try:
            # Get form data
            input_data = [
                float(request.POST.get('year')),
                float(request.POST.get('month')),
                float(request.POST.get('manpw_cost')),
                float(request.POST.get('material_cost')),
                float(request.POST.get('manag_cost'))
            ]
            
            model = RandomForestClassifier()
            model.fit(x_train, y_train)
            prediction = model.predict([input_data])[0]
            
            return render(request, 'users/output.html', {'prediction': prediction})
        except Exception as e:
            messages.error(request, f'Prediction error: {str(e)}')
            return redirect('predection')
    
    return render(request, 'users/predection.html')