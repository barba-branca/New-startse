from django.shortcuts import render
from empresarios.models import Empresas, Documento, Metricas
from django.http import HttpResponse, Http404
from .models import PropostaInvestimento
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.messages import constants
import mercadopago
import os
import google.generativeai as genai

def sugestao(request):
    areas = Empresas.area_choices
    if request.method == "GET":
        return render(request, 'sugestao.html', {'areas': areas})
    elif request.method == 'POST':
        tipo = request.POST. get('tipo')
        area = request.POST.getlist('area')
        valor = request.POST.get('valor')

        
        if tipo == 'C':
            empresas = Empresas.objects.filter(tempo_existencia='+5').filter(estagio='E')
        
        elif tipo == 'D':
            empresas = Empresas.objects.filter(tempo_existencia__in=['-6', '+6', '+1']).exclude(estagio='E')
        empresas = empresas.filter(area__in=area)
        # TODO: Tipo generico
        empresas_selecionadas =[]
        
        for empresa in empresas:
            percentual = float(valor) * 100 / float(empresa.valuation)
            
            if percentual >= 1:
                empresas_selecionadas.append(empresa)
        return render(request, 'sugestao.html', {'areas': areas, 'empresas': empresas_selecionadas})
    

def ver_empresa(request, id):
    empresa = Empresas.objects.get(id=id)
    documentos = Documento.objects.filter(empresa=empresa)
    metricas = Metricas.objects.filter(empresa=empresa)
    return render(request, 'ver_empresa.html', {'empresa': empresa, 'documentos': documentos, 'metricas': metricas})

def realizar_proposta(request, id):
    valor = request.POST.get('valor')
    percentual = request.POST.get('percentual')
    empresa = Empresas.objects.get(id=id)

    
    propostas_aceitas = PropostaInvestimento.objects.filter(empresa=empresa).filter(status='PA')
    
    total = 0
    for pa in propostas_aceitas:
        total = total + pa.percentual


       

    if total + float(percentual) > empresa.percentual_equity:
        messages.add_message(request, constants.WARNING, 'O percentual solicitado ultrapassa o percentual maximo.')
        return redirect(f'/investidores/ver_empresa/{id}')
    
    try:
        valuation = (100 * float(valor)) / float(percentual)
    except ZeroDivisionError:
        messages.add_message(request, constants.WARNING, f'O percentual não pode ser zero')
        return redirect(f'/investidores/ver_empresa/{id}')
    except ValueError:
        messages.add_message(request, constants.WARNING, f'Valor ou percentual inválido')
        return redirect(f'/investidores/ver_empresa/{id}')
        
    if valuation < (int(empresa.valuation / 2)):
        messages.add_message(request, constants.WARNING, f'Seu valuation proposto foi R${valuation} e deve ser no mínimo {empresa.valuation / 2}')
        return redirect(f'/investidores/ver_empresa/{id}')
        
    pi = PropostaInvestimento(
        valor=valor,
        percentual=percentual,
        empresa=empresa,
        investidor=request.user
    )
    
    pi.save()
    return redirect(f'/investidores/assinar_contrato/{pi.id}')


def assinar_contrato(request, id):
    pi = PropostaInvestimento.objects.get(id=id)
    if pi.status != 'AS':
        raise Http404()
            
    if request.method == 'GET':
        return render(request, 'assinar_contrato.html', {'pi' : pi})
    

    #implementar inteligencia artificial para validar a self e o rg se é verdadeiro
    


    elif request.method == 'POST':
        selfie = request.FILES.get('selfie')
        rg = request.FILES.get('rg')
        
        pi.selfie = selfie
        pi.rg = rg
        pi.status = 'PE'
        pi.save()
        messages.add_message(request, constants.SUCCESS, f'Contrato assinado com sucesso, sua proposta foi enviada a empresa.')
        return redirect(f'/investidores/ver_empresa/{pi.empresa.id}')

def realizar_pagamento(request):
    sdk = mercadopago.SDK(os.environ.get('MERCADO_PAGO_ACCESS_TOKEN'))

    payment_data = {
        "items": [
            {
                "id": "1",
                "title": "Investimento Start-SE",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 100.00  # Valor fixo para teste
            }
        ],
        "back_urls": {
            "success": "http://127.0.0.1:8000/investidores/sucesso",
            "failure": "http://127.0.0.1:8000/investidores/erro",
            "pending": "http://127.0.0.1:8000/investidores/pendente"
        },
        "auto_return": "approved"
    }

    preference_response = sdk.preference().create(payment_data)
    preference = preference_response["response"]

    return redirect(preference["init_point"])

def pagamento_sucesso(request):
    return HttpResponse("<h3>Pagamento realizado com sucesso!</h3>")

def pagamento_erro(request):
    return HttpResponse("<h3>Erro ao realizar o pagamento.</h3>")

def pagamento_pendente(request):
    return HttpResponse("<h3>Pagamento pendente.</h3>")

def realizar_analise_ia(request, id):
    api_key = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)

    empresa = Empresas.objects.get(id=id)

    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    Analise a seguinte empresa para um investidor:
    Nome: {empresa.nome}
    Área: {empresa.get_area_display()}
    Descrição: {empresa.descricao}
    Estágio: {empresa.get_estagio_display()}
    Valuation Esperado: {empresa.valuation}

    Dê 3 pontos positivos e 3 pontos de atenção para investir nesta empresa.
    """

    response = model.generate_content(prompt)

    return render(request, 'analise_ia.html', {'analysis': response.text, 'empresa': empresa})
