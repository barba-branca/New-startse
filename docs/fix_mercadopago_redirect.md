# Correção do Redirecionamento para o Mercado Pago

Este documento registra a correção realizada no fluxo de checkout da plataforma **START-SE**, resolvendo o problema de redirecionamento que impedia o acesso à tela de pagamento do Mercado Pago durante os testes locais.

---

## 1. Descrição do Problema
Ao clicar em "Assinar Corporativo" (ou qualquer outro plano pago) e realizar o login, a plataforma redirecionava o usuário de volta para a página inicial em vez de encaminhá-lo para a tela de pagamentos do Mercado Pago.

### Causa Raiz
* Para assinaturas, o Mercado Pago utiliza a configuração `auto_return: "approved"`, que exige que as URLs de retorno (`back_urls`) sejam obrigatoriamente seguras (**HTTPS**).
* Durante o desenvolvimento local (`http://127.0.0.1:8000`), a URL gerada dinamicamente iniciava com `http://`.
* A API do Mercado Pago rejeitava a criação da preferência com o erro:  
  `auto_return invalid. back_url.success must be defined`
* Devido a essa falha na criação da preferência, a view de checkout salvava uma mensagem de erro e redirecionava o usuário de volta para a página inicial.

---

## 2. Alterações Realizadas

Atualizamos a lógica de geração das preferências para garantir que as URLs de retorno sempre utilizem o protocolo HTTPS, satisfazendo a validação do Mercado Pago:

### [landingPage/utils.py](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/landingPage/utils.py)
Adicionamos uma verificação que substitui `http://` por `https://` na URL base enviada ao Mercado Pago:
```python
    # Mercado Pago exige URLs HTTPS para retorno
    if base_url.startswith("http://"):
        base_url = base_url.replace("http://", "https://")
```

---

## 3. Validação e Testes
* O fluxo foi validado simulando o comportamento de um usuário real:
  1. Acessou-se a tela de login com o redirecionamento: `/usuarios/logar/?next=/checkout/corporativo/`
  2. Autenticou-se utilizando as credenciais de teste.
  3. **Resultado:** O redirecionamento funcionou perfeitamente e o usuário foi encaminhado para a tela oficial de checkout do Mercado Pago (`https://www.mercadopago.com.br/checkout/...`).

---

## 4. Teste e Simulação em Dispositivos Móveis (Mobile)
Durante os testes de responsividade em navegadores de computador, apenas redimensionar a tela para um tamanho pequeno (ex: usando a opção "Responsive" do DevTools) **não** é suficiente para ativar a versão mobile do checkout do Mercado Pago.

### Motivo técnico
O Mercado Pago realiza a detecção do dispositivo no servidor por meio do cabeçalho HTTP **`User-Agent`** enviado pelo navegador. Se o `User-Agent` for de um navegador desktop, ele renderizará a versão desktop mesmo em resoluções pequenas.

### Como testar a interface mobile corretamente no navegador:
1. Abra as Ferramentas do Desenvolvedor (**F12**).
2. Ative a barra de simulação de dispositivos (ícone de celular/tablet no topo esquerdo do DevTools).
3. No menu suspenso de dispositivos (onde diz "Responsive"), selecione um modelo de celular real (ex: **iPhone 12 Pro** ou **Pixel 7**).
4. **Atualize a página (F5)** para aplicar o cabeçalho de simulação do celular.
5. Inicie o fluxo de checkout; o Mercado Pago abrirá a interface 100% otimizada para mobile.
