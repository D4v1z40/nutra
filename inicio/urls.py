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
<<<<<<< HEAD
    path('alterar_senha/', views.alterar_senha, name='alterar_senha'),
    path('sobre_sistema/', views.sobre_sistema, name='sobre_sistema'),
    path('sobre_desenvolvedores/', views.sobre_desenvolvedores,
         name='sobre_desenvolvedores'),
    path('dieta/', views.dieta, name='dieta'),
    path('detalhes_alimento/<int:food_id>/',
         views.detalhes_alimento, name='detalhes_alimento'),
    path('adicionar_exercicio/', views.adicionar_exercicio,
         name='adicionar_exercicio'),
    path('montar_treino_detalhes/', views.montar_treino_detalhes,
         name='montar_treino_detalhes'),
    path('visualizar_treino/', views.visualizar_treino, name='visualizar_treino'),

    # APIs do sistema de dieta
    path('api/profile/update/', views.update_profile, name='update_profile'),
    path('api/password/change/', views.change_password, name='change_password'),
    path('api/personal-data/update/', views.update_personal_data, name='update_personal_data'),
    path('api/foods/search/', views.search_foods, name='search_foods'),
    path('api/meals/add/', views.add_meal, name='add_meal'),
    path('api/meals/<int:meal_id>/delete/',
         views.delete_meal, name='delete_meal'),
    path('api/meals/<int:meal_id>/copy/', views.copy_meal, name='copy_meal'),
    path('api/diet/clear-day/', views.clear_day, name='clear_day'),
    path('api/diet/replicate-day/', views.replicate_day, name='replicate_day'),
    path('api/foods/<int:food_id>/toggle-favorite/',
         views.toggle_favorite, name='toggle_favorite'),
    path('populate-foods/', views.populate_sample_foods, name='populate_foods'),

=======
    path('sobre_sistema/', views.sobre_sistema, name='sobre_sistema'),
    path('sobre_desenvolvedores/', views.sobre_desenvolvedores,
         name='sobre_desenvolvedores'),

>>>>>>> 7c00dd63e00d5001ae3bb0d5b39c11a1dfb22ba9
    # Outras rotas...

]
