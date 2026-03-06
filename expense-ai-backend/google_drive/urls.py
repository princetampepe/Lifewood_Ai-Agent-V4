from django.urls import path
from . import views

urlpatterns = [
    path('auth/', views.google_drive_auth, name='google_drive_auth'),
    path('callback/', views.oauth2callback, name='oauth2callback'),
    path('files/', views.list_drive_files, name='list_drive_files'),
]