from crewai import Task
from agents import kamila, thoth, hera, hermes

# Tarefa 1: Processamento Visual (Hera)
task_ocr_fiscal = Task(
    description="""Analise a imagem da nota fiscal fornecida. 
    1. Extraia o CNPJ do emissor.
    2. Liste os itens comprados e seus respectivos valores.
    3. Identifique o valor total da nota.""",
    expected_output="Um relatório JSON estruturado com os dados da nota fiscal.",
    agent=hera
)

# Tarefa 2: Análise Financeira (Hermes)
task_analise_financeira = Task(
    description="""Com base nos dados extraídos pela Hera:
    1. Calcule a carga tributária estimada.
    2. Compare os gastos com o orçamento mensal (simulando dados de entrada).
    3. Identifique anomalias nos preços.""",
    expected_output="Um resumo executivo sobre a saúde financeira desta transação.",
    agent=hermes,
    context=[task_ocr_fiscal]
)

# Tarefa 3: Comunicação Sakanews (Kamila/Thoth)
task_gerar_post = Task(
    description="""Com base em toda a análise anterior, gere um post informativo para o blog Sakanews.
    O tom deve ser profissional, tecnológico e focado em como o sistema S.A.K.A facilita a gestão empresarial.""",
    expected_output="Um post de blog em Markdown pronto para publicação no Sakanews.",
    agent=kamila,
    context=[task_analise_financeira]
)
