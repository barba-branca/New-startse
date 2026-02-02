"""
Serviços para Data Room e Assinatura Digital
New Start - Plataforma de Captação de Investimentos
"""

import requests
import hashlib
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone


# =============================================================================
# SERVIÇO DATA ROOM - URLs TEMPORÁRIAS
# =============================================================================

def verificar_acesso_dataroom(investidor, empresa):
    """
    Verifica se o investidor tem permissão para acessar o Data Room da empresa.
    
    Regra: Investidor precisa ter uma proposta aceita (PA) ou em negociação.
    """
    from .models import PropostaInvestimento
    
    propostas_validas = PropostaInvestimento.objects.filter(
        investidor=investidor,
        empresa=empresa,
        status__in=['PA', 'AS', 'PE']  # Aceita, Aguardando Assinatura, ou Proposta Enviada
    ).exists()
    
    return propostas_validas


def registrar_acesso_documento(documento, investidor, ip=None):
    """
    Registra o acesso ao documento para fins de auditoria.
    """
    from .models import AcessoDocumento
    
    AcessoDocumento.objects.create(
        documento=documento,
        investidor=investidor,
        ip_acesso=ip
    )


def gerar_url_temporaria_local(documento, tempo_expiracao_minutos=30):
    """
    Para ambiente local/desenvolvimento: gera uma URL simples.
    Em produção, use gerar_url_temporaria_azure.
    """
    # Em desenvolvimento, retorna a URL do media
    return documento.arquivo.url


def gerar_url_temporaria_azure(documento, tempo_expiracao_minutos=30):
    """
    Gera URL temporária (Signed URL) para documentos armazenados no Azure Blob Storage.
    
    Requer:
        - azure-storage-blob instalado
        - Variáveis de ambiente: AZURE_ACCOUNT_NAME, AZURE_ACCOUNT_KEY, AZURE_CONTAINER_NAME
    """
    try:
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions
        
        account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
        account_key = settings.AZURE_STORAGE_ACCOUNT_KEY
        container_name = settings.AZURE_STORAGE_CONTAINER_NAME
        
        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=container_name,
            blob_name=documento.arquivo.name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(minutes=tempo_expiracao_minutos)
        )
        
        url = f"https://{account_name}.blob.core.windows.net/{container_name}/{documento.arquivo.name}?{sas_token}"
        return url
        
    except ImportError:
        # Se azure-storage-blob não estiver instalado, usa URL local
        return gerar_url_temporaria_local(documento, tempo_expiracao_minutos)
    except Exception as e:
        # Em caso de erro, retorna None
        return None


# =============================================================================
# SERVIÇO ZAPSIGN - ASSINATURA DIGITAL
# =============================================================================

class ZapSignService:
    """
    Integração com a API ZapSign para assinatura digital de contratos.
    
    Documentação: https://docs.zapsign.com.br/
    """
    BASE_URL = "https://api.zapsign.com.br/api/v1"
    
    def __init__(self, api_token=None):
        self.api_token = api_token or settings.ZAPSIGN_API_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def criar_documento_de_template(self, contrato, investidor, empresario, template_id=None):
        """
        Cria um documento para assinatura a partir de um template.
        
        Args:
            contrato: Objeto ContratoDigital
            investidor: Usuário investidor
            empresario: Usuário empresário
            template_id: ID do template no ZapSign (opcional, usa settings se não fornecido)
        
        Returns:
            dict com dados do documento criado
        """
        template_id = template_id or getattr(settings, 'ZAPSIGN_TEMPLATE_ID', None)
        
        if not template_id:
            return {'erro': 'Template ID não configurado'}
        
        payload = {
            "template_id": template_id,
            "signer_name": f"Contrato {contrato.get_tipo_contrato_display()} - {contrato.proposta.empresa.nome}",
            "external_id": str(contrato.id),
            "signers": [
                {
                    "name": investidor.get_full_name() or investidor.username,
                    "email": investidor.email,
                    "auth_mode": "email",
                    "send_automatic_email": True,
                    "order_group": 1
                },
                {
                    "name": empresario.get_full_name() or empresario.username,
                    "email": empresario.email,
                    "auth_mode": "email",
                    "send_automatic_email": True,
                    "order_group": 2
                }
            ],
            "data": [
                {"de": "{{NOME_EMPRESA}}", "para": contrato.proposta.empresa.nome},
                {"de": "{{CNPJ_EMPRESA}}", "para": contrato.proposta.empresa.cnpj},
                {"de": "{{VALOR_INVESTIMENTO}}", "para": f"R$ {contrato.proposta.valor:,.2f}"},
                {"de": "{{PERCENTUAL_EQUITY}}", "para": f"{contrato.proposta.percentual}%"},
                {"de": "{{NOME_INVESTIDOR}}", "para": investidor.get_full_name() or investidor.username},
                {"de": "{{NOME_EMPRESARIO}}", "para": empresario.get_full_name() or empresario.username},
                {"de": "{{DATA_CONTRATO}}", "para": timezone.now().strftime("%d/%m/%Y")}
            ]
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/models/create-doc",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    'sucesso': True,
                    'documento_id': data.get('token') or data.get('doc_id'),
                    'signers': data.get('signers', []),
                    'status': data.get('status'),
                    'dados_completos': data
                }
            else:
                return {
                    'sucesso': False,
                    'erro': f'Erro {response.status_code}: {response.text}'
                }
                
        except requests.exceptions.RequestException as e:
            return {'sucesso': False, 'erro': f'Erro de conexão: {str(e)}'}

    def obter_status_documento(self, documento_id):
        """
        Obtém o status atual de um documento.
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/docs/{documento_id}",
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                return {'sucesso': True, 'dados': response.json()}
            else:
                return {'sucesso': False, 'erro': f'Erro {response.status_code}'}
                
        except requests.exceptions.RequestException as e:
            return {'sucesso': False, 'erro': str(e)}

    def cancelar_documento(self, documento_id):
        """
        Cancela um documento pendente.
        """
        try:
            response = requests.delete(
                f"{self.BASE_URL}/docs/{documento_id}",
                headers=self.headers,
                timeout=15
            )
            
            return {'sucesso': response.status_code in [200, 204]}
            
        except requests.exceptions.RequestException as e:
            return {'sucesso': False, 'erro': str(e)}


# =============================================================================
# PROCESSAMENTO DE WEBHOOKS
# =============================================================================

def processar_webhook_zapsign(payload):
    """
    Processa webhook recebido do ZapSign.
    
    Eventos possíveis:
        - doc_created: Documento criado
        - doc_signed: Assinatura realizada
        - doc_refused: Documento recusado
        - doc_finished: Todas as assinaturas concluídas
    
    Quando o contrato é totalmente assinado (SIGNED):
        - ContratoDigital.status = 'SIGNED'
        - PropostaInvestimento.status = 'PA' (Proposta Aceita/Paga)
    """
    from .models import ContratoDigital, WebhookLog, PropostaInvestimento
    
    evento = payload.get('event_type') or payload.get('event')
    documento_id = payload.get('doc_token') or payload.get('document_id') or payload.get('token')
    
    # Registra o webhook
    log = WebhookLog.objects.create(
        evento=evento or 'unknown',
        payload=payload,
        processado=False
    )
    
    if not documento_id:
        log.erro = 'documento_id não encontrado no payload'
        log.save()
        return {'sucesso': False, 'erro': 'documento_id não encontrado'}
    
    try:
        contrato = ContratoDigital.objects.get(documento_id_externo=documento_id)
        log.contrato = contrato
    except ContratoDigital.DoesNotExist:
        log.erro = f'Contrato não encontrado para documento_id: {documento_id}'
        log.save()
        return {'sucesso': False, 'erro': 'Contrato não encontrado'}
    
    # Processa baseado no evento
    try:
        proposta_atualizada = False
        
        if evento in ['doc_signed', 'signer_signed']:
            # Alguém assinou
            signer_email = payload.get('signer', {}).get('email', '')
            
            if signer_email == contrato.proposta.investidor.email:
                contrato.assinado_investidor_em = timezone.now()
            elif signer_email == contrato.proposta.empresa.user.email:
                contrato.assinado_empresario_em = timezone.now()
            
            # Atualiza status
            if contrato.esta_totalmente_assinado:
                contrato.status = 'SIGNED'
                contrato.finalizado_em = timezone.now()
                
                # IMPORTANTE: Atualiza a PropostaInvestimento para PA (Paga/Aceita)
                contrato.proposta.status = 'PA'
                contrato.proposta.save()
                proposta_atualizada = True
            else:
                contrato.status = 'PARTIAL'
                
        elif evento in ['doc_finished', 'doc_completed']:
            contrato.status = 'SIGNED'
            contrato.finalizado_em = timezone.now()
            
            # IMPORTANTE: Atualiza a PropostaInvestimento para PA (Paga/Aceita)
            contrato.proposta.status = 'PA'
            contrato.proposta.save()
            proposta_atualizada = True
            
        elif evento in ['doc_refused', 'doc_rejected']:
            contrato.status = 'REJECTED'
            
            # Atualiza a PropostaInvestimento para PR (Recusada)
            contrato.proposta.status = 'PR'
            contrato.proposta.save()
            proposta_atualizada = True
            
        elif evento == 'doc_expired':
            contrato.status = 'EXPIRED'
        
        contrato.save()
        
        log.processado = True
        log.processado_em = timezone.now()
        log.save()
        
        return {
            'sucesso': True, 
            'status_contrato': contrato.status,
            'proposta_atualizada': proposta_atualizada,
            'status_proposta': contrato.proposta.status if proposta_atualizada else None
        }
        
    except Exception as e:
        log.erro = str(e)
        log.save()
        return {'sucesso': False, 'erro': str(e)}


def gerar_hash_documento(arquivo):
    """
    Gera hash SHA-256 do documento para validação de integridade.
    """
    hasher = hashlib.sha256()
    
    if hasattr(arquivo, 'read'):
        for chunk in arquivo.chunks():
            hasher.update(chunk)
    else:
        hasher.update(arquivo)
    
    return hasher.hexdigest()
