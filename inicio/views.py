from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages  # para exibir mensagens (opcional)
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

# Create your views here.


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Antes estava "email"
        senha = request.POST.get('senha')

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
def sobre_sistema(request):
    return render(request, 'sobre_sistema.html')


@login_required
def sobre_desenvolvedores(request):
    return render(request, 'sobre_desenvolvedores.html')


def logout_view(request):
    logout(request)
    # O 'login' aqui é o nome da URL da página de login
    return redirect('login')
