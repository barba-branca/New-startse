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
    pitch = models.FileField(upload_to='pitchs')
    logo = models.FileField(upload_to='logo')

    def __str__(self):
        return f'{self.user.username} | {self.nome}'
    
    @property
    def total_captado(self):
        from investidores.models import PropostaInvestimento
        return PropostaInvestimento.objects.filter(empresa=self, status='PA').aggregate(models.Sum('valor'))['valor__sum'] or 0

    @property
    def percentual_captado(self):
        total = self.total_captado
        if self.valor == 0:
            return 0
        return int((total / self.valor) * 100)

    @property
    def qtd_investidores(self):
        from investidores.models import PropostaInvestimento
        return PropostaInvestimento.objects.filter(empresa=self, status='PA').values('investidor').distinct().count()

    @property
    def percentual_vendido(self):
        from investidores.models import PropostaInvestimento
        return PropostaInvestimento.objects.filter(empresa=self, status='PA').aggregate(models.Sum('percentual'))['percentual__sum'] or 0
    
    @property
    def percentual_a_vender(self):
        return self.percentual_equity - self.percentual_vendido
    
    @property
    def status(self):
        if self.percentual_captado >= 100:
            return mark_safe('<span class="badge bg-success">Captação concluída</span>')
        
        if date.today() > self.data_final_captacao:
            return mark_safe('<span class="badge bg-secondary">Captação finalizada</span>')
                
        return mark_safe('<span class="badge bg-success">Em captação</span>')
    
    @property
    def valuation(self):
        return float (f'{(100 * self.valor) / self.percentual_equity:.2f}')
    
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
        
