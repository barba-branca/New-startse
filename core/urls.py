from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('landingPage.urls')),  # A raiz do site agora vai para a landing page
    path('admin/', admin.site.urls),  # Rota para o painel de administração do Django
    path('usuarios/', include('usuarios.urls')),  # Inclui as URLs do app 'usuarios'
    path('empresarios/', include('empresarios.urls')),  # Rota para o app 'empresarios'
    path('investidores/', include('investidores.urls')),  # Rota para o app 'investidores'
    path('otc/', include('otc.urls')),
    # path('social-auth/', include('social_django.urls', namespace='social')),  # COMENTADO: conexões Gmail desativadas
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Serve arquivos de mídia em desenvolvimento



# O código acima é a configuração de URLs do Django para um projeto. Ele inclui as seguintes partes:
# - Importações necessárias para o funcionamento das URLs.
# - Configuração das URLs principais do projeto, incluindo redirecionamento para a página de login e inclusão de URLs específicas para diferentes aplicativos (usuarios, empresarios, investidores).
# - Configuração para servir arquivos de mídia durante o desenvolvimento.