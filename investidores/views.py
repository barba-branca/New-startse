from django.shortcuts import render
from empresarios.models import Empresas, Documento
from django.http import HttpResponse
from .models import PropostaInvestimento
from django.shortcuts import redirect

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
    # TODO: Listar as metricas dinamicamente
    return render(request, 'ver_empresa.html', {'empresa': empresa, 'documentos': documentos})

def realizar_proposta(request, id):
    valor = request.POST.get('valor')
    percentual = request.POST.get('percentual')
    empresa = Empresas.objects.get('id=id')
    
    pi = PropostaInvestimento(
        valor=valor,
        percentual=percentual,
        empresa=empresa,
        investidor=request.user
    )
    
    pi.save()
    return redirect(f'/investidores/assinar_contrato/{pi.id}')