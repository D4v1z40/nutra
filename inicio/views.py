from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages  # para exibir mensagens (opcional)
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import date, timedelta
import json

from .models import UserProfile, Food, UserFood, Meal, MealItem, DailyNutrition

# Create your views here.


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        # Validação básica
        if not username or not senha:
            messages.error(request, "Por favor, preencha todos os campos.")
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=senha)

        if user is not None:
            auth_login(request, user)
            return redirect('perfil')
        else:
            messages.error(
                request, "Credenciais inválidas. Verifique seu nome de usuário e senha.")
    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirma_senha = request.POST.get('confirma-senha')

        if senha != confirma_senha:
            messages.error(request, "As senhas não coincidem.")
            return render(request, 'register.html')

        # Verifica se já existe um usuário com este username
        if User.objects.filter(username=usuario).exists():
            messages.error(request, "Nome de usuário já existe.")
            return render(request, 'register.html')

        try:
            user = User.objects.create_user(
                username=usuario, email=email, password=senha)
            user.save()
            messages.success(
                request, "Usuário criado com sucesso! Faça login para continuar.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Erro ao criar usuário: {e}")

    return render(request, 'register.html')


@login_required
def perfil(request):
    return render(request, 'perfil.html')


@login_required
def treino(request):
    return render(request, 'treino.html')


@login_required
def montar_treino(request):
    return render(request, 'montar_treino.html')


@login_required
def configuracoes(request):
    return render(request, 'configuracoes.html')


@login_required
def alterar_senha(request):
    return render(request, 'alterar_senha.html')


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def change_password(request):
    """Altera a senha do usuário"""
    try:
        data = json.loads(request.body)
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        # Validar se a senha atual está correta
        if not request.user.check_password(current_password):
            return JsonResponse({
                'success': False, 
                'error': 'Senha atual incorreta'
            })

        # Validar se as novas senhas coincidem
        if new_password != confirm_password:
            return JsonResponse({
                'success': False, 
                'error': 'As novas senhas não coincidem'
            })

        # Validar se a nova senha é diferente da atual
        if current_password == new_password:
            return JsonResponse({
                'success': False, 
                'error': 'A nova senha deve ser diferente da atual'
            })

        # Alterar a senha
        request.user.set_password(new_password)
        request.user.save()

        return JsonResponse({
            'success': True,
            'message': 'Senha alterada com sucesso!'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def update_personal_data(request):
    """Atualiza os dados pessoais do usuário"""
    try:
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        full_name = request.POST.get('full_name')

        # Validar email
        if email and email != request.user.email:
            if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Este email já está em uso'
                })
            request.user.email = email

        # Atualizar nome
        if full_name:
            request.user.first_name = full_name

        request.user.save()

        # Atualizar telefone no perfil
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        if phone:
            profile.phone = phone
        profile.save()

        return JsonResponse({
            'success': True,
            'message': 'Dados pessoais atualizados com sucesso!'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def sobre_sistema(request):
    return render(request, 'sobre_sistema.html')


@login_required
def sobre_desenvolvedores(request):
    return render(request, 'sobre_desenvolvedores.html')


@login_required
def detalhes_alimento(request, food_id):
    try:
        food = Food.objects.get(id=food_id)
        context = {
            'food': food,
        }
        return render(request, 'detalhes_alimento.html', context)
    except Food.DoesNotExist:
        return redirect('dieta')


@login_required
def dieta(request):
    # Obter ou criar perfil do usuário
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Calcular metas se não foram definidas
    if created or profile.daily_calories == 2000:
        try:
            profile.daily_calories = profile.calculate_daily_calories()
            protein, carbs, fat = profile.calculate_macros()
            profile.protein_goal = protein
            profile.carbs_goal = carbs
            profile.fat_goal = fat
            profile.save()
        except Exception as e:
            # Se houver erro no cálculo, usar valores padrão
            profile.daily_calories = 2000
            profile.protein_goal = 150
            profile.carbs_goal = 250
            profile.fat_goal = 67
            profile.save()

    # Obter data atual ou da URL
    selected_date = request.GET.get('date', date.today().isoformat())
    try:
        selected_date = date.fromisoformat(selected_date)
    except:
        selected_date = date.today()

    # Obter refeições do dia
    meals = Meal.objects.filter(
        user=request.user, date=selected_date).order_by('created_at')

    # Obter dados nutricionais do dia
    daily_nutrition, created = DailyNutrition.objects.get_or_create(
        user=request.user,
        date=selected_date,
        defaults={
            'calories_consumed': 0,
            'calories_burned': 0,
            'protein_consumed': 0,
            'carbs_consumed': 0,
            'fat_consumed': 0,
            'fiber_consumed': 0,
            'total_cost': 0
        }
    )

    # Calcular totais das refeições com tratamento de erro
    try:
        total_calories = sum(meal.get_total_calories() for meal in meals)
        total_protein = sum(meal.get_total_protein() for meal in meals)
        total_carbs = sum(meal.get_total_carbs() for meal in meals)
        total_fat = sum(meal.get_total_fat() for meal in meals)
        total_fiber = sum(meal.get_total_fiber() for meal in meals)
        total_cost = sum(meal.get_total_cost() for meal in meals)
    except Exception as e:
        # Se houver erro nos cálculos, usar valores padrão
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        total_fiber = 0
        total_cost = 0

    # Atualizar dados diários
    daily_nutrition.calories_consumed = total_calories
    daily_nutrition.protein_consumed = total_protein
    daily_nutrition.carbs_consumed = total_carbs
    daily_nutrition.fat_consumed = total_fat
    daily_nutrition.fiber_consumed = total_fiber
    daily_nutrition.total_cost = total_cost
    daily_nutrition.save()

    context = {
        'profile': profile,
        'meals': meals,
        'selected_date': selected_date,
        'daily_nutrition': daily_nutrition,
        'total_calories': total_calories,
        'total_protein': total_protein,
        'total_carbs': total_carbs,
        'total_fat': total_fat,
        'total_fiber': total_fiber,
        'total_cost': total_cost,
    }

    return render(request, 'dieta.html', context)


@login_required
def adicionar_exercicio(request):
    return render(request, 'adicionar_exercicio.html')


@login_required
def montar_treino_detalhes(request):
    return render(request, 'montar_treino_detalhes.html')


@login_required
def visualizar_treino(request):
    return render(request, 'visualizar_treino.html')


def logout_view(request):
    logout(request)
    # O 'login' aqui é o nome da URL da página de login
    return redirect('login')


# APIs para o sistema de dieta

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def update_profile(request):
    """Atualiza o perfil do usuário"""
    try:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Verificar se é um FormData (upload de arquivo) ou JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Tratar FormData para upload de foto
            if 'profile_photo' in request.FILES:
                # Aqui você pode processar a foto se necessário
                # Por enquanto, apenas retornamos sucesso
                pass
            
            # Atualizar campos do perfil
            if 'full_name' in request.POST:
                request.user.first_name = request.POST['full_name']
                request.user.save()
            
            if 'birth_date' in request.POST and request.POST['birth_date']:
                from datetime import datetime
                try:
                    birth_date = datetime.strptime(request.POST['birth_date'], '%Y-%m-%d').date()
                    profile.birth_date = birth_date
                except ValueError:
                    pass
            
            if 'gender' in request.POST:
                profile.gender = request.POST['gender']
            
            if 'height' in request.POST and request.POST['height']:
                try:
                    profile.height = int(request.POST['height'])
                except ValueError:
                    pass
            
            if 'weight' in request.POST and request.POST['weight']:
                try:
                    profile.weight = float(request.POST['weight'])
                except ValueError:
                    pass
            
            if 'objective' in request.POST:
                profile.objective = request.POST['objective']
        else:
            # Tratar JSON para atualização de metas
            data = json.loads(request.body)
            
            # Atualizar campos básicos
            if 'first_name' in data:
                request.user.first_name = data['first_name']
                request.user.save()

            if 'birth_date' in data:
                profile.birth_date = data['birth_date']

            if 'height' in data:
                profile.height = data['height']

            if 'weight' in data:
                profile.weight = data['weight']

            if 'objective' in data:
                profile.objective = data['objective']

            # Atualizar metas manualmente se fornecidas
            if 'daily_calories' in data:
                profile.daily_calories = data['daily_calories']

            if 'protein_goal' in data:
                profile.protein_goal = data['protein_goal']

            if 'carbs_goal' in data:
                profile.carbs_goal = data['carbs_goal']

            if 'fat_goal' in data:
                profile.fat_goal = data['fat_goal']

        # Recalcular metas se necessário
        if profile.height and profile.weight and profile.objective:
            profile.daily_calories = profile.calculate_daily_calories()
            protein, carbs, fat = profile.calculate_macros()
            profile.protein_goal = protein
            profile.carbs_goal = carbs
            profile.fat_goal = fat

        profile.save()

        return JsonResponse({
            'success': True,
            'message': 'Perfil atualizado com sucesso!',
            'profile': {
                'first_name': request.user.first_name,
                'birth_date': profile.birth_date.isoformat() if profile.birth_date else None,
                'height': profile.height,
                'weight': float(profile.weight) if profile.weight else None,
                'objective': profile.objective,
                'daily_calories': profile.daily_calories,
                'protein_goal': profile.protein_goal,
                'carbs_goal': profile.carbs_goal,
                'fat_goal': profile.fat_goal,
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
@require_http_methods(["GET"])
def search_foods(request):
    """Busca alimentos"""
    try:
        query = request.GET.get('q', '').lower()
        filter_type = request.GET.get('filter', 'all')

        foods = Food.objects.all()

        # Aplicar filtro de busca
        if query:
            foods = foods.filter(name__icontains=query)

        # Aplicar filtros especiais
        if filter_type == 'favorites':
            try:
                user_foods = UserFood.objects.filter(
                    user=request.user, is_favorite=True)
                foods = foods.filter(userfood__in=user_foods)
            except Exception:
                # Se houver erro, usar todos os alimentos
                pass
        elif filter_type == 'recent':
            try:
                user_foods = UserFood.objects.filter(
                    user=request.user).order_by('-last_used')[:20]
                foods = foods.filter(userfood__in=user_foods)
            except Exception:
                # Se houver erro, usar todos os alimentos
                pass

        # Limitar resultados
        foods = foods[:50]

        food_list = []
        for food in foods:
            try:
                food_list.append({
                    'id': food.id,
                    'name': food.name,
                    'calories_per_100g': food.calories_per_100g,
                    'protein_per_100g': float(food.protein_per_100g),
                    'carbs_per_100g': float(food.carbs_per_100g),
                    'fat_per_100g': float(food.fat_per_100g),
                    'fiber_per_100g': float(food.fiber_per_100g),
                    'sodium_per_100g': food.sodium_per_100g,
                    'estimated_price': float(food.estimated_price),
                    'category': food.category,
                })
            except Exception:
                # Se houver erro com um alimento, pular
                continue

        return JsonResponse({'foods': food_list})
    except Exception as e:
        return JsonResponse({'foods': [], 'error': str(e)})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def add_meal(request):
    """Adiciona uma nova refeição"""
    try:
        data = json.loads(request.body)

        # Criar refeição
        meal = Meal.objects.create(
            user=request.user,
            name=data.get('name', 'Refeição'),
            date=data['date']
        )

        # Adicionar itens da refeição
        for item_data in data.get('items', []):
            try:
                food = Food.objects.get(id=item_data['food_id'])
                quantity = float(item_data.get('quantity', 100))
                
                MealItem.objects.create(
                    meal=meal,
                    food=food,
                    quantity=quantity
                )

                # Atualizar alimentos recentes do usuário
                user_food, created = UserFood.objects.get_or_create(
                    user=request.user,
                    food=food
                )
                user_food.save()  # Atualiza last_used
            except (Food.DoesNotExist, ValueError, TypeError) as e:
                # Se houver erro com um item, continuar com os outros
                continue

        return JsonResponse({
            'success': True,
            'meal_id': meal.id,
            'meal': {
                'id': meal.id,
                'name': meal.name,
                'total_calories': meal.get_total_calories(),
                'total_protein': meal.get_total_protein(),
                'total_carbs': meal.get_total_carbs(),
                'total_fat': meal.get_total_fat(),
                'total_fiber': meal.get_total_fiber(),
                'total_cost': meal.get_total_cost(),
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_meal(request, meal_id):
    """Remove uma refeição"""
    try:
        meal = Meal.objects.get(id=meal_id, user=request.user)
        meal.delete()
        return JsonResponse({'success': True})
    except Meal.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Refeição não encontrada'})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def copy_meal(request, meal_id):
    """Copia uma refeição para outro dia"""
    try:
        data = json.loads(request.body)
        original_meal = Meal.objects.get(id=meal_id, user=request.user)

        # Criar nova refeição
        new_meal = Meal.objects.create(
            user=request.user,
            name=original_meal.name,
            date=data['target_date']
        )

        # Copiar itens
        for item in original_meal.mealitem_set.all():
            MealItem.objects.create(
                meal=new_meal,
                food=item.food,
                quantity=item.quantity
            )

        return JsonResponse({
            'success': True,
            'meal_id': new_meal.id
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def clear_day(request):
    """Limpa todas as refeições de um dia"""
    try:
        data = json.loads(request.body)
        target_date = data['date']

        meals = Meal.objects.filter(user=request.user, date=target_date)
        meals.delete()

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def replicate_day(request):
    """Replica todas as refeições de um dia para outro"""
    try:
        data = json.loads(request.body)
        source_date = data['source_date']
        target_date = data['target_date']

        # Obter refeições do dia fonte
        source_meals = Meal.objects.filter(user=request.user, date=source_date)

        # Copiar para o dia destino
        for meal in source_meals:
            new_meal = Meal.objects.create(
                user=request.user,
                name=meal.name,
                date=target_date
            )

            for item in meal.mealitem_set.all():
                MealItem.objects.create(
                    meal=new_meal,
                    food=item.food,
                    quantity=item.quantity
                )

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def toggle_favorite(request, food_id):
    """Alterna favorito de um alimento"""
    try:
        user_food, created = UserFood.objects.get_or_create(
            user=request.user,
            food_id=food_id
        )
        user_food.is_favorite = not user_food.is_favorite
        user_food.save()

        return JsonResponse({
            'success': True,
            'is_favorite': user_food.is_favorite
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def populate_sample_foods(request):
    """Popula o banco com alimentos de exemplo"""
    sample_foods = [
        {
            'name': 'Arroz Branco Cozido',
            'calories_per_100g': 130,
            'protein_per_100g': 2.7,
            'carbs_per_100g': 28.0,
            'fat_per_100g': 0.3,
            'fiber_per_100g': 0.4,
            'sodium_per_100g': 1,
            'estimated_price': 0.50,
            'category': 'cereais'
        },
        {
            'name': 'Frango Grelhado',
            'calories_per_100g': 165,
            'protein_per_100g': 31.0,
            'carbs_per_100g': 0.0,
            'fat_per_100g': 3.6,
            'fiber_per_100g': 0.0,
            'sodium_per_100g': 74,
            'estimated_price': 8.00,
            'category': 'proteinas'
        },
        {
            'name': 'Brócolis',
            'calories_per_100g': 34,
            'protein_per_100g': 2.8,
            'carbs_per_100g': 7.0,
            'fat_per_100g': 0.4,
            'fiber_per_100g': 2.6,
            'sodium_per_100g': 33,
            'estimated_price': 3.50,
            'category': 'vegetais'
        },
        {
            'name': 'Banana',
            'calories_per_100g': 89,
            'protein_per_100g': 1.1,
            'carbs_per_100g': 23.0,
            'fat_per_100g': 0.3,
            'fiber_per_100g': 2.6,
            'sodium_per_100g': 1,
            'estimated_price': 2.00,
            'category': 'frutas'
        },
        {
            'name': 'Ovo Cozido',
            'calories_per_100g': 155,
            'protein_per_100g': 13.0,
            'carbs_per_100g': 1.1,
            'fat_per_100g': 11.0,
            'fiber_per_100g': 0.0,
            'sodium_per_100g': 124,
            'estimated_price': 1.50,
            'category': 'proteinas'
        }
    ]
    
    for food_data in sample_foods:
        Food.objects.get_or_create(
            name=food_data['name'],
            defaults=food_data
        )
    
    return JsonResponse({'success': True, 'message': 'Alimentos de exemplo adicionados!'})
