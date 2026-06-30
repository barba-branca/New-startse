from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from empresarios.models import Empresas
from datetime import date
from django.core.files.uploadedfile import SimpleUploadedFile

class BuscaAvancadaTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        
        logo = SimpleUploadedFile("logo.png", b"file_content", content_type="image/png")
        pitch = SimpleUploadedFile("pitch.pdf", b"file_content", content_type="application/pdf")
        
        self.empresa1 = Empresas.objects.create(
            user=self.user,
            nome="EduTech Ltda",
            cnpj="12.345.678/0001-99",
            site="https://edutech.com",
            tempo_existencia="+1",
            descricao="Startup focada em educação e tecnologia inovadora.",
            data_final_captacao=date(2027, 12, 31),
            percentual_equity=10,
            estagio="MVP",
            area="ED",
            publico_alvo="B2C",
            valor=100000.00,
            logo=logo,
            pitch=pitch
        )
        
        self.empresa2 = Empresas.objects.create(
            user=self.user,
            nome="AgroTech Solutions",
            cnpj="98.765.432/0001-00",
            site="https://agrotech.com",
            tempo_existencia="+5",
            descricao="Inovação no campo e sustentabilidade.",
            data_final_captacao=date(2027, 12, 31),
            percentual_equity=20,
            estagio="E",
            area="AT",
            publico_alvo="B2B",
            valor=500000.00,
            logo=logo,
            pitch=pitch
        )

    def test_busca_avancada_status_code(self):
        response = self.client.get(reverse('busca_avancada'))
        self.assertEqual(response.status_code, 200)

    def test_busca_avancada_filter_nome(self):
        response = self.client.get(reverse('busca_avancada') + '?nome=EduTech')
        self.assertEqual(len(response.context['empresas']), 1)
        self.assertEqual(response.context['empresas'][0].nome, "EduTech Ltda")

    def test_busca_avancada_filter_area(self):
        response = self.client.get(reverse('busca_avancada') + '?area=AT')
        self.assertEqual(len(response.context['empresas']), 1)
        self.assertEqual(response.context['empresas'][0].nome, "AgroTech Solutions")

    def test_busca_avancada_filter_valuation(self):
        # valuation de empresa1 = 100 * 100000 / 10 = 1000000
        # valuation de empresa2 = 100 * 500000 / 20 = 2500000
        response = self.client.get(reverse('busca_avancada') + '?valuation_min=1500000')
        self.assertEqual(len(response.context['empresas']), 1)
        self.assertEqual(response.context['empresas'][0].nome, "AgroTech Solutions")


class PainelInvestidorTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='investor1', password='password123')
        
        logo = SimpleUploadedFile("logo.png", b"file_content", content_type="image/png")
        pitch = SimpleUploadedFile("pitch.pdf", b"file_content", content_type="application/pdf")
        
        self.empresa = Empresas.objects.create(
            user=self.user,
            nome="StartSe Ltda",
            cnpj="11.222.333/0001-44",
            site="https://startse.com",
            tempo_existencia="+1",
            descricao="Plataforma de crowdfunding.",
            data_final_captacao=date(2027, 12, 31),
            percentual_equity=10,
            estagio="MVP",
            area="FT",
            publico_alvo="B2B",
            valor=100000.00,
            logo=logo,
            pitch=pitch
        )
        
        # Cria propostas de investimento
        from investidores.models import PropostaInvestimento
        self.proposta_aceita = PropostaInvestimento.objects.create(
            valor=50000.00,
            percentual=5.0,
            empresa=self.empresa,
            investidor=self.user,
            status='PA'
        )
        
        self.proposta_pendente = PropostaInvestimento.objects.create(
            valor=20000.00,
            percentual=2.0,
            empresa=self.empresa,
            investidor=self.user,
            status='AS'
        )

    def test_painel_investidor_anonymous_redirect(self):
        response = self.client.get(reverse('painel_investidor'))
        # Deve redirecionar para a página de login
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/usuarios/logar/' in response.url)

    def test_painel_investidor_authenticated(self):
        self.client.login(username='investor1', password='password123')
        response = self.client.get(reverse('painel_investidor'))
        self.assertEqual(response.status_code, 200)
        
        # Verificar se as métricas no context estão corretas
        self.assertEqual(response.context['total_investido'], 50000.00)
        self.assertEqual(response.context['propostas_pendentes'], 1)
        self.assertEqual(response.context['startups_apoiadas'], 1)
        self.assertEqual(len(response.context['propostas']), 2)


class SugestoesTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testinvestor', password='password123')
        logo = SimpleUploadedFile("logo.png", b"file_content", content_type="image/png")
        pitch = SimpleUploadedFile("pitch.pdf", b"file_content", content_type="application/pdf")
        
        # Empresa 1 - Conservadora (Existência +5 anos, Estágio E)
        self.empresa_c = Empresas.objects.create(
            user=self.user,
            nome="Empresa Velha S.A.",
            cnpj="11.111.111/0001-11",
            site="https://empresa.com",
            tempo_existencia="+5",
            descricao="Empresa consolidada no mercado.",
            data_final_captacao=date(2027, 12, 31),
            percentual_equity=10,
            estagio="E",
            area="ED",
            publico_alvo="B2B",
            valor=100000.00,
            logo=logo,
            pitch=pitch
        )
        
        # Empresa 2 - Despojada (Existência menos de 6 meses, Estágio I)
        self.empresa_d = Empresas.objects.create(
            user=self.user,
            nome="Startup Nova Ltda",
            cnpj="22.222.222/0001-22",
            site="https://startup.com",
            tempo_existencia="-6",
            descricao="Ideia revolucionária.",
            data_final_captacao=date(2027, 12, 31),
            percentual_equity=20,
            estagio="I",
            area="FT",
            publico_alvo="B2C",
            valor=50000.00,
            logo=logo,
            pitch=pitch
        )

    def test_sugestao_heuristica_conservador(self):
        response = self.client.post(reverse('sugestao'), {
            'tipo': 'C',
            'area': ['ED', 'FT'],
            'valor': '50000'
        })
        self.assertEqual(response.status_code, 200)
        # Deve sugerir apenas a empresa conservadora
        self.assertEqual(len(response.context['empresas']), 1)
        self.assertEqual(response.context['empresas'][0].nome, "Empresa Velha S.A.")

    def test_sugestao_heuristica_despojado(self):
        response = self.client.post(reverse('sugestao'), {
            'tipo': 'D',
            'area': ['ED', 'FT'],
            'valor': '50000'
        })
        self.assertEqual(response.status_code, 200)
        # Deve sugerir apenas a startup despojada
        self.assertEqual(len(response.context['empresas']), 1)
        self.assertEqual(response.context['empresas'][0].nome, "Startup Nova Ltda")

    def test_sugestao_ia_fallback_sem_api_key(self):
        # Com usar_ia=on, mas sem chaves de API, deve cair no fallback heurístico sem quebrar
        response = self.client.post(reverse('sugestao'), {
            'tipo': 'C',
            'area': ['ED', 'FT'],
            'valor': '50000',
            'usar_ia': 'on'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['fonte_sugestao'], "Regras do Sistema")
        self.assertEqual(len(response.context['empresas']), 1)
        self.assertEqual(response.context['empresas'][0].nome, "Empresa Velha S.A.")


