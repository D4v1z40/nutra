from django.urls import path
from . import views

urlpatterns = [

    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('perfil/', views.perfil, name='perfil'),
    path('treino/', views.treino, name='treino'),
    path('montar_treino/', views.montar_treino, name='montar_treino'),

]