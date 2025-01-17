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

from storage_module import views
from storage_module.views import BoxDetailView, FacilityDetailView, FacilityListView, \
    FreezerDetailView, HomeView, RackDetailView, SampleDetailView, SamplesView, \
    ShelfDetailView, SampleMoveWizard

urlpatterns = [
    path('accounts/', include('edc_base.auth.urls')),
    path('admin/', include('edc_base.auth.urls')),
    path('admin/', admin.site.urls),
    path('home/', HomeView.as_view(), name='home_url'),
    path('samples/', SamplesView.as_view(), name='samples_url'),
    path('get_shelves/', views.get_shelves, name='get_shelves'),
    path('get_racks/', views.get_racks, name='get_racks'),
    path('samples/<str:sample_id>/', SampleDetailView.as_view(), name='sample_detail'),
    path('box/<str:box_id>/', BoxDetailView.as_view(), name='box_detail'),
    path('rack/<str:rack_id>/', RackDetailView.as_view(), name='rack_detail'),
    path('shelf/<str:shelf_id>/', ShelfDetailView.as_view(), name='shelf_detail'),
    path('freezer/<str:freezer_id>/', FreezerDetailView.as_view(), name='freezer_detail'),
    path('freezer_data/<int:freezer_id>/', views.freezer_data, name='freezer_data'),
    path('facility/<str:facility_id>/', FacilityDetailView.as_view(),
         name='facility_detail'),
    path('move_samples/', SampleMoveWizard.as_view(), name='move_samples'),
    path('reports/', HomeView.as_view(), name='reports_url'),
    path('dashboard/', HomeView.as_view(), name='dashboard_url'),
    path('storage_view/', FacilityListView.as_view(), name='storage_view'),
    path('select2/', include('django_select2.urls')),
    path('help/', HomeView.as_view(), name='help_url'),
    path('', HomeView.as_view(), name='home_url'),
]
