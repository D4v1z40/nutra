from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('perfil/', views.perfil, name='perfil'),
    path('treino/', views.treino, name='treino'),
    path('montar_treino/', views.montar_treino, name='montar_treino'),
    path('logout/', views.logout_view, name='logout'),
    path('configuracoes/', views.configuracoes, name='configuracoes'),
    path('sobre_sistema/', views.sobre_sistema, name='sobre_sistema'),
    path('sobre_desenvolvedores/', views.sobre_desenvolvedores,
         name='sobre_desenvolvedores'),

    # Outras rotas...

]
