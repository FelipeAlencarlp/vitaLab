from django.shortcuts import render, redirect
from .models import TiposExames, SolicitacaoExame, PedidosExames
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib import messages

@login_required
def solicitar_exames(request):
    tipos_exames = TiposExames.objects.all()
    data = datetime.now()

    if request.method == 'GET':
        return render(request, 'solicitar_exames.html', {'tipos_exames': tipos_exames})

    elif request.method == 'POST':
        exames_id = request.POST.getlist('exames') # retorna como lista
        solicitacao_exames = TiposExames.objects.filter(id__in=exames_id)

        # TODO: Calcular preços dos exames disponiveis

        preco_total = 0
        for exame in solicitacao_exames:
            if exame.disponivel:
                preco_total += exame.preco

        return render(request, 'solicitar_exames.html', {'tipos_exames': tipos_exames,
                                                         'solicitacao_exames': solicitacao_exames,
                                                         'preco_total': preco_total,
                                                         'data': data})


@login_required
def fechar_pedido(request):
    exames_id = request.POST.getlist('id_exames')
    solicitacao_exames = TiposExames.objects.filter(id__in=exames_id)

    pedido_exame = PedidosExames(
        usuario=request.user,
        data=datetime.now()
    )

    pedido_exame.save()

    for exame in solicitacao_exames:
        solicitacao_exame_temp = SolicitacaoExame(
            usuario=request.user,
            exame=exame,
            status='E'
        )
        solicitacao_exame_temp.save()
        pedido_exame.exames.add(solicitacao_exame_temp)

    pedido_exame.save()

    messages.add_message(request, messages.SUCCESS, 'Pedido de exames realizado com sucesso! Aguarde confirmação.')
    return redirect('/exames/gerenciar_pedidos/')


@login_required
def gerenciar_pedidos(request):
    pedidos_exames = PedidosExames.objects.filter(usuario=request.user)
    return render(request, 'gerenciar_pedidos.html', {'pedidos_exames': pedidos_exames})


@login_required
def cancelar_pedido(request, pedido_id):
    pedido = PedidosExames.objects.get(id=pedido_id)

    if not pedido.usuario == request.user:
        messages.add_message(request, messages.ERROR, 'Esse pedido não é seu! Impossível cancelar.')
        return redirect('/exames/gerenciar_pedidos/')

    pedido.agendado = False
    pedido.save()

    messages.add_message(request, messages.SUCCESS, 'Pedido cancelado com sucesso!')
    return redirect('/exames/gerenciar_pedidos/')


@login_required
def gerenciar_exames(request):
    exames = SolicitacaoExame.objects.filter(usuario=request.user)
    return render(request, 'gerenciar_exames.html', {'exames': exames})


@login_required
def permitir_abrir_exame(request, exame_id):
    exame = SolicitacaoExame.objects.get(id=exame_id)

    if not exame.requer_senha:
        if not exame.resultado:
            messages.add_message(request, messages.ERROR, 'Não foi possível encontrar o arquivo do exame, por favor contate seu médico.')
            return redirect(f'/exames/gerenciar_exames/')
        
        return redirect(exame.resultado.url)

    return redirect(f'/exames/solicitar_senha_exames/{exame_id}')


@login_required
def solicitar_senha_exames(request, exame_id):
    exame = SolicitacaoExame.objects.get(id=exame_id)
    if request.method == 'GET':
        return render(request, 'solicitar_senha_exames.html', {'exame': exame})
    
    elif request.method == 'POST':
        senha = request.POST.get('senha')

        if senha == exame.senha:
            if not exame.resultado:
                messages.add_message(request, messages.ERROR, 'Não foi possível encontrar o arquivo do exame, por favor contate seu médico.')
                return redirect(f'/exames/solicitar_senha_exames/{exame_id}')
        
            return redirect(exame.resultado.url)
        
        messages.add_message(request, messages.ERROR, 'Senha inválida!')
        return redirect(f'/exames/solicitar_senha_exames/{exame_id}')
