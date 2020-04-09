from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:steamid>', views.profile),
    path('<steamid>', views.invalid_id),
] 
