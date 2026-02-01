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
