"""
URL configuration for frontend project.

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
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('restaurar-datos/', views.restaurar_datos, name='restaurar_datos'),
    path('cargar-mensajes/', views.cargar_mensajes, name='cargar_mensajes'),
    path('cargar-configuracion/', views.cargar_configuracion, name='cargar_configuracion'),
    path('consultar-hashtags/', views.consultar_hashtags, name='consultar_hashtags'),
    path('consultar-menciones/', views.consultar_menciones, name='consultar_menciones'),
    path('consultar-sentimientos/', views.consultar_sentimientos, name='consultar_sentimientos'),
    path('graficar-hashtags/', views.graficar_hashtags, name='graficar_hashtags'),
    path('graficar-menciones/', views.graficar_menciones, name='graficar_menciones'),
    path('graficar-sentimientos/', views.graficar_sentimientos, name='graficar_sentimientos'),
    path('informacion-estudiante/', views.informacion_estudiante, name='informacion_estudiante'),
]
