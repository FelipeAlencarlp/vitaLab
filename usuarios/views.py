from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

def cadastro(request):
    if request.user.is_authenticated:
        return redirect('/exames/solicitar_exames/')

    return render(request, 'cadastro.html')


def valida_cadastro(request):
    if request.method == 'POST':
        primeiro_nome = request.POST.get('primeiro_nome')
        ultimo_nome = request.POST.get('ultimo_nome')
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        email = request.POST.get('email')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not senha == confirmar_senha:
            messages.add_message(request, messages.ERROR, 'As senhas não conferem.')
            return redirect('/auth/cadastro/')

        if len(senha) < 6:
            messages.add_message(request, messages.WARNING, 'A senha deve conter no mínimo 6 caracteres.')
            return redirect('/auth/cadastro/')

        if User.objects.filter(username=username).exists():
            messages.add_message(request, messages.WARNING, 'Esse usuário já existe! Por favor, escolha outro.')
            return redirect('/auth/cadastro/')
        
        if User.objects.filter(email=email).exists():
            messages.add_message(request, messages.WARNING, 'Esse e-mail já está em uso! Por favor, escolha outro.')
            return redirect('/auth/cadastro/')

        try:
            usuario = User.objects.create_user(
                first_name=primeiro_nome,
                last_name=ultimo_nome,
                username=username,
                email=email,
                password=senha
            )
            usuario.save()
            
            messages.add_message(request, messages.SUCCESS, 'Cadastro realizado com sucesso!')
            return redirect('/auth/login/')
        
        except:
            messages.add_message(request, messages.ERROR, 'Erro interno do sistema! Contate um Administrador.')
            return redirect('/auth/cadastro/')


def logar(request):
    if request.user.is_authenticated:
        return redirect('/exames/solicitar_exames/')
    
    return render(request, 'login.html')


def valida_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        usuarioExiste = authenticate(username=username, password=senha)

        if usuarioExiste:
            login(request, usuarioExiste)
            return redirect('/exames/solicitar_exames/')
        
        messages.add_message(request, messages.ERROR, 'Usuário ou senha inválido.')
        return redirect('/auth/login/')


