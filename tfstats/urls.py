"""tfstats URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import homepage.views
import about.views
import search.views
import login.views

urlpatterns = [
    path('', homepage.views.index),
    path('profiles/', include("profiles.urls")),
    path('admin/', admin.site.urls),
    path('about/', about.views.about),
    path('global/', include("global_stats.urls")),
    path('search/', search.views.search),
    path('login/', include("login.urls")),
    path('logout/', login.views.logout),
]

urlpatterns += staticfiles_urlpatterns()
