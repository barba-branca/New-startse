from django.urls import path
from . import views

app_name = 'otc'

urlpatterns = [
    path('rfq/request/', views.request_quote, name='request_quote'),
    path('rfq/execute/', views.execute_trade, name='execute_trade'),
]
