# Documentação: Separação de Perfis & Validação de CNPJ

**Autor:** Barba-Branca

Este documento detalha o sistema de gerenciamento de perfis da **New Start-se**, que separa os fluxos e acessos entre **Investidores** e **Empresários** com validação de CNPJ obrigatória no ato de cadastro.

---

## 🏗️ 1. Arquitetura de Perfis (`PerfilUsuario`)

Para estender o modelo de usuários nativo do Django (`django.contrib.auth.models.User`) sem gerar dependências complexas ou quebras de integridade, foi implementado o modelo `PerfilUsuario` em [usuarios/models.py](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/usuarios/models.py):

- **Relação**: OneToOne com o modelo `User`.
- **Tipo de Conta (`role`)**:
  - `'I'` - **Investidor PJ**: Acesso exclusivo ao marketplace, busca avançada, KYC, e propostas de aporte.
  - `'E'` - **Empresário / Startup**: Acesso exclusivo à listagem de empresas, cadastro de startups, métricas, due diligence e gestão de propostas aceitas/recusadas.
- **CNPJ**: Armazenado de forma limpa (apenas números) e com restrição de unicidade (`unique=True`).
- **Razão Social**: Preenchida automaticamente com dados fiscais oficiais recuperados no cadastro.

---

## 🔒 2. Fluxo de Cadastro e Validação

Durante o registro do usuário em `/usuarios/cadastro/`:
1. O usuário escolhe o tipo de conta (Investidor vs. Empresário).
2. Fornece seu **CNPJ** (formatado ou não).
3. O sistema limpa a pontuação e executa o validador `validar_cnpj_api` do módulo [empresarios/utils.py](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/empresarios/utils.py):
   - Valida os **dígitos verificadores** localmente para evitar consultas a CNPJs matematicamente incorretos.
   - Consulta a **Brasil API** (Receita Federal) para garantir a existência e situação ativa do cadastro e recuperar a Razão Social.
   - Bloqueia e avisa o usuário caso o CNPJ esteja inválido, inexistente ou já cadastrado por outra conta.
4. Se válido, o usuário e seu respectivo perfil são salvos no banco de dados.

---

## 🚫 3. Controle de Rotas e Segurança (Decorators)

Para prevenir erros operacionais ou brechas onde investidores acessem áreas administrativas de captação (ou empresários enviem propostas para si mesmos), criamos decorators de controle rígidos:

* **`@investidor_required`** ([investidores/views.py](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/investidores/views.py)): Aplicado a todas as views do aplicativo de investidores. Caso a conta logada possua perfil de empresário (`role == 'E'`), ela é bloqueada e redirecionada para `/empresarios/listar_empresas/`.
* **`@empresario_required`** ([empresarios/views.py](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/empresarios/views.py)): Aplicado a todas as views de captação. Caso a conta logada possua perfil de investidor (`role == 'I'`), ela é bloqueada e redirecionada para `/investidores/painel/`.

---
*Documentação de controle de perfis elaborada sob a coordenação de Barba-Branca.*
