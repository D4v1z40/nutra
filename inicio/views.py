from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def login(request):
    return render(request, 'login.html')
def register(request):
    return render(request, 'register.html')
def perfil(request):
    return render(request, 'perfil.html')
def treino(request):
    return render(request, 'treino.html')
def montar_treino(request):
    return render(request, 'montar_treino.html')