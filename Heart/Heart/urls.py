# Heart/urls.py or project_name/urls.py
from django.contrib import admin
from django.urls import path, include
from predictor import views  # Import the views from the predictor app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('predictor/', include('predictor.urls')),  # Include the urls of the predictor app
    path('', views.home, name='home'),  # Add this line to serve the root URL
]
