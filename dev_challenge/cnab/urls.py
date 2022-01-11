from django.urls import path
from . import views

urlpatterns = [
    path('', views.cnab, name='cnab')
]
