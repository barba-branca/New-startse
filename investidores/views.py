from django.shortcuts import render
from empresarios.models import Empresas, Documento, Metricas
from django.http import HttpResponse, Http404
from .models import PropostaInvestimento
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.messages import constants

import os
import requests
# ============================================================================
# OPÇÃO DE IA: Descomente a linha abaixo para usar Google Gemini ao invés do Ollama
import google.generativeai as genai
# ============================================================================
from .utils import realizar_kyc

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
        realizar_kyc(request.user)
        messages.add_message(request, constants.SUCCESS, f'Contrato assinado com sucesso, sua proposta foi enviada a empresa.')
        return redirect(f'/investidores/ver_empresa/{pi.empresa.id}')


def realizar_analise_ia(request, id):
    """
    Análise de empresa usando IA
    
    OPÇÕES DISPONÍVEIS:
    1. Ollama (Open Source - Local) - Ativo por padrão
    2. Google Gemini (API) - Comentado abaixo
    
    Para usar Gemini ao invés do Ollama:
    1. Descomente o import do genai no topo do arquivo
    2. Comente toda a seção "OLLAMA" abaixo
    3. Descomente toda a seção "GEMINI" abaixo
    4. Configure a variável de ambiente GEMINI_API_KEY
    """
    empresa = Empresas.objects.get(id=id)
    
    prompt = f"""Você é um analista de investimentos especializado em startups e crowdfunding.
    
Analise a seguinte empresa para um potencial investidor:

**Nome:** {empresa.nome}
**Área de Atuação:** {empresa.get_area_display()}
**Descrição:** {empresa.descricao}
**Estágio:** {empresa.get_estagio_display()}
**Valuation Esperado:** R$ {empresa.valuation}

Por favor, forneça uma análise completa incluindo:

## 🟢 3 Pontos Positivos
Liste 3 pontos fortes desta empresa que a tornam atrativa para investimento.

## 🟡 3 Pontos de Atenção  
Liste 3 riscos ou pontos que o investidor deve considerar antes de investir.

## 📊 Recomendação
Dê uma recomendação geral sobre este investimento (Conservador/Moderado/Agressivo).

Responda em português brasileiro de forma clara e profissional."""

    # ============================================================================
    # LÓGICA DE IA: Tenta Gemini primeiro (se tiver API Key), senão usa Ollama
    # ============================================================================
    
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if api_key:
        # USA GOOGLE GEMINI
        try:
            genai.configure(api_key=api_key)
            model_gemini = genai.GenerativeModel("gemini-1.5-flash")
            response = model_gemini.generate_content(prompt)
            analysis = response.text
        except Exception as e:
            analysis = f"Erro ao gerar análise com Gemini: {str(e)}"
    else:
        # USA OLLAMA (Local)
        ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        model_ollama = os.environ.get("OLLAMA_MODEL", "llama3")
        
        try:
            response = requests.post(
                f"{ollama_url}/api/generate",
                json={
                    "model": model_ollama,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result.get("response", "Não foi possível gerar a análise.")
            else:
                analysis = f"Erro ao conectar com Ollama: Status {response.status_code}. Verifique se o Ollama está rodando."
                
        except requests.exceptions.ConnectionError:
            analysis = """⚠️ **Ollama não está rodando!**

Para usar a Análise de IA, siga os passos:

1. **Instale o Ollama:** https://ollama.ai/download
2. **Baixe um modelo:** `ollama pull llama3`
3. **O Ollama rodará automaticamente em segundo plano**

Após isso, a análise funcionará automaticamente."""
        except Exception as e:
            analysis = f"Erro ao gerar análise: {str(e)}"

    return render(request, 'analise_ia.html', {'analysis': analysis, 'empresa': empresa})
