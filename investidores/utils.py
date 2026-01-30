
def realizar_kyc(investidor):
    # Simula uma validação de KYC
    from .models import KYC
    # Aqui poderia chamar uma API externa de background check
    KYC.objects.create(
        investidor=investidor,
        status_verificado=True,
        score_fraude=10
    )
