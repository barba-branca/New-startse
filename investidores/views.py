from django.shortcuts import render
from empresarios.models import Empresas, Documento
from django.http import HttpResponse, Http404
from .models import PropostaInvestimento
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.messages import constants

def sugestao(request):
    areas = Empresas.area_choices
    if request.method == "GET":
        return render(request, 'sugestao.html', {'areas': areas})
    elif request.method == 'POST':
        tipo = request.POST. get('tipo')
        area = request.POST.getlist('area')
        valor = request.POST.get('valor')
<<<<<<< HEAD
        
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

=======

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
    
>>>>>>> 1892e8bffbb807089d8216fc51bce544130b65d9
def ver_empresa(request, id):
    empresa = Empresas.objects.get(id=id)
    documentos = Documento.objects.filter(empresa=empresa)
    # TODO: Listar as metricas dinamicamente
    return render(request, 'ver_empresa.html', {'empresa': empresa, 'documentos': documentos})

def realizar_proposta(request, id):
    valor = request.POST.get('valor')
    percentual = request.POST.get('percentual')
    empresa = Empresas.objects.get(id=id)
<<<<<<< HEAD
=======


>>>>>>> 1892e8bffbb807089d8216fc51bce544130b65d9
    
    propostas_aceitas = PropostaInvestimento.objects.filter(empresa=empresa).filter(status='PA')
    
    total = 0
    for pa in propostas_aceitas:
        total = total + pa.percentual
<<<<<<< HEAD
    
=======
       
>>>>>>> 1892e8bffbb807089d8216fc51bce544130b65d9
    if total + float(percentual) > empresa.percentual_equity:
        messages.add_message(request, constants.WARNING, 'O percentual solicitado ultrapassa o percentual maximo.')
        return redirect(f'/investidores/ver_empresa/{id}')
    
    valuation = (100 * int(valor)) / int (percentual)
<<<<<<< HEAD
        
        
    if valuation < (int(empresa.valuation / 2)):
        messages.add_message(request, constants.WARNING, f'Seu valuation proposto foi R${valuation} e deve ser no mínimo {empresa.valuation / 2}')
=======

        
        
    if valuation < (int(empresa.valuation / 2)):
        messages.add_message(request, constants.WARNING, f'Seu valuation proposto foi R${valuation} e deve ser no mínimo {empresa.valuation / 2 }')
>>>>>>> 1892e8bffbb807089d8216fc51bce544130b65d9
        return redirect(f'/investidores/ver_empresa/{id}')
        
    pi = PropostaInvestimento(
        valor=valor,
        percentual=percentual,
        empresa=empresa,
        investidor=request.user
    )
    
<<<<<<< HEAD
    pi.save()
    return redirect(f'/investidores/assinar_contrato/{pi.id}') 
=======
    
    

    pi.save()
    return redirect(f'/investidores/assinar_contrato/{pi.id}') # vai dar erro por enquanto
>>>>>>> 1892e8bffbb807089d8216fc51bce544130b65d9

def assinar_contrato(request, id):
    pi = PropostaInvestimento.objects.get(id=id)
    if pi.status != 'AS':
        raise Http404()
            
    if request.method == 'GET':
        return render(request, 'assinar_contrato.html', {'pi' : pi})
    
<<<<<<< HEAD
    #implementar inteligencia artificial para validar a self e o rg se é verdadeiro
    
=======
>>>>>>> 1892e8bffbb807089d8216fc51bce544130b65d9
    elif request.method == 'POST':
        selfie = request.FILES.get('selfie')
        rg = request.FILES.get('rg')
        
        pi.selfie = selfie
        pi.rg = rg
        pi.status = 'PE'
        pi.save()
        messages.add_message(request, constants.SUCCESS, f'Contrato assinado com sucesso, sua proposta foi enviada a empresa.')
        return redirect(f'/investidores/ver_empresa/{pi.empresa.id}')