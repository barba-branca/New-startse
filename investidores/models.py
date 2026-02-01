from django.db import models
from empresarios.models import Empresas
from django.contrib.auth.models import User

# Create your models here.

class PropostaInvestimento(models.Model):
    status_choices = (
        ('AS', 'Aguardando assinatura'),
        ('PE', 'Proposta enviada'),
        ('PA', 'Proposta aceita'),
        ('PR', 'Proposta recusada')
    )
    valor = models.DecimalField(max_digits=9, decimal_places=2)
    percentual = models.FloatField()
    empresa = models.ForeignKey(Empresas, on_delete=models.DO_NOTHING)
    investidor = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=2, choices=status_choices, default='AS')
    selfie = models.FileField(upload_to="selfie", null=True, blank=True)
    rg = models.FileField(upload_to="rg", null=True, blank=True)
    
    def __str__(self):

        return str(self.valor)
    
    @property
    def valuation(self):
        return(100 * float(self.valor)) / float(self.percentual)

class KYC(models.Model):
    investidor = models.ForeignKey(User, on_delete=models.CASCADE)
    data_verificacao = models.DateField(auto_now_add=True)
    status_verificado = models.BooleanField(default=False)
    score_fraude = models.IntegerField(default=0)

    def __str__(self):
        return f'KYC - {self.investidor.username}'


# =============================================================================
# DATA ROOM - DOCUMENTOS CONFIDENCIAIS
# =============================================================================

class DocumentoDataRoom(models.Model):
    """
    Documentos confidenciais da empresa, acessíveis apenas para investidores com Match aprovado.
    """
    TIPO_CHOICES = [
        ('DRE', 'Demonstração de Resultados (DRE)'),
        ('BP', 'Balanço Patrimonial'),
        ('FC', 'Fluxo de Caixa'),
        ('PLANILHA', 'Planilha Financeira'),
        ('CONTRATO', 'Contrato Social/Estatuto'),
        ('PATENTE', 'Patente/Propriedade Intelectual'),
        ('AUDITORIA', 'Relatório de Auditoria'),
        ('OUTRO', 'Outro Documento')
    ]
    
    empresa = models.ForeignKey(Empresas, on_delete=models.CASCADE, related_name='documentos_dataroom')
    titulo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    arquivo = models.FileField(upload_to='dataroom/')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='OUTRO')
    privado = models.BooleanField(default=True, help_text='Se True, apenas investidores com Match podem visualizar')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Documento Data Room'
        verbose_name_plural = 'Documentos Data Room'
    
    def __str__(self):
        return f'{self.titulo} - {self.empresa.nome}'


class AcessoDocumento(models.Model):
    """
    Registro de acessos aos documentos do Data Room para auditoria.
    """
    documento = models.ForeignKey(DocumentoDataRoom, on_delete=models.CASCADE, related_name='acessos')
    investidor = models.ForeignKey(User, on_delete=models.CASCADE)
    data_acesso = models.DateTimeField(auto_now_add=True)
    ip_acesso = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-data_acesso']
    
    def __str__(self):
        return f'{self.investidor.username} acessou {self.documento.titulo}'


# =============================================================================
# CONTRATOS DIGITAIS - ASSINATURA ELETRÔNICA
# =============================================================================

class ContratoDigital(models.Model):
    """
    Contratos de investimento com assinatura digital via ZapSign/Clicksign.
    """
    STATUS_CHOICES = [
        ('DRAFT', 'Rascunho'),
        ('PENDING', 'Pendente de Envio'),
        ('SENT', 'Enviado para Assinatura'),
        ('PARTIAL', 'Parcialmente Assinado'),
        ('SIGNED', 'Totalmente Assinado'),
        ('REJECTED', 'Rejeitado'),
        ('EXPIRED', 'Expirado'),
        ('CANCELLED', 'Cancelado')
    ]
    
    TIPO_CONTRATO_CHOICES = [
        ('MUTUO', 'Mútuo Conversível'),
        ('NDA', 'Termo de Confidencialidade (NDA)'),
        ('SAFE', 'SAFE (Simple Agreement for Future Equity)'),
        ('INVESTIMENTO', 'Contrato de Investimento'),
        ('OUTRO', 'Outro')
    ]
    
    proposta = models.ForeignKey(PropostaInvestimento, on_delete=models.CASCADE, related_name='contratos')
    tipo_contrato = models.CharField(max_length=20, choices=TIPO_CONTRATO_CHOICES, default='MUTUO')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    # Dados da API de assinatura (ZapSign/Clicksign)
    documento_id_externo = models.CharField(max_length=100, blank=True, help_text='ID do documento na plataforma de assinatura')
    url_assinatura_investidor = models.URLField(blank=True)
    url_assinatura_empresario = models.URLField(blank=True)
    
    # Datas
    criado_em = models.DateTimeField(auto_now_add=True)
    enviado_em = models.DateTimeField(null=True, blank=True)
    assinado_investidor_em = models.DateTimeField(null=True, blank=True)
    assinado_empresario_em = models.DateTimeField(null=True, blank=True)
    finalizado_em = models.DateTimeField(null=True, blank=True)
    expira_em = models.DateTimeField(null=True, blank=True)
    
    # Documento final assinado
    documento_assinado = models.FileField(upload_to='contratos_assinados/', null=True, blank=True)
    
    # Hash para validação de integridade
    hash_documento = models.CharField(max_length=64, blank=True)
    
    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Contrato Digital'
        verbose_name_plural = 'Contratos Digitais'
    
    def __str__(self):
        return f'{self.get_tipo_contrato_display()} - {self.proposta.empresa.nome} ({self.get_status_display()})'
    
    @property
    def esta_totalmente_assinado(self):
        return self.assinado_investidor_em and self.assinado_empresario_em
    
    @property
    def pode_ser_enviado(self):
        return self.status in ['DRAFT', 'PENDING']


class WebhookLog(models.Model):
    """
    Log de webhooks recebidos das plataformas de assinatura para auditoria.
    """
    contrato = models.ForeignKey(ContratoDigital, on_delete=models.CASCADE, null=True, blank=True, related_name='webhook_logs')
    evento = models.CharField(max_length=50)
    payload = models.JSONField()
    processado = models.BooleanField(default=False)
    erro = models.TextField(blank=True)
    recebido_em = models.DateTimeField(auto_now_add=True)
    processado_em = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-recebido_em']
    
    def __str__(self):
        return f'Webhook {self.evento} - {self.recebido_em}'

