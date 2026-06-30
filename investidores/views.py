from django.shortcuts import render
from empresarios.models import Empresas, Documento, Metricas
from django.http import HttpResponse, Http404
from .models import PropostaInvestimento
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib.auth.decorators import login_required

import os
import requests
# ============================================================================
# OPÇÃO DE IA: Descomente a linha abaixo para usar Google Gemini ao invés do Ollama
from google import genai
# ============================================================================
from .utils import realizar_kyc

def sugestao(request):
    areas = Empresas.area_choices
    if request.method == "GET":
        return render(request, 'sugestao.html', {'areas': areas})
        
    elif request.method == 'POST':
        tipo = request.POST.get('tipo')
        area = request.POST.getlist('area')
        valor = request.POST.get('valor')
        usar_ia = request.POST.get('usar_ia') == 'on'
        
        # Filtro base: apenas startups com equity > 0
        empresas = Empresas.objects.filter(percentual_equity__gt=0)
        
        if area:
            empresas = empresas.filter(area__in=area)
            
        # Filtrar startups onde o valor do investidor compra pelo menos 1% do valuation
        empresas_candidatas = []
        for empresa in empresas:
            if empresa.valuation > 0:
                percentual = float(valor) * 100 / float(empresa.valuation)
                if percentual >= 1:
                    empresas_candidatas.append(empresa)

        # Regra heurística padrão (fallback)
        empresas_selecionadas = []
        if tipo == 'C':
            for emp in empresas_candidatas:
                if emp.tempo_existencia == '+5' and emp.estagio == 'E':
                    empresas_selecionadas.append(emp)
        elif tipo == 'D':
            for emp in empresas_candidatas:
                if emp.tempo_existencia in ['-6', '+6', '+1'] and emp.estagio != 'E':
                    empresas_selecionadas.append(emp)
        else:
            empresas_selecionadas = empresas_candidatas

        justificativas = {}
        fonte_sugestao = "Regras do Sistema"

        if usar_ia and empresas_candidatas:
            import json
            api_key = os.environ.get("GEMINI_API_KEY")
            
            # Formatar dados das empresas para a IA
            empresas_data = []
            for emp in empresas_candidatas:
                empresas_data.append({
                    "id": emp.id,
                    "nome": emp.nome,
                    "descricao": emp.descricao,
                    "estagio": emp.get_estagio_display(),
                    "area": emp.get_area_display(),
                    "tempo_existencia": emp.get_tempo_existencia_display(),
                    "valuation": float(emp.valuation)
                })

            tipo_ext = "Conservador (busca menos risco e retorno previsível)" if tipo == 'C' else "Despojado (aceita correr riscos elevados para altos retornos)"
            areas_ext = ", ".join([dict(areas).get(a, a) for a in area]) if area else "Qualquer área"
            
            prompt = f"""Você é um analista especialista de investimentos em startups e crowdfunding.
O investidor possui o seguinte perfil de investimento:
- Perfil: {tipo_ext}
- Áreas de interesse: {areas_ext}
- Valor disponível para investimento: R$ {valor}

Aqui está a lista de startups candidatas disponíveis para receber aporte:
{json.dumps(empresas_data, ensure_ascii=False)}

Com base nos dados fornecidos, selecione as melhores startups para recomendar a esse investidor.
Você deve responder estritamente no formato JSON abaixo, sem blocos de código markdown adicionais (como ```json ... ```), sem explicações nem introduções. Apenas retorne o JSON puro contendo uma lista de objetos com o id da empresa e a justificativa de até 2 frases em português brasileiro:

[
  {{
    "id": <id_da_startup>,
    "justificativa": "<justificativa personalizada baseada no perfil do investidor e no segmento da startup>"
  }}
]
"""
            
            if api_key:
                try:
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=prompt
                    )
                    content = response.text.strip()
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.endswith("```"):
                        content = content[:-3]
                    content = content.strip()
                    
                    sugestoes_ia = json.loads(content)
                    empresas_ia_ids = [item['id'] for item in sugestoes_ia]
                    empresas_ia_selecionadas = [emp for emp in empresas_candidatas if emp.id in empresas_ia_ids]
                    
                    if empresas_ia_selecionadas:
                        empresas_selecionadas = empresas_ia_selecionadas
                        for item in sugestoes_ia:
                            justificativas[item['id']] = item['justificativa']
                        fonte_sugestao = "Inteligência Artificial (Gemini)"
                except Exception as e:
                    print(f"[ERRO IA SUGESTAO] {str(e)}")
            else:
                # Fallback para Ollama se Gemini não estiver configurado
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
                        timeout=30
                    )
                    if response.status_code == 200:
                        result = response.json()
                        content = result.get("response", "").strip()
                        if content.startswith("```json"):
                            content = content[7:]
                        if content.endswith("```"):
                            content = content[:-3]
                        content = content.strip()
                        sugestoes_ia = json.loads(content)
                        empresas_ia_ids = [item['id'] for item in sugestoes_ia]
                        empresas_ia_selecionadas = [emp for emp in empresas_candidatas if emp.id in empresas_ia_ids]
                        if empresas_ia_selecionadas:
                            empresas_selecionadas = empresas_ia_selecionadas
                            for item in sugestoes_ia:
                                justificativas[item['id']] = item['justificativa']
                            fonte_sugestao = "Inteligência Artificial (Ollama)"
                except Exception as e:
                    print(f"[ERRO OLLAMA SUGESTAO] {str(e)}")

        # Anexar as justificativas
        for empresa in empresas_selecionadas:
            empresa.justificativa_ia = justificativas.get(empresa.id, None)

        return render(request, 'sugestao.html', {
            'areas': areas,
            'empresas': empresas_selecionadas,
            'usar_ia': usar_ia,
            'fonte_sugestao': fonte_sugestao,
            'tipo_selecionado': tipo,
            'areas_selecionadas': area,
            'valor_selecionado': valor
        })

    

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
        # USA GOOGLE GEMINI (MODERNO)
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
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


def busca_avancada(request):
    from django.db.models import Q, F, ExpressionWrapper, DecimalField
    
    # 1. Recuperar opções para os dropdowns / checkboxes
    areas = Empresas.area_choices
    estagios = Empresas.estagio_choices
    tempos = Empresas.tempo_existencia_choices
    
    # 2. Query base (filtramos apenas empresas com equity > 0 para evitar divisão por zero no valuation)
    empresas = Empresas.objects.filter(percentual_equity__gt=0)
    
    # 3. Capturar filtros da requisição GET
    nome = request.GET.get('nome', '').strip()
    areas_selecionadas = request.GET.getlist('area')
    estagios_selecionados = request.GET.getlist('estagio')
    tempos_selecionados = request.GET.getlist('tempo_existencia')
    
    equity_min = request.GET.get('equity_min', '').strip()
    equity_max = request.GET.get('equity_max', '').strip()
    valor_min = request.GET.get('valor_min', '').strip()
    valor_max = request.GET.get('valor_max', '').strip()
    valuation_min = request.GET.get('valuation_min', '').strip()
    valuation_max = request.GET.get('valuation_max', '').strip()
    
    # 4. Aplicar filtros básicos via ORM
    if nome:
        empresas = empresas.filter(Q(nome__icontains=nome) | Q(descricao__icontains=nome))
        
    if areas_selecionadas:
        empresas = empresas.filter(area__in=areas_selecionadas)
        
    if estagios_selecionados:
        empresas = empresas.filter(estagio__in=estagios_selecionados)
        
    if tempos_selecionados:
        empresas = empresas.filter(tempo_existencia__in=tempos_selecionados)
        
    if equity_min:
        try:
            empresas = empresas.filter(percentual_equity__gte=int(equity_min))
        except ValueError:
            pass
            
    if equity_max:
        try:
            empresas = empresas.filter(percentual_equity__lte=int(equity_max))
        except ValueError:
            pass
            
    if valor_min:
        try:
            empresas = empresas.filter(valor__gte=float(valor_min))
        except ValueError:
            pass
            
    if valor_max:
        try:
            empresas = empresas.filter(valor__lte=float(valor_max))
        except ValueError:
            pass
            
    # 5. Anotação para Valuation dinâmico
    empresas = empresas.annotate(
        val=ExpressionWrapper(
            (F('valor') * 100) / F('percentual_equity'),
            output_field=DecimalField(max_digits=15, decimal_places=2)
        )
    )
    
    # 6. Filtrar por Valuation
    if valuation_min:
        try:
            empresas = empresas.filter(val__gte=float(valuation_min))
        except ValueError:
            pass
            
    if valuation_max:
        try:
            empresas = empresas.filter(val__lte=float(valuation_max))
        except ValueError:
            pass
            
    # 7. Organizar filtros passados de volta para o template para repovoar os campos
    filtros = {
        'nome': nome,
        'areas_selecionadas': areas_selecionadas,
        'estagios_selecionados': estagios_selecionados,
        'tempos_selecionados': tempos_selecionados,
        'equity_min': equity_min,
        'equity_max': equity_max,
        'valor_min': valor_min,
        'valor_max': valor_max,
        'valuation_min': valuation_min,
        'valuation_max': valuation_max,
    }
    
    context = {
        'areas': areas,
        'estagios': estagios,
        'tempos': tempos,
        'filtros': filtros,
        'empresas': empresas,
    }
    
    return render(request, 'busca_avancada.html', context)


@login_required(login_url='/usuarios/logar/')
def painel_investidor(request):
    from django.db.models import Sum
    from .models import PropostaInvestimento, KYC, ContratoDigital
    
    # 1. Obter todas as propostas do investidor
    propostas = PropostaInvestimento.objects.filter(investidor=request.user).order_by('-id')
    
    # 2. Métricas do Portfólio
    total_investido = propostas.filter(status='PA').aggregate(total=Sum('valor'))['total'] or 0
    propostas_pendentes = propostas.filter(status__in=['AS', 'PE']).count()
    startups_apoiadas = propostas.filter(status='PA').values('empresa').distinct().count()
    
    # 3. Status de KYC
    kyc = KYC.objects.filter(investidor=request.user).first()
    
    # 4. Contratos Digitais vinculados
    contratos = ContratoDigital.objects.filter(proposta__investidor=request.user).order_by('-criado_em')
    
    context = {
        'propostas': propostas,
        'total_investido': total_investido,
        'propostas_pendentes': propostas_pendentes,
        'startups_apoiadas': startups_apoiadas,
        'kyc': kyc,
        'contratos': contratos,
    }
    
    return render(request, 'painel_investidor.html', context)

