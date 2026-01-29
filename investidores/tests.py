from django.test import TestCase, Client
from django.contrib.auth.models import User
from empresarios.models import Empresas
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, timedelta

class VerEmpresaViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')

        logo = SimpleUploadedFile(name='test_logo.jpg', content=b'', content_type='image/jpeg')
        pitch = SimpleUploadedFile(name='test_pitch.mp4', content=b'', content_type='video/mp4')

        self.empresa = Empresas.objects.create(
            user=self.user,
            nome='Test Company',
            cnpj='12345678901234',
            site='http://test.com',
            tempo_existencia='-6',
            descricao='Test Description',
            data_final_captacao=date.today() + timedelta(days=30),
            percentual_equity=10,
            estagio='I',
            area='ED',
            publico_alvo='B2B',
            valor=100000.00,
            pitch=pitch,
            logo=logo
        )

    def test_ver_empresa_renders_correctly(self):
        response = self.client.get(f'/investidores/ver_empresa/{self.empresa.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Company')
        self.assertContains(response, 'Faça sua proposta') # Check for the new form title
        self.assertContains(response, 'Pagar com Mercado Pago') # Check for the button
