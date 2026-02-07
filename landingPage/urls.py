from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landingPage'),
    path('logar/', views.login_view, name="logar"),
    path('checkout/<str:plan_id>/', views.checkout, name='checkout')
]
