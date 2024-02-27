"""
URL configuration for storage_module project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from django.urls.conf import include

from storage_module.views import HomeView, SamplesView

urlpatterns = [
    path('accounts/', include('edc_base.auth.urls')),
    path('admin/', include('edc_base.auth.urls')),
    path('admin/', admin.site.urls),
    path('home/', HomeView.as_view(), name='home_url'),
    path('samples/', SamplesView.as_view(), name='samples_url'),
    path('reports/', HomeView.as_view(), name='reports_url'),
    path('dashboard/', HomeView.as_view(), name='dashboard_url'),
    path('help/', HomeView.as_view(), name='help_url'),
    path('', HomeView.as_view(), name='home_url'),
]
