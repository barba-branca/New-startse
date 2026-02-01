"""
Views para Webhooks e Data Room
New Start - Plataforma de Captação de Investimentos
"""

import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import DocumentoDataRoom, ContratoDigital, AcessoDocumento
from .services import (
    verificar_acesso_dataroom,
    registrar_acesso_documento,
    gerar_url_temporaria_local,
    processar_webhook_zapsign
)


# =============================================================================
# WEBHOOKS - ASSINATURA DIGITAL
# =============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def webhook_zapsign(request):
    """
    Endpoint para receber webhooks do ZapSign.
    
    URL: /api/webhooks/zapsign/
    
    O ZapSign envia notificações quando:
    - Documento é assinado
    - Documento é recusado
    - Documento expira
    - Todas as assinaturas são concluídas
    """
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    resultado = processar_webhook_zapsign(payload)
    
    if resultado.get('sucesso'):
        return JsonResponse({'status': 'ok', 'resultado': resultado}, status=200)
    else:
        return JsonResponse({'status': 'error', 'erro': resultado.get('erro')}, status=200)


@csrf_exempt
@require_http_methods(["POST"])
def webhook_clicksign(request):
    """
    Endpoint para receber webhooks do Clicksign.
    
    URL: /api/webhooks/clicksign/
    
    Nota: Implementação similar ao ZapSign, ajustar payload conforme documentação.
    """
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # Clicksign usa formato diferente, fazer mapeamento
    payload_normalizado = {
        'event_type': payload.get('event', {}).get('name'),
        'doc_token': payload.get('document', {}).get('key'),
        'signer': {
            'email': payload.get('event', {}).get('data', {}).get('signer', {}).get('email')
        }
    }
    
    resultado = processar_webhook_zapsign(payload_normalizado)
    
    return JsonResponse({'status': 'received'}, status=200)


# =============================================================================
# DATA ROOM - ACESSO A DOCUMENTOS
# =============================================================================

@login_required
def listar_documentos_dataroom(request, empresa_id):
    """
    Lista documentos do Data Room disponíveis para o investidor.
    
    Retorna apenas documentos que o investidor tem permissão para ver.
    """
    from empresarios.models import Empresas
    
    empresa = get_object_or_404(Empresas, id=empresa_id)
    
    # Verifica se tem permissão
    if not verificar_acesso_dataroom(request.user, empresa):
        return JsonResponse({
            'erro': 'Você não tem permissão para acessar o Data Room desta empresa.',
            'motivo': 'É necessário ter uma proposta aceita ou em negociação.'
        }, status=403)
    
    documentos = DocumentoDataRoom.objects.filter(empresa=empresa)
    
    # Se não for o dono da empresa, filtra apenas públicos ou se tiver match
    if empresa.user != request.user:
        documentos = documentos.filter(privado=False) | documentos.filter(privado=True)
    
    dados = []
    for doc in documentos:
        dados.append({
            'id': doc.id,
            'titulo': doc.titulo,
            'descricao': doc.descricao,
            'tipo': doc.get_tipo_display(),
            'privado': doc.privado,
            'criado_em': doc.criado_em.isoformat(),
            'pode_acessar': True
        })
    
    return JsonResponse({
        'empresa': empresa.nome,
        'total': len(dados),
        'documentos': dados
    })


@login_required
def acessar_documento_dataroom(request, documento_id):
    """
    Gera URL temporária para acesso ao documento.
    
    Registra o acesso para auditoria.
    """
    documento = get_object_or_404(DocumentoDataRoom, id=documento_id)
    
    # Verifica permissão
    if not verificar_acesso_dataroom(request.user, documento.empresa):
        return JsonResponse({
            'erro': 'Acesso negado a este documento.',
        }, status=403)
    
    # Registra o acesso
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
    registrar_acesso_documento(documento, request.user, ip)
    
    # Gera URL temporária
    url = gerar_url_temporaria_local(documento)
    
    return JsonResponse({
        'documento': documento.titulo,
        'url': url,
        'expira_em': '30 minutos',
        'aviso': 'Esta URL é temporária e para uso exclusivo do investidor autenticado.'
    })


# =============================================================================
# CONTRATOS - GERENCIAMENTO
# =============================================================================

@login_required
def status_contrato(request, contrato_id):
    """
    Retorna o status atual de um contrato digital.
    """
    contrato = get_object_or_404(ContratoDigital, id=contrato_id)
    
    # Verifica se o usuário é parte do contrato
    if request.user not in [contrato.proposta.investidor, contrato.proposta.empresa.user]:
        return JsonResponse({'erro': 'Acesso negado'}, status=403)
    
    return JsonResponse({
        'id': contrato.id,
        'tipo': contrato.get_tipo_contrato_display(),
        'status': contrato.get_status_display(),
        'empresa': contrato.proposta.empresa.nome,
        'valor': float(contrato.proposta.valor),
        'assinado_investidor': contrato.assinado_investidor_em.isoformat() if contrato.assinado_investidor_em else None,
        'assinado_empresario': contrato.assinado_empresario_em.isoformat() if contrato.assinado_empresario_em else None,
        'finalizado': contrato.esta_totalmente_assinado,
        'url_assinatura_investidor': contrato.url_assinatura_investidor if request.user == contrato.proposta.investidor else None,
        'url_assinatura_empresario': contrato.url_assinatura_empresario if request.user == contrato.proposta.empresa.user else None,
    })


@login_required
def historico_acessos_documento(request, documento_id):
    """
    Lista histórico de acessos a um documento (apenas para o empresário dono).
    """
    documento = get_object_or_404(DocumentoDataRoom, id=documento_id)
    
    # Apenas o dono da empresa pode ver o histórico
    if request.user != documento.empresa.user:
        return JsonResponse({'erro': 'Acesso negado'}, status=403)
    
    acessos = AcessoDocumento.objects.filter(documento=documento)
    
    dados = [{
        'investidor': acesso.investidor.username,
        'email': acesso.investidor.email,
        'data': acesso.data_acesso.isoformat(),
        'ip': acesso.ip_acesso
    } for acesso in acessos]
    
    return JsonResponse({
        'documento': documento.titulo,
        'total_acessos': len(dados),
        'acessos': dados
    })
