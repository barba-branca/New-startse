# Documentação de Ajustes de Responsividade Mobile

Este documento registra as melhorias de layout e responsividade realizadas no projeto **START-SE** para garantir uma navegação fluida em dispositivos móveis.

---

## 1. Telas de Autenticação (Login e Cadastro)

### Problema
Ao acessar as telas de Cadastro e Login em dispositivos móveis, era exibido um bloco escuro vazio ocupando 100% da altura da tela (`100vh`), obrigando o usuário a rolar para baixo para ver o formulário.

### Causa Raiz
A coluna lateral da imagem (`col-md-2 bg-img`) possuía a classe do Bootstrap `d-flex` que aplica `display: flex !important;`. Isso sobrescrevia a regra CSS de ocultação no mobile, fazendo com que a coluna vazia continuasse sendo renderizada e empurrasse todo o formulário para baixo.

### Solução
Substituímos o controle de ocultação do CSS pelas classes utilitárias nativas do Bootstrap:
* **[cadastro.html](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/usuarios/templates/cadastro.html#L13):** Alterado de `d-flex` para `d-none d-md-flex`.
* **[logar.html](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/usuarios/templates/logar.html#L9):** Alterado de `d-flex` para `d-none d-md-flex`.

---

## 2. Landing Page Inicial (`landingPage/templates/index.html`)

Corrigimos três principais problemas de responsividade na landing page inicial:

### A. Sobreposição no Menu Mobile
* **Problema:** Ao abrir o menu mobile lateral, os botões de chamada para ação (CTA) se sobrepunham ao link "FAQ" na lista de links.
* **Causa Raiz:** O script JavaScript calculava a posição do topo do container de CTA de forma estática com base em uma estimativa de altura dos links (`70 + (length * 50) + 40`). Como os links reais possuem preenchimento e fontes maiores, a altura real da lista era superior a `50px` por item.
* **Solução:** Alteramos o cálculo do posicionamento para utilizar a altura real computada do elemento na tela via JavaScript:
  ```javascript
  top: ${70 + navLinks.getBoundingClientRect().height}px;
  ```

### B. Alinhamento dos Cards de Tecnologia (Tech Stack)
* **Problema:** Na seção de tecnologias utilizadas, os itens (`.tech-item`) tentavam exibir o ícone, o título e a descrição lado a lado em uma única linha no mobile, o que causava espremimento e cortes de texto.
* **Causa Raiz:** A regra CSS no media query de `768px` forçava `flex-direction: row;` sem que os textos estivessem encapsulados em um container próprio para separá-los do ícone.
* **Solução:** Alteramos a estrutura do flexbox no mobile para manter uma orientação vertical (`flex-direction: column`) e centralizada, alinhando-se com o restante do design da seção:
  ```css
  .tech-item {
      flex-direction: column;
      align-items: center;
      text-align: center;
  }
  .tech-item .tech-desc {
      text-align: center;
  }
  ```

### C. Largura dos Cards de Planos (Pricing Cards)
* **Problema:** O card do plano **Corporativo** (o último card) era renderizado em largura reduzida e desalinhada em relação aos planos Básico e Profissional nas telas de tablet e mobile.
* **Causa Raiz:** 
  1. No CSS principal, as `.pricing-card` não tinham `width: 100%` definido, fazendo com que o navegador não as esticasse uniformemente em todas as resoluções.
  2. No media query de `992px` (tablet), o card Corporativo foi configurado para ocupar 2 colunas (`grid-column: span 2`), mas com um limite fixo e estático de `max-width: 400px` e `margin: 0 auto;`. Isso causava uma discrepância de tamanho (ora maior, ora menor que as outras) conforme a largura da tela variava.
  3. No media query de `768px` (mobile), a margem automática e o grid-span herdados não eram completamente resetados.
* **Solução:**
  1. Adicionamos `width: 100%` e `box-sizing: border-box` na classe principal `.pricing-card` para fazê-las preencherem o espaço disponível uniformemente.
  2. No media query de `992px` (tablet), definimos a largura máxima do card Corporativo de forma matemática: `max-width: calc(50% - 10px);`. Como o grid tem 2 colunas e espaçamento (gap) de `20px`, essa fórmula calcula exatamente a largura de uma única coluna (`50%` do grid menos a metade do gap). Assim, o card Corporativo fica **exatamente com a mesma largura** dos outros planos.
  3. No media query de `768px` (mobile), resetamos o grid para 1 coluna e removemos a margem para que todos os três planos ocupem 100% da largura.

---

## 3. Validação e Testes
* Executamos testes em diferentes viewports e medimos as larguras exatas dos cards:
  * **Visualização Desktop (3 colunas):** Todos os 3 cards alinham-se perfeitamente lado a lado com largura idêntica.
  * **Visualização Tablet (800px de largura - 2 colunas):** Os três cards medem **exatamente 350px** de largura (os dois primeiros lado a lado e o Corporativo centralizado abaixo, com tamanho idêntico).
  * **Visualização Mobile (386px de largura - 1 coluna):** Os três cards empilham-se verticalmente, medindo **exatamente 348px** de largura.

