"""
URL configuration for mars project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from .views import home_view, test_view
from tenants.views import (register_view, login_view, logout_view,)

urlpatterns = [
    path('', home_view, name='home'),
    path('fees/', include('fees.urls')),
    path('accounting/', include('accounting.urls')),
    path('charges/', include('charges.urls')),
    path('files/', include('files.urls')),

    path('admin/', admin.site.urls),
    path('register/', register_view),
    path('login/', login_view),
    path('logout/', logout_view),
    path('test/', test_view)
]
