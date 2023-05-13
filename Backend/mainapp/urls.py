from django.contrib import admin
from django.urls import path, include

from mainapp import views

urlpatterns = [
    path('get-full-db/', views.get_full_db, name='get-full-data')
]
