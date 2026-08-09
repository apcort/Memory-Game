from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),

    path('nivel/', views.seleccionar_nivel, name='seleccionar_nivel'),
    path('jugar/<str:nivel>/', views.jugar_view, name='jugar'),
    path('api/guardar-partida/', views.guardar_partida, name='guardar_partida'),

    path('perfil/', views.perfil_view, name='perfil'),
]
