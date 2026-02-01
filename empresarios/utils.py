import requests
import os
import re

def validar_digitos_cnpj(cnpj):
    """
    Valida os dígitos verificadores do CNPJ.
    """
    cnpj = re.sub(r'\D', '', cnpj)
    
    if len(cnpj) != 14:
        return False
    
    # Verifica se todos os dígitos são iguais (CNPJs inválidos como 00000000000000)
    if cnpj == cnpj[0] * 14:
        return False
    
    # Calcula o primeiro dígito verificador
    soma = 0
    peso = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for i in range(12):
        soma += int(cnpj[i]) * peso[i]
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    # Calcula o segundo dígito verificador
    soma = 0
    peso = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for i in range(13):
        soma += int(cnpj[i]) * peso[i]
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    return cnpj[12] == str(digito1) and cnpj[13] == str(digito2)


def validar_cnpj_api(cnpj):
    """
    Valida CNPJ consultando APIs.
    Primeiro valida os dígitos verificadores, depois consulta a API para obter dados.
    
    Retorna:
        - dict com dados da empresa se válido
        - None se inválido ou erro na API
    """
    # Remove caracteres não numéricos do CNPJ
    cnpj_limpo = re.sub(r'\D', '', cnpj)
    
    # Verifica se tem 14 dígitos
    if len(cnpj_limpo) != 14:
        return {'erro': 'CNPJ deve ter 14 dígitos', 'valido': False}
    
    # Valida dígitos verificadores
    if not validar_digitos_cnpj(cnpj_limpo):
        return {'erro': 'CNPJ inválido (dígitos verificadores incorretos)', 'valido': False}
    
    # Tenta consultar a Brasil API (gratuita)
    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            dados = response.json()
            return {
                'valido': True,
                'razao_social': dados.get('razao_social', ''),
                'nome_fantasia': dados.get('nome_fantasia', ''),
                'situacao': dados.get('descricao_situacao_cadastral', ''),
                'atividade_principal': dados.get('cnae_fiscal_descricao', ''),
                'data_abertura': dados.get('data_inicio_atividade', ''),
                'uf': dados.get('uf', ''),
                'municipio': dados.get('municipio', ''),
                'dados_completos': dados
            }
        elif response.status_code == 404:
            return {'erro': 'CNPJ não encontrado na base da Receita Federal', 'valido': False}
        else:
            # Em caso de erro da API, ainda permite cadastro se o CNPJ passou na validação de dígitos
            return {'valido': True, 'mensagem': f'API retornou status {response.status_code}. CNPJ validado localmente.'}
            
    except requests.exceptions.Timeout:
        # CNPJ passou na validação de dígitos, permite cadastro
        return {'valido': True, 'mensagem': 'Timeout na consulta - CNPJ validado localmente'}
    except requests.exceptions.RequestException as e:
        # CNPJ passou na validação de dígitos, permite cadastro
        return {'valido': True, 'mensagem': f'Erro na consulta API: {str(e)}. CNPJ validado localmente.'}
    except Exception as e:
        return {'valido': True, 'mensagem': f'Erro inesperado: {str(e)}. CNPJ validado localmente.'}


def realizar_due_diligence(empresa):
    # Simula uma validação automática
    from .models import DueDiligence
    score = 0
    if empresa.tempo_existencia in ['+1', '+5']:
        score += 50
    if empresa.estagio in ['MVPP', 'E']:
        score += 30
    if empresa.valuation > 0:
        score += 20

    status = True if score >= 80 else False

    DueDiligence.objects.create(
        empresa=empresa,
        status_compliance=status,
        score_risco=100-score,
        analise_detalhada="Analise automatica baseada no estagio e tempo de existencia."
    )


# =============================================================================
# MOTOR FINANCEIRO - VALUATION DCF (Discounted Cash Flow)
# =============================================================================

def calcular_valuation_dcf(fluxos_caixa: list, taxa_desconto: float = 0.15) -> dict:
    """
    Calcula o valuation usando o método de Fluxo de Caixa Descontado (DCF).
    
    Fórmula: V = Σ (FCF_t / (1 + r)^t)
    
    Args:
        fluxos_caixa: Lista de fluxos de caixa projetados por ano [FCF_1, FCF_2, ...]
        taxa_desconto: Taxa de desconto (WACC ou taxa mínima de retorno). Default: 15%
    
    Returns:
        dict com valor presente total, detalhamento por ano e métricas
    """
    if not fluxos_caixa:
        return {'valor_presente': 0, 'detalhamento': [], 'erro': 'Nenhum fluxo de caixa informado'}
    
    valor_presente_total = 0
    detalhamento = []
    
    for t, fcf in enumerate(fluxos_caixa, 1):
        fator_desconto = (1 + taxa_desconto) ** t
        valor_presente = fcf / fator_desconto
        valor_presente_total += valor_presente
        
        detalhamento.append({
            'ano': t,
            'fcf_nominal': round(fcf, 2),
            'fator_desconto': round(fator_desconto, 4),
            'valor_presente': round(valor_presente, 2)
        })
    
    return {
        'valor_presente': round(valor_presente_total, 2),
        'taxa_desconto': taxa_desconto,
        'anos_projetados': len(fluxos_caixa),
        'detalhamento': detalhamento
    }


def projetar_crescimento(valor_inicial: float, taxa_crescimento: float, anos: int = 5) -> list:
    """
    Projeta o crescimento do fluxo de caixa ao longo dos anos.
    
    Args:
        valor_inicial: Valor do primeiro ano (FCF atual)
        taxa_crescimento: Taxa de crescimento anual (ex: 0.20 para 20%)
        anos: Número de anos para projetar
    
    Returns:
        Lista de projeções com ano, valor e label para gráficos
    """
    projecoes = []
    valor_atual = valor_inicial
    
    for ano in range(1, anos + 1):
        valor_atual *= (1 + taxa_crescimento)
        projecoes.append({
            'ano': ano,
            'valor': round(valor_atual, 2),
            'label': f'Ano {ano}',
            'crescimento_acumulado': round(((valor_atual / valor_inicial) - 1) * 100, 2)
        })
    
    return projecoes


def calcular_valuation_completo(empresa, faturamento_anual: float, margem_lucro: float = 0.15, 
                                 taxa_crescimento: float = 0.20, taxa_desconto: float = 0.15, 
                                 anos: int = 5) -> dict:
    """
    Calcula o valuation completo de uma empresa usando DCF.
    
    Args:
        empresa: Objeto Empresa do modelo
        faturamento_anual: Faturamento anual atual
        margem_lucro: Margem de lucro líquido (default 15%)
        taxa_crescimento: Crescimento anual esperado (default 20%)
        taxa_desconto: Taxa de desconto/WACC (default 15%)
        anos: Período de projeção (default 5 anos)
    
    Returns:
        dict completo com valuation, projeções e métricas
    """
    # Fluxo de caixa livre = Faturamento * Margem
    fcf_atual = faturamento_anual * margem_lucro
    
    # Projeta os fluxos de caixa futuros
    projecoes = projetar_crescimento(fcf_atual, taxa_crescimento, anos)
    fluxos_caixa = [p['valor'] for p in projecoes]
    
    # Calcula o valuation DCF
    valuation_dcf = calcular_valuation_dcf(fluxos_caixa, taxa_desconto)
    
    # Valuation simples (múltiplo de receita) para comparação
    valuation_multiplo = faturamento_anual * 3  # Múltiplo de 3x receita (comum para startups)
    
    # Valuation do modelo (percentual equity)
    valuation_modelo = empresa.valuation if hasattr(empresa, 'valuation') else 0
    
    return {
        'empresa': {
            'nome': empresa.nome,
            'estagio': empresa.get_estagio_display() if hasattr(empresa, 'get_estagio_display') else '',
            'area': empresa.get_area_display() if hasattr(empresa, 'get_area_display') else ''
        },
        'inputs': {
            'faturamento_anual': faturamento_anual,
            'margem_lucro': margem_lucro,
            'taxa_crescimento': taxa_crescimento,
            'taxa_desconto': taxa_desconto,
            'anos_projecao': anos
        },
        'valuation': {
            'dcf': valuation_dcf['valor_presente'],
            'multiplo_receita': valuation_multiplo,
            'modelo_equity': valuation_modelo,
            'media': round((valuation_dcf['valor_presente'] + valuation_multiplo) / 2, 2)
        },
        'projecoes': projecoes,
        'detalhamento_dcf': valuation_dcf['detalhamento'],
        'grafico_labels': ['Atual'] + [p['label'] for p in projecoes],
        'grafico_valores': [fcf_atual] + [p['valor'] for p in projecoes]
    }


# =============================================================================
# KAMILA AI - ANÁLISE INTELIGENTE DE STARTUPS
# =============================================================================

def get_prompt_kamila(empresa, faturamento: float = None, metricas: list = None) -> str:
    """
    Gera o prompt para a Kamila AI analisar a startup.
    """
    metricas_texto = ""
    if metricas:
        metricas_texto = "\n".join([f"- {m.titulo}: {m.valor}" for m in metricas])
    
    return f"""Você é a KAMILA, uma analista sênior de Venture Capital da plataforma New Start.
Sua missão é analisar startups brasileiras e fornecer insights valiosos para investidores.

## EMPRESA PARA ANÁLISE:

**Nome:** {empresa.nome}
**Área de Atuação:** {empresa.get_area_display() if hasattr(empresa, 'get_area_display') else empresa.area}
**Estágio:** {empresa.get_estagio_display() if hasattr(empresa, 'get_estagio_display') else empresa.estagio}
**Tempo de Existência:** {empresa.get_tempo_existencia_display() if hasattr(empresa, 'get_tempo_existencia_display') else empresa.tempo_existencia}
**Descrição:** {empresa.descricao}
**Valuation Proposto:** R$ {empresa.valuation:,.2f}
**Equity Oferecido:** {empresa.percentual_equity}%
{f'**Faturamento Informado:** R$ {faturamento:,.2f}' if faturamento else ''}
{f'**Métricas:**\n{metricas_texto}' if metricas_texto else ''}

## CRITÉRIOS DE AVALIAÇÃO:

1. **ESCALABILIDADE (0-100):** Avalie o potencial de crescimento exponencial, modelo de negócio, tamanho do mercado endereçável (TAM/SAM/SOM).

2. **SAÚDE FINANCEIRA (0-100):** Avalie a gestão financeira, burn rate implícito, valuation vs. estágio, necessidade de capital.

3. **RISCOS DE MERCADO (0-100):** Avalie concorrência, barreiras de entrada, dependência de fatores externos, riscos regulatórios.

## FORMATO DE RESPOSTA:

Responda APENAS com um JSON válido (sem markdown, sem ```), no seguinte formato exato:

{{"escalabilidade": {{"score": 75, "analise": "Análise detalhada aqui..."}}, "saude_financeira": {{"score": 60, "analise": "Análise detalhada aqui..."}}, "riscos": {{"score": 45, "analise": "Análise detalhada aqui..."}}, "score_geral": 60, "recomendacao": "INVESTIR" ou "ANALISAR" ou "EVITAR", "recomendacao_texto": "Resumo executivo da recomendação...", "pontos_fortes": ["Ponto 1", "Ponto 2", "Ponto 3"], "pontos_atencao": ["Ponto 1", "Ponto 2", "Ponto 3"], "perguntas_investidor": ["Pergunta 1?", "Pergunta 2?", "Pergunta 3?"]}}
"""


def analisar_com_kamila_ai(empresa, faturamento: float = None) -> dict:
    """
    Executa a análise de IA usando Kamila (Gemini ou Ollama).
    
    Args:
        empresa: Objeto Empresa do modelo
        faturamento: Faturamento anual (opcional)
    
    Returns:
        dict com análise completa ou erro
    """
    import json
    
    # Busca métricas da empresa
    try:
        from .models import Metricas
        metricas = list(Metricas.objects.filter(empresa=empresa))
    except:
        metricas = []
    
    prompt = get_prompt_kamila(empresa, faturamento, metricas)
    
    # Tenta usar Gemini primeiro (se configurado)
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            
            # Tenta parsear o JSON da resposta
            texto_resposta = response.text.strip()
            # Remove possíveis marcadores de código
            if texto_resposta.startswith('```'):
                texto_resposta = texto_resposta.split('\n', 1)[1]
            if texto_resposta.endswith('```'):
                texto_resposta = texto_resposta.rsplit('```', 1)[0]
            
            analise = json.loads(texto_resposta)
            analise['fonte'] = 'Gemini'
            analise['sucesso'] = True
            return analise
            
        except json.JSONDecodeError as e:
            return {
                'sucesso': False,
                'erro': f'Erro ao processar resposta da IA: {str(e)}',
                'resposta_raw': response.text if 'response' in dir() else None
            }
        except Exception as e:
            # Se Gemini falhar, tenta Ollama
            pass
    
    # Tenta usar Ollama (local)
    ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
    ollama_model = os.environ.get("OLLAMA_MODEL", "llama3.2")
    
    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": ollama_model,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            texto_resposta = result.get("response", "")
            
            analise = json.loads(texto_resposta)
            analise['fonte'] = 'Ollama'
            analise['sucesso'] = True
            return analise
        else:
            return {
                'sucesso': False,
                'erro': f'Ollama retornou status {response.status_code}'
            }
            
    except requests.exceptions.ConnectionError:
        return {
            'sucesso': False,
            'erro': 'IA não disponível. Configure GEMINI_API_KEY ou inicie o Ollama.',
            'instrucoes': 'Para usar Ollama: 1) Instale em https://ollama.ai 2) Execute: ollama pull llama3.2'
        }
    except json.JSONDecodeError as e:
        return {
            'sucesso': False,
            'erro': f'Erro ao processar resposta: {str(e)}'
        }
    except Exception as e:
        return {
            'sucesso': False,
            'erro': f'Erro inesperado: {str(e)}'
        }


def gerar_relatorio_investimento(empresa, faturamento: float = None) -> dict:
    """
    Gera um relatório completo de investimento combinando Valuation DCF e Análise IA.
    
    Args:
        empresa: Objeto Empresa
        faturamento: Faturamento anual (opcional, usa estimativa se não informado)
    
    Returns:
        dict com relatório completo para o dashboard
    """
    # Se não tiver faturamento, estima baseado no valuation desejado
    if not faturamento:
        faturamento = float(empresa.valor) * 2  # Estimativa conservadora
    
    # Calcula valuation
    valuation_data = calcular_valuation_completo(
        empresa=empresa,
        faturamento_anual=faturamento,
        margem_lucro=0.15,
        taxa_crescimento=0.20,
        taxa_desconto=0.15
    )
    
    # Executa análise IA
    analise_ia = analisar_com_kamila_ai(empresa, faturamento)
    
    return {
        'empresa': empresa.nome,
        'data_geracao': __import__('datetime').datetime.now().isoformat(),
        'valuation': valuation_data,
        'analise_ia': analise_ia,
        'resumo': {
            'valuation_dcf': valuation_data['valuation']['dcf'],
            'score_ia': analise_ia.get('score_geral', 0) if analise_ia.get('sucesso') else None,
            'recomendacao': analise_ia.get('recomendacao', 'N/A') if analise_ia.get('sucesso') else 'Análise IA indisponível'
        }
    }

