# 📋 ROTEIRO DE IMPLEMENTAÇÃO - NEW START MVP

**Autor:** Barba-Branca  
**Data:** 01/02/2026  
**Versão:** 1.0

---

## 📌 VISÃO GERAL

Este documento contém o roteiro completo para implementação das funcionalidades críticas do MVP da plataforma New Start.

---

## 🎯 1. REFATORAÇÃO E UI CLEANUP

### 1.1 Correção de Conflitos de Merge ✅
**Arquivo:** `investidores/templates/assinar_contrato.html`
- Remover marcadores `<<<<<<< HEAD`, `=======`, `>>>>>>> hash`
- Status: **A IMPLEMENTAR**

### 1.2 Substituição de Lorem Ipsum ✅
**Arquivo:** `investidores/templates/assinar_contrato.html`
- Substituir por texto jurídico de Mútuo Conversível
- Status: **A IMPLEMENTAR**

### 1.3 Empty States para Dashboard
- Criar componente quando Valuation = 0
- Exibir CTA "Comece sua jornada"
- Status: **A IMPLEMENTAR**

---

## 🤖 2. INTELIGÊNCIA ARTIFICIAL (KAMILA AI)

### 2.1 Arquivo: `empresarios/utils.py`
```python
def analisar_com_ia(empresa):
    """
    Análise de Venture Capital usando IA.
    Avalia: Escalabilidade, Saúde Financeira, Riscos de Mercado.
    Retorna JSON estruturado.
    """
```

### 2.2 Prompt da Kamila
```
Você é a Kamila, uma analista sênior de Venture Capital da New Start.
Analise a empresa com base nos seguintes critérios:

1. ESCALABILIDADE (0-100): Potencial de crescimento exponencial
2. SAÚDE FINANCEIRA (0-100): Solidez e gestão financeira
3. RISCOS DE MERCADO (0-100): Vulnerabilidades e ameaças

Retorne APENAS um JSON válido no formato:
{
  "escalabilidade": {"score": 0, "analise": "..."},
  "saude_financeira": {"score": 0, "analise": "..."},
  "riscos": {"score": 0, "analise": "..."},
  "recomendacao_geral": "...",
  "pontos_fortes": ["...", "..."],
  "pontos_atencao": ["...", "..."]
}
```

---

## 📊 3. MOTOR FINANCEIRO (VALUATION DCF)

### 3.1 Fórmula DCF
$$V = \sum_{t=1}^{n} \frac{FCF_t}{(1 + r)^t}$$

### 3.2 Implementação Python
```python
def calcular_valuation_dcf(fluxos_caixa: list, taxa_desconto: float, anos: int = 5):
    """
    Calcula o valuation usando Fluxo de Caixa Descontado.
    
    Args:
        fluxos_caixa: Lista de FCF projetados por ano
        taxa_desconto: Taxa de desconto (WACC ou taxa mínima)
        anos: Período de projeção
    
    Returns:
        Valor presente total (Valuation)
    """
    valor_presente = 0
    for t, fcf in enumerate(fluxos_caixa, 1):
        valor_presente += fcf / ((1 + taxa_desconto) ** t)
    return valor_presente
```

### 3.3 Projeção de Crescimento
```python
def projetar_crescimento(valor_inicial: float, taxa_crescimento: float, anos: int):
    """
    Projeta o crescimento do fluxo de caixa.
    """
    projecoes = []
    valor_atual = valor_inicial
    for ano in range(1, anos + 1):
        valor_atual *= (1 + taxa_crescimento)
        projecoes.append({
            'ano': ano,
            'valor': round(valor_atual, 2),
            'label': f'Ano {ano}'
        })
    return projecoes
```

---

## 🔐 4. DATA ROOM SEGURO

### 4.1 Modelo de Documento Protegido
```python
class DocumentoDataRoom(models.Model):
    empresa = models.ForeignKey(Empresas, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    arquivo = models.FileField(upload_to='dataroom/')
    tipo = models.CharField(choices=[
        ('DRE', 'Demonstração de Resultados'),
        ('BP', 'Balanço Patrimonial'),
        ('PLANILHA', 'Planilha Financeira'),
        ('CONTRATO', 'Contrato'),
        ('OUTRO', 'Outro')
    ])
    privado = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
```

### 4.2 Signed URL (Azure Blob Storage)
```python
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta

def gerar_url_temporaria(documento, tempo_expiracao_minutos=30):
    """
    Gera URL temporária para visualização do documento.
    Somente investidores com Match aprovado têm acesso.
    """
    sas_token = generate_blob_sas(
        account_name=settings.AZURE_ACCOUNT_NAME,
        container_name=settings.AZURE_CONTAINER_NAME,
        blob_name=documento.arquivo.name,
        account_key=settings.AZURE_ACCOUNT_KEY,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(minutes=tempo_expiracao_minutos)
    )
    return f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_CONTAINER_NAME}/{documento.arquivo.name}?{sas_token}"
```

---

## ✍️ 5. ASSINATURA DIGITAL

### 5.1 Modelo de Contrato
```python
class ContratoDigital(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('SENT', 'Enviado para Assinatura'),
        ('SIGNED', 'Assinado'),
        ('REJECTED', 'Rejeitado'),
        ('EXPIRED', 'Expirado')
    ]
    
    proposta = models.ForeignKey(PropostaInvestimento, on_delete=models.CASCADE)
    documento_id_externo = models.CharField(max_length=100, blank=True)  # ID ZapSign/Clicksign
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    url_assinatura = models.URLField(blank=True)
    assinado_em = models.DateTimeField(null=True, blank=True)
```

### 5.2 Integração com ZapSign
```python
import requests

class ZapSignService:
    BASE_URL = "https://api.zapsign.com.br/api/v1"
    
    def __init__(self, api_token):
        self.headers = {"Authorization": f"Bearer {api_token}"}
    
    def criar_documento(self, contrato, investidor, empresario):
        payload = {
            "name": f"Contrato Mútuo Conversível - {contrato.proposta.empresa.nome}",
            "signers": [
                {"name": investidor.get_full_name(), "email": investidor.email},
                {"name": empresario.get_full_name(), "email": empresario.email}
            ],
            "template_id": settings.ZAPSIGN_TEMPLATE_ID
        }
        response = requests.post(f"{self.BASE_URL}/docs", json=payload, headers=self.headers)
        return response.json()
```

### 5.3 Webhook para Status
```python
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def webhook_assinatura(request):
    """
    Endpoint para receber atualizações de status da ZapSign/Clicksign.
    """
    data = json.loads(request.body)
    documento_id = data.get('document_id')
    status = data.get('status')
    
    try:
        contrato = ContratoDigital.objects.get(documento_id_externo=documento_id)
        if status == 'signed':
            contrato.status = 'SIGNED'
            contrato.assinado_em = timezone.now()
        contrato.save()
        return JsonResponse({'success': True})
    except ContratoDigital.DoesNotExist:
        return JsonResponse({'error': 'Contrato não encontrado'}, status=404)
```

---

## 📁 ARQUIVOS A CRIAR/MODIFICAR

| Arquivo | Ação | Descrição |
|---------|------|-----------|
| `investidores/templates/assinar_contrato.html` | Modificar | Remover conflitos e Lorem Ipsum |
| `empresarios/utils.py` | Adicionar | Funções de IA e Valuation DCF |
| `empresarios/models.py` | Adicionar | Campos de análise IA e Data Room |
| `investidores/models.py` | Adicionar | Modelo ContratoDigital |
| `empresarios/templates/empresa.html` | Modificar | Empty state quando valuation=0 |
| `core/webhooks.py` | Criar | Endpoints para webhooks |
| `core/urls.py` | Modificar | Adicionar rotas de webhook |

---

## 🔄 ORDEM DE IMPLEMENTAÇÃO

1. **Fase 1 - Limpeza** (30 min)
   - Corrigir conflitos de merge
   - Substituir Lorem Ipsum por texto jurídico

2. **Fase 2 - Motor Financeiro** (1h)
   - Implementar cálculo DCF
   - Criar projeções de crescimento

3. **Fase 3 - Kamila AI** (1h30)
   - Implementar função de análise IA
   - Criar endpoint para chamada assíncrona

4. **Fase 4 - Data Room** (1h)
   - Criar modelo de documento seguro
   - Implementar Signed URLs

5. **Fase 5 - Assinatura Digital** (2h)
   - Integrar API ZapSign
   - Configurar webhooks

---

**Total estimado:** 6 horas de desenvolvimento
