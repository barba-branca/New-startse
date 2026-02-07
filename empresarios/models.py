from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils.safestring import mark_safe

class Empresas(models.Model):
    tempo_existencia_choices = (
        ('-6', 'Menos de 6 meses'),
        ('+6', 'Mais de 6 meses'),
        ('+1', 'Mais de 1 ano'),
        ('+5', 'Mais de 5 anos')
    )
    estagio_choices = (
        ('I', 'Tenho apenas uma ideia'),
        ('MVP', 'Possuo um MVP'),
        ('MVPP', 'Possuo um MVP com clientes pagantes'),
        ('E', 'Empresa pronta para escalar'),
    )
    area_choices = (
        ('ED', 'Ed-tech'),
        ('FT', 'Fintech'),
        ('AT', 'Agrotech'),

    )
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    nome = models.CharField(max_length=50)
    cnpj = models.CharField(max_length=30)
    site = models.URLField()
    tempo_existencia = models.CharField(max_length=2, choices=tempo_existencia_choices, default='-6')
    descricao = models.TextField()
    data_final_captacao = models.DateField()
    percentual_equity = models.IntegerField() # Percentual esperado
    estagio = models.CharField(max_length=4, choices=estagio_choices, default='I')
    area = models.CharField(max_length=3, choices=area_choices)
    publico_alvo = models.CharField(max_length=3)
    valor = models.DecimalField(max_digits=9, decimal_places=2) # Valor total a ser vendido
    taxa_intermediacao = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Taxa de Intermediação"
    )
    
    valor_liquido = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Valor Líquido"
    )
    pitch = models.FileField(upload_to='pitchs')
    logo = models.FileField(upload_to='logo')

    def __str__(self):
        return f'{self.user.username} | {self.nome}'
    
    @property
    def total_captado(self):
        try:
            # Import DENTRO do método para evitar circular import
            from investidores.models import PropostaInvestimento
            total = PropostaInvestimento.objects.filter(
                empresa=self, 
                status='PA'
            ).aggregate(total=models.Sum('valor'))['total']
            return total or 0
        except Exception as e:
            # Log o erro específico
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro em total_captado para empresa {self.id}: {e}")
            return 0

    @property
    def percentual_captado(self):
        try:
            total = self.total_captado
            if not self.valor or self.valor == 0:
                return 0
            return int((float(total) / float(self.valor)) * 100)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Erro em percentual_captado: {e}")
            return 0

    @property
    def qtd_investidores(self):
        try:
            from investidores.models import PropostaInvestimento
            return PropostaInvestimento.objects.filter(empresa=self, status='PA').values('investidor').distinct().count()
        except:
            return 0

    @property
    def percentual_vendido(self):
        try:
            from investidores.models import PropostaInvestimento
            vendido = PropostaInvestimento.objects.filter(empresa=self, status='PA').aggregate(total=models.Sum('percentual'))['total']
            return vendido or 0
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Erro em percentual_vendido: {e}")
            return 0
    
    @property
    def percentual_a_vender(self):
        equity = self.percentual_equity if self.percentual_equity is not None else 0
        return equity - self.percentual_vendido
    
    @property
    def status(self):
        try:
            if self.percentual_captado >= 100:
                return mark_safe('<span class="badge bg-success">Captação concluída</span>')
            
            if self.data_final_captacao and date.today() > self.data_final_captacao:
                return mark_safe('<span class="badge bg-secondary">Captação finalizada</span>')
                    
            return mark_safe('<span class="badge bg-success">Em captação</span>')
        except:
            return mark_safe('<span class="badge bg-warning">Erro no status</span>')
    
    @property
    def valuation(self):
        try:
            if not self.percentual_equity or self.percentual_equity == 0:
                return 0
            valor = float(self.valor) if self.valor else 0
            return round((100 * valor) / float(self.percentual_equity), 2)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Erro em valuation: {e}")
            return 0
    
class Documento(models.Model):
    empresa = models.ForeignKey(Empresas, on_delete=models.DO_NOTHING)
    titulo = models.CharField(max_length=30)
    arquivo = models.FileField(upload_to="documentos")
    
    def __str__(self):
        return self.titulo
    
class Metricas(models.Model):
    empresa = models.ForeignKey(Empresas, on_delete=models.DO_NOTHING)
    titulo = models.CharField(max_length=30)
    valor = models.FloatField()

    def __str__(self):
        return self.titulo

class DueDiligence(models.Model):
    empresa = models.ForeignKey(Empresas, on_delete=models.CASCADE)
    data_analise = models.DateField(auto_now_add=True)
    status_compliance = models.BooleanField(default=False)
    score_risco = models.IntegerField(default=0)
    analise_detalhada = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Due Diligence - {self.empresa.nome}'
        
