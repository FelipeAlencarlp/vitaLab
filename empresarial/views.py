from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models.functions import Concat
from django.db.models import Value
from exames.models import SolicitacaoExame
from django.http import HttpResponse, FileResponse
from .utils import gerar_pdf_exames, gerar_senha_aleatoria


@staff_member_required # somente quem tiver permissão acessa
def gerenciar_clientes(request):
    clientes = User.objects.filter(is_staff=False)

    nome = request.GET.get('nome')
    email = request.GET.get('email')

    if email:
        clientes = clientes.filter(email__contains=email)

    if nome:
        clientes = clientes.annotate(full_name=Concat('first_name', Value(' '), 'last_name')).filter(full_name__contains=nome)

    return render(request, 'gerenciar_clientes.html', {'clientes': clientes})


@staff_member_required 
def cliente(request, cliente_id):
    cliente = User.objects.get(id=cliente_id)
    exames = SolicitacaoExame.objects.filter(usuario=cliente)

    return render(request, 'cliente.html', {'cliente': cliente, 'exames': exames})


@staff_member_required
def exame_cliente(request, exame_id):
    exame = SolicitacaoExame.objects.get(id=exame_id)

    return render(request, 'exame_cliente.html', {'exame': exame})


@staff_member_required
def proxy_pdf(request, exame_id):
    exame = SolicitacaoExame.objects.get(id=exame_id)

    arquivoResponse = exame.resultado.open()

    return HttpResponse(arquivoResponse)


@staff_member_required
def gerar_senha(request, exame_id):
    exame = SolicitacaoExame.objects.get(id=exame_id)

    if exame.senha:
        return FileResponse(gerar_pdf_exames(exame.exame.nome, exame.usuario.first_name, exame.senha), filename="token.pdf")

    exame.senha = gerar_senha_aleatoria(6)
    exame.save()
    return FileResponse(gerar_pdf_exames(exame.exame.nome, exame.usuario.first_name, exame.senha), filename="token.pdf")


@staff_member_required
def alterar_dados_exame(request, exame_id):
    exame = SolicitacaoExame.objects.get(id=exame_id)

    arquivo_pdf = request.FILES.get('resultado')
    status = request.POST.get('status')
    requer_senha = request.POST.get('requer_senha')

    if requer_senha and (not exame.senha):
        messages.add_message(request, messages.ERROR, 'Para exigir a senha é preciso criar uma primeiro!')
        return redirect(f'/empresarial/exame_cliente/{exame_id}')
    
    exame.requer_senha = True if requer_senha else False

    if arquivo_pdf:
        exame.resultado = arquivo_pdf

    exame.status = status

    exame.save()

    messages.add_message(request, messages.SUCCESS, 'Exame alterado com sucesso!')
    return redirect(f'/empresarial/exame_cliente/{exame_id}')