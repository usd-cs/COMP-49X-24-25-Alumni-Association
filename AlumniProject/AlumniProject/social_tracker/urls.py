from django.urls import path
from . import views

app_name = 'social_tracker' 

urlpatterns = [
    path('download-csv/', views.download_csv, name='download_csv'),
]
