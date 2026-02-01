from crewai import Crew, Process
from agents import kamila, thoth, hera, hermes
from tasks import task_ocr_fiscal, task_analise_financeira, task_gerar_post

# Configuração da Equipe S.A.K.A.
saka_crew = Crew(
    agents=[kamila, thoth, hera, hermes],
    tasks=[task_ocr_fiscal, task_analise_financeira, task_gerar_post],
    process=Process.sequential, # Mudança para Hierarchical se Kamila for Manager
    verbose=True
)

def iniciar_sistema():
    print("### Iniciando Sistema S.A.K.A. na VPS Azure ###")
    print("-----------------------------------------------")
    
    # Execução
    resultado = saka_crew.kickoff()
    
    print("\n\n########################")
    print("## RESULTADO DO S.A.K.A ##")
    print("########################\n")
    print(resultado)

if __name__ == "__main__":
    iniciar_sistema()
