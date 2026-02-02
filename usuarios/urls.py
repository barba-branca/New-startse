from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.cadastro, name="cadastro"),
    path('logar/', views.logar, name="logar"),
    path('google-login/', views.google_login, name="google_login"),
]