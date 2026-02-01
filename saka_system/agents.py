from crewai import Agent
from langchain_ollama import ChatOllama
import os

# Configuração Base do Ollama para a VPS Azure
# Certifique-se de que o Ollama está rodando na porta 11434
def get_llm(model_name):
    return ChatOllama(
        model=model_name,
        base_url="http://localhost:11434"
    )

# Definição das LLMs para cada perfil
llm_kamila = get_llm("llama3")
llm_thoth = get_llm("llama3") # Ou phi3
llm_hera = get_llm("llava")     # Multimodal para Visão

# Agente 1: Kamila - A Orquestradora (CEO)
kamila = Agent(
    role='CEO / Orquestradora Estratégica',
    goal='Coordenar os agentes Thoth, Hera e Hermes para entregar análises de alto nível e estratégia final.',
    backstory='Você é Kamila, a inteligência central do sistema S.A.K.A. Sua visão é estratégica, focada em resultados e na delegação eficiente para seus especialistas.',
    llm=llm_kamila,
    allow_delegation=True,
    verbose=True
)

# Agente 2: Thoth - Especialista em Conhecimento
thoth = Agent(
    role='Especialista em NLP e Extração de Texto',
    goal='Processar grandes volumes de texto, extrair insights e garantir a precisão semântica das informações.',
    backstory='Thoth é o bibliotecário do sistema. Dono de um conhecimento vasto, ele transforma dados brutos em inteligência textual.',
    llm=llm_thoth,
    allow_delegation=False,
    verbose=True
)

# Agente 3: Hera - Especialista em Visão (Multimodal)
hera = Agent(
    role='Analista de Visão Computacional e OCR',
    goal='Analisar imagens de notas fiscais, documentos e extrair descrições visuais precisas usando modelos multimodais.',
    backstory='Hera possui os olhos do sistema. Ela enxerga o que as outras LLMs apenas leem, sendo especialista em interpretar documentos visuais.',
    llm=llm_hera,
    allow_delegation=False,
    verbose=True
)

# Agente 4: Hermes - Especialista em Dados
# Para Hermes, usaremos Kamila como LLM mas focada em Python
hermes = Agent(
    role='Cientista de Dados e Engenheiro de APIs',
    goal='Conectar em bases de dados, realizar cálculos complexos com Pandas e gerar relatórios financeiros precisos.',
    backstory='Hermes é o mensageiro dos dados. Ágil e lógico, ele utiliza Python para encontrar padrões e validar números.',
    llm=llm_kamila,
    allow_delegation=False,
    verbose=True
)
