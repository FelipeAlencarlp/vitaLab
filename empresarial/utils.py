import string
import os
from random import choice, shuffle # choice -> acrescenta caracteres / shuffle -> embaralha a string
from django.conf import settings
from django.template.loader import render_to_string # transforma tags do Django em string
from weasyprint import HTML
from io import BytesIO # cria variável na memória para salvar arquivos como se fosse em disco

def gerar_senha_aleatoria(tamanho):
    caracteres_especiais = string.punctuation
    caracteres_normais = string.ascii_letters
    numros_list = string.digits

    sobra = 0
    quantidade = tamanho // 3

    if not tamanho % 3 == 0:
        sobra = tamanho - quantidade

    letras = ''
    for i in range(0, quantidade + sobra):
        letras += choice(caracteres_normais)

    especiais = ''
    for i in range(0, quantidade):
        especiais += choice(caracteres_especiais)

    numeros = ''
    for i in range(0, quantidade):
        numeros += choice(numros_list)

    senha = list(letras + especiais + numeros)
    shuffle(senha)

    return ''.join(senha)


def gerar_pdf_exames(exame, paciente, senha):
    path_template = os.path.join(settings.BASE_DIR, 'templates/partials/senha_exame.html')
    template_render = render_to_string(path_template, {'exame': exame, 'paciente': paciente, 'senha': senha})

    path_output = BytesIO()
    HTML(string=template_render).write_pdf(path_output)
    path_output.seek(0) # volta o ponteiro para o inicio do arquivo

    return path_output
