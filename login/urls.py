from django.urls import path

from . import views

urlpatterns = [
    path('', views.lits, name='sits'),
    path('return/', views.return_url, name='return'),
] 
