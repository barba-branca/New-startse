# Documentação: Funcionalidade de Busca Avançada de Startups

Esta documentação descreve a arquitetura, o design e a implementação da funcionalidade de **Busca Avançada de Startups** no módulo de investidores da plataforma **START-SE**.

---

## 1. Visão Geral

A funcionalidade de Busca Avançada permite que investidores filtrem de forma minuciosa as startups disponíveis para captação no Marketplace. Diferente do sistema de sugestões automáticas baseadas em perfil de risco, a busca avançada oferece controle granular ao usuário para localizar oportunidades com base em múltiplos critérios simultâneos.

---

## 2. Parâmetros de Filtro Suportados

A busca é processada via método `GET` utilizando a URL `/investidores/busca_avancada/`. Os parâmetros suportados são:

| Parâmetro | Campo no Banco / Modelo | Tipo de Filtro | Descrição |
| :--- | :--- | :--- | :--- |
| `nome` | `nome` e `descricao` | Texto parcial (`icontains`) | Filtra empresas cujo nome ou descrição contenha o termo digitado. |
| `area` | `area` | Seleção múltipla | Filtra startups que pertençam às áreas selecionadas (ex: Ed-tech, Fintech, Agrotech). |
| `estagio` | `estagio` | Seleção múltipla | Filtra pelo estágio de desenvolvimento (Ideia, MVP, MVP Pago, Escala). |
| `tempo_existencia` | `tempo_existencia` | Seleção múltipla | Filtra pelo tempo de existência da empresa. |
| `valuation_min` / `valuation_max` | Calculado dinamicamente | Faixa de valores | Filtra com base no valuation dinâmico da empresa. |
| `equity_min` / `equity_max` | `percentual_equity` | Faixa de valores | Filtra pelo percentual de equity oferecido pela startup. |
| `valor_min` / `valor_max` | `valor` | Faixa de valores | Filtra pela meta de captação solicitada pela startup. |

---

## 3. Implementação Técnica

### A. View (`investidores/views.py`)
A view [busca_avancada](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/investidores/views.py#L294) realiza o processamento dos filtros combinados de forma otimizada.
- **Prevenção de Divisão por Zero**: Filtra-se `percentual_equity__gt=0` na query base para evitar falhas no cálculo do valuation.
- **Valuation Dinâmico via Banco de Dados**:
  Como o *valuation* é uma propriedade calculada (`(valor * 100) / percentual_equity`) e não uma coluna de banco de dados física, implementamos uma anotação dinâmica usando `ExpressionWrapper` para possibilitar a filtragem de faixas diretamente no banco de dados, maximizando o desempenho do banco:
  ```python
  from django.db.models import F, ExpressionWrapper, DecimalField

  empresas = empresas.annotate(
      val=ExpressionWrapper(
          (F('valor') * 100) / F('percentual_equity'),
          output_field=DecimalField(max_digits=15, decimal_places=2)
      )
  )
  ```
- **Persistência de Estado**: Os valores aplicados são repassados ao dicionário `filtros` no contexto, garantindo que o formulário permaneça preenchido com as escolhas do usuário após o carregamento da página.

### B. Template (`investidores/templates/busca_avancada.html`)
- Utiliza **Checkboxes** responsivos para seleção múltipla de Categorias (Áreas, Estágios e Tempos de Existência) em vez de selects múltiplos padrão, otimizando o uso no mobile.
- Apresenta os resultados em um grid responsivo de 3 colunas (desktop) que decai para 1 coluna (mobile).
- Cada card inclui badges com estilos personalizados para a Área de Atuação e Estágio, detalhes de Valuation e Equity, além de uma **barra de progresso dinâmica** para exibir o percentual já captado pela startup em relação à meta.

### C. Rota URL (`investidores/urls.py`)
A rota é registrada como:
```python
path('busca_avancada/', views.busca_avancada, name="busca_avancada"),
```

---

## 4. Testes e Validação

Uma suíte de testes unitários dedicada foi adicionada a [investidores/tests.py](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/investidores/tests.py) para validar a robustez de cada filtro:
1. **`test_busca_avancada_status_code`**: Valida que a página de busca carrega com status HTTP 200.
2. **`test_busca_avancada_filter_nome`**: Verifica a busca de termo textual no nome da startup.
3. **`test_busca_avancada_filter_area`**: Garante que o filtro por área exibe as empresas corretas.
4. **`test_busca_avancada_filter_valuation`**: Valida a precisão da filtragem de faixa numérica no valuation calculado dinamicamente.

Para executar os testes:
```bash
python manage.py test
```
