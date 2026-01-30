import requests
import re

def consultar_cnpj(cnpj):
    # Remove all non-digit characters
    cnpj = re.sub(r'\D', '', str(cnpj))

    # Check if the CNPJ has 14 digits
    if len(cnpj) != 14:
        return None

    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException:
        return None

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
