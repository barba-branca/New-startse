# Documentação: Sugestões de IA para Investidores

Esta documentação descreve a arquitetura, o design e o mecanismo de inteligência artificial empregado no módulo de **Sugestões de Investimento** (Marketplace) da plataforma **START-SE**.

---

## 1. Visão Geral

O sistema de sugestões analisa o perfil de risco do investidor (Conservador ou Despojado), as áreas de mercado em que possui interesse (ex: Fintechs, Agrotechs, Edtechs) e o capital disponível para sugerir as startups mais alinhadas.

Com a integração de IA, o sistema agora gera **recomendações inteligentes justificadas**, explicando em linguagem natural o porquê de cada startup ser recomendada com base nas preferências do usuário.

---

## 2. Fluxo da IA e Prompt de Recomendação

### A. Preparação de Dados
A view pré-filtra as startups candidatas da plataforma onde o capital disponível do investidor é suficiente para comprar pelo menos **1% do valuation** (equity mínimo de participação).

### B. O Prompt de Análise
Os metadados das startups são compilados e enviados estruturados em JSON para o modelo **Gemini** ou **Ollama** com as seguintes instruções:
- Analisar a afinidade de cada startup com o perfil de risco do investidor.
- Analisar a afinidade com os segmentos (áreas de interesse).
- Gerar justificativas em português brasileiro personalizadas e concisas (limite de 2 frases).
- Retornar estritamente um array JSON contendo IDs e justificativas correspondentes.

### C. Estrutura de Retorno do JSON
```json
[
  {
    "id": 1,
    "justificativa": "Esta edtech é ideal para seu perfil conservador, pois já possui um MVP estável e receita recorrente escalável, reduzindo consideravelmente os riscos de mercado."
  }
]
```

---

## 3. Resiliência e Fallback Seguro

Para garantir a alta disponibilidade da plataforma mesmo sob indisponibilidade de rede ou falha de chave das APIs de IA:
1. **Fallback Automático**: Se a requisição de IA falhar ou o formato JSON retornado estiver quebrado, a view captura a exceção e executa de imediato a **Heurística Clássica**.
2. **Heurística Clássica**:
   - **Conservador**: Retorna startups que têm tempo de mercado superior a 5 anos (`tempo_existencia='+5'`) e estão prontas para escalar (`estagio='E'`).
   - **Despojado**: Retorna startups jovens com menos de 5 anos de mercado e que ainda estão validando MVP ou modelo de negócio (`estagio!='E'`).
3. **Badge Indicadora**: O template exibe de forma clara a autoria das sugestões através de uma badge com o texto `💡 Fonte das Sugestões: Inteligência Artificial` ou `💡 Fonte das Sugestões: Regras do Sistema`.

---

## 4. Testes e Validação (`investidores/tests.py`)

A classe `SugestoesTestCase` foi adicionada para garantir o funcionamento correto:
- **`test_sugestao_heuristica_conservador`**: Valida que o filtro clássico conservador funciona perfeitamente isolando startups maduras.
- **`test_sugestao_heuristica_despojado`**: Valida que o filtro clássico despojado traz startups em fases de validação rápida.
- **`test_sugestao_ia_fallback_sem_api_key`**: Simula uma chamada de IA sem chaves de API, confirmando que o sistema degrada graciosamente para a heurística tradicional sem gerar erros HTTP 500 ou quebras de tela.
