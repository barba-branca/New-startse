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
    # Verifica se usuário está autenticado
    if not request.user.is_authenticated:
        messages.add_message(request, constants.ERROR, 'Você precisa estar logado para fazer uma proposta.')
        return redirect('/usuarios/logar')
    
    # Verifica se é POST
    if request.method != 'POST':
        return redirect(f'/investidores/ver_empresa/{id}')
    
    valor = request.POST.get('valor')
    percentual = request.POST.get('percentual')
    
    # Valida campos obrigatórios
    if not valor or not percentual:
        messages.add_message(request, constants.WARNING, 'Valor e percentual são obrigatórios.')
        return redirect(f'/investidores/ver_empresa/{id}')
    
    try:
        # Busca a empresa
        empresa = Empresas.objects.get(id=id)
        
        # Converte valores
        valor_float = float(valor)
        percentual_float = float(percentual)
        
        # Validações básicas
        if valor_float <= 0:
            messages.add_message(request, constants.WARNING, 'O valor deve ser maior que zero.')
            return redirect(f'/investidores/ver_empresa/{id}')
        
        if percentual_float <= 0:
            messages.add_message(request, constants.WARNING, 'O percentual deve ser maior que zero.')
            return redirect(f'/investidores/ver_empresa/{id}')
        
        # Calcula propostas já aceitas
        propostas_aceitas = PropostaInvestimento.objects.filter(empresa=empresa, status='PA')
        total = sum(pa.percentual for pa in propostas_aceitas)

        if total + percentual_float > empresa.percentual_equity:
            messages.add_message(request, constants.WARNING, 'O percentual solicitado ultrapassa o percentual máximo disponível.')
            return redirect(f'/investidores/ver_empresa/{id}')
        
        # Calcula valuation proposto
        valuation = (100 * valor_float) / percentual_float
        
        # Verifica se valuation é aceitável (mínimo 50% do valuation da empresa)
        valuation_minimo = empresa.valuation / 2
        if valuation < valuation_minimo:
            messages.add_message(request, constants.WARNING, f'Seu valuation proposto foi R${valuation:.2f} e deve ser no mínimo R${valuation_minimo:.2f}')
            return redirect(f'/investidores/ver_empresa/{id}')
        
        # Cria a proposta
        pi = PropostaInvestimento(
            valor=valor_float,
            percentual=percentual_float,
            empresa=empresa,
            investidor=request.user
        )
        
        pi.save()
        messages.add_message(request, constants.SUCCESS, 'Proposta criada com sucesso! Agora assine o contrato.')
        return redirect(f'/investidores/assinar_contrato/{pi.id}')
        
    except Empresas.DoesNotExist:
        messages.add_message(request, constants.ERROR, 'Empresa não encontrada.')
        return redirect('/investidores/sugestao')
    except ValueError:
        messages.add_message(request, constants.WARNING, 'Valor ou percentual inválido. Use apenas números.')
        return redirect(f'/investidores/ver_empresa/{id}')
    except Exception as e:
        # Log do erro para debugging
        print(f"[ERRO PROPOSTA] {type(e).__name__}: {str(e)}")
        messages.add_message(request, constants.ERROR, f'Erro ao criar proposta: {type(e).__name__}')
        return redirect(f'/investidores/ver_empresa/{id}')


def assinar_contrato(request, id):
    # Verifica autenticação
    if not request.user.is_authenticated:
        messages.add_message(request, constants.ERROR, 'Você precisa estar logado.')
        return redirect('/usuarios/logar')
    
    try:
        pi = PropostaInvestimento.objects.get(id=id)
    except PropostaInvestimento.DoesNotExist:
        messages.add_message(request, constants.ERROR, 'Proposta não encontrada.')
        return redirect('/investidores/sugestao')
    
    # Verifica se o usuário é o dono da proposta
    if pi.investidor != request.user:
        messages.add_message(request, constants.ERROR, 'Você não tem permissão para acessar esta proposta.')
        return redirect('/investidores/sugestao')
    
    # Verifica se a proposta ainda pode ser assinada
    if pi.status != 'AS':
        messages.add_message(request, constants.WARNING, 'Esta proposta já foi processada.')
        return redirect(f'/investidores/ver_empresa/{pi.empresa.id}')
            
    if request.method == 'GET':
        return render(request, 'assinar_contrato.html', {'pi': pi})
    
    elif request.method == 'POST':
        selfie = request.FILES.get('selfie')
        rg = request.FILES.get('rg')
        aceite = request.POST.get('aceite')
        
        # Valida se os arquivos foram enviados
        if not selfie:
            messages.add_message(request, constants.WARNING, 'Por favor, envie a selfie com o documento.')
            return render(request, 'assinar_contrato.html', {'pi': pi})
        
        if not rg:
            messages.add_message(request, constants.WARNING, 'Por favor, envie o documento de identidade.')
            return render(request, 'assinar_contrato.html', {'pi': pi})
        
        # Valida se aceitou os termos
        if not aceite:
            messages.add_message(request, constants.WARNING, 'Você precisa aceitar os termos do contrato.')
            return render(request, 'assinar_contrato.html', {'pi': pi})
        
        # Valida tamanho dos arquivos (máx 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if selfie.size > max_size:
            messages.add_message(request, constants.WARNING, 'A selfie deve ter no máximo 5MB.')
            return render(request, 'assinar_contrato.html', {'pi': pi})
        
        if rg.size > max_size:
            messages.add_message(request, constants.WARNING, 'O documento deve ter no máximo 5MB.')
            return render(request, 'assinar_contrato.html', {'pi': pi})
        
        try:
            # Salva os arquivos
            pi.selfie = selfie
            pi.rg = rg
            pi.status = 'PE'  # Proposta Enviada
            pi.save()
            
            # Realiza verificação KYC
            realizar_kyc(request.user)
            
            messages.add_message(request, constants.SUCCESS, 
                'Contrato assinado com sucesso! Sua proposta foi enviada para análise da empresa.')
            return redirect(f'/investidores/ver_empresa/{pi.empresa.id}')
            
        except Exception as e:
            print(f"[ERRO ASSINATURA] {type(e).__name__}: {str(e)}")
            messages.add_message(request, constants.ERROR, 'Erro ao processar assinatura. Tente novamente.')
            return render(request, 'assinar_contrato.html', {'pi': pi})


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
