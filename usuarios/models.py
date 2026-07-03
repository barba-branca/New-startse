from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    ROLE_CHOICES = (
        ('I', 'Investidor'),
        ('E', 'Empresário'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    role = models.CharField(max_length=1, choices=ROLE_CHOICES)
    cnpj = models.CharField(max_length=18, unique=True)
    razao_social = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
