from django.urls import path
from . import views
from . import views_api
from django.shortcuts import render

urlpatterns = [
    # Views existentes
    path('sugestao/', views.sugestao, name="sugestao"),
    path('busca_avancada/', views.busca_avancada, name="busca_avancada"),
    path('painel/', views.painel_investidor, name="painel_investidor"),
    path('ver_empresa/<int:id>', views.ver_empresa, name="ver_empresa"),
    path('realizar_proposta/<int:id>', views.realizar_proposta, name="realizar_proposta"),
    path("assinar_contrato/<int:id>", views.assinar_contrato, name="assinar_contrato"),
    path("realizar_analise_ia/<int:id>", views.realizar_analise_ia, name="realizar_analise_ia"),
    
    # =========================================================================
    # API - Data Room
    # =========================================================================
    path('api/dataroom/<int:empresa_id>/', views_api.listar_documentos_dataroom, name="api_dataroom_lista"),
    path('api/dataroom/documento/<int:documento_id>/', views_api.acessar_documento_dataroom, name="api_dataroom_acesso"),
    path('api/dataroom/documento/<int:documento_id>/acessos/', views_api.historico_acessos_documento, name="api_dataroom_historico"),
    
    # =========================================================================
    # API - Contratos Digitais
    # =========================================================================
    path('api/contrato/<int:contrato_id>/status/', views_api.status_contrato, name="api_contrato_status"),
    
    # =========================================================================
    # Webhooks - Assinatura Digital
    # =========================================================================
    path('api/webhooks/zapsign/', views_api.webhook_zapsign, name="webhook_zapsign"),
    path('api/webhooks/clicksign/', views_api.webhook_clicksign, name="webhook_clicksign"),
]