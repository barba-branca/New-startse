
def realizar_due_diligence(empresa):
    # Simula uma validação automática
    from .models import DueDiligence
    score = 0
    if empresa.tempo_existencia in ['+1', '+5']:
        score += 50
    if empresa.estagio in ['MVPP', 'E']:
        score += 30
    if empresa.valuation > 0:
        score += 20

    status = True if score >= 80 else False

    DueDiligence.objects.create(
        empresa=empresa,
        status_compliance=status,
        score_risco=100-score,
        analise_detalhada="Analise automatica baseada no estagio e tempo de existencia."
    )
