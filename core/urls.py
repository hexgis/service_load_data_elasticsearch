"""gcpRunLandsatChangeDetection URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path

from .views import (UpdateDetectionView,
                    ClearDetectionStructure, CreateDetectionStructure)

urlpatterns = [
    # path('create', CreateES.as_view(), name='create-es-structure'),
    path('delete-detection', ClearDetectionStructure.as_view(),
         name='delete-detection'),
    path('update-detection', UpdateDetectionView.as_view(), name='update-detection'),
    path('create-detection', CreateDetectionStructure.as_view(),
         name='create-detection'),

    path('delete-soy', ClearDetectionStructure.as_view(), name='delete-detection'),
    path('update-soy', UpdateDetectionView.as_view(), name='update-detection'),
    path('create-soy', CreateDetectionStructure.as_view(), name='create-detection'),

]
