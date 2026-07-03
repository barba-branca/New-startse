# Documentação: KYC Inteligente & Contratos por IA

**Autor:** Barba-Branca

Este documento detalha o funcionamento e os algoritmos de prevenção a fraudes de identidade (KYC) e redação automática de contratos de investimento utilizando inteligência artificial generativa multimodal na plataforma **New Start-se**.

---

## 🔒 1. Validação KYC Anti-Fraude Multimodal por IA

Durante o processo de submissão de propostas de aporte, o investidor é obrigado a enviar fotos de sua identidade e uma selfie segurando o documento. Para garantir a segurança e evitar fraudes de forma dinâmica, foi implementada a verificação por IA na view [`assinar_contrato`](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/investidores/views.py#L427-L509):

- **Modelo**: `gemini-1.5-flash` (IA multimodal do Google Gemini).
- **Entradas**: Bytes da selfie do investidor e da foto do documento em close-up.
- **Análise Anti-Fraude**:
  - Compara a fisionomia da foto do documento com o rosto do investidor na selfie.
  - Valida o layout físico e formato do documento (se é um RG, CNH ou Passaporte válido).
  - Detecta traços de edição digital (Photoshop, recortes ou adulterações).
  - Verifica se a foto é de uma pessoa física ao vivo ou uma foto de tela de computador/celular.
- **Retorno JSON Estruturado**: A IA responde em formato JSON validado contendo a chave booleana `"valido"` e `"motivo"` (descrição explicativa do status). Se inválido, impede a criação da proposta e emite o alerta ao investidor.

---

## 📝 2. Geração Dinâmica de Contratos por IA

Os contratos de mútuo conversível são inteiramente gerados por IA e atualizados dinamicamente:

- **Injeção de Parâmetros**: A função [`gerar_contrato_com_ia`](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/investidores/views.py#L312-L425) extrai automaticamente:
  - Nome completo e e-mail do **Investidor**.
  - Nome completo e e-mail do **Empresário** (dono da startup beneficiada).
  - Valor do mútuo, percentual de equity e estágio da empresa.
  - **Data e Horário do registro eletrônico da transação**.
- **Motor de IA & Intercalação**: Os motores de IA são intercalados dinamicamente através de um sorteio aleatório (shuffle-loop) a cada requisição de contrato, alternando o uso de prioridade entre o Google Gemini e o Ollama local (`llama3.2`). Caso o primeiro motor selecionado falhar ou estiver sem credenciais de acesso, o sistema tenta imediatamente o segundo. Se ambos falharem, o sistema renderiza o template jurídico fallback padrão em HTML.
- **Registro Eletrônico**: O preâmbulo e o rodapé do documento gerado são marcados com a data e horário exatos em que a assinatura eletrônica foi realizada.

---

## 📅 3. Timestamp e Auditoria no Painel do Empresário

No modelo `PropostaInvestimento` de [investidores/models.py](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/investidores/models.py), adicionamos o campo `data_criacao` que persiste automaticamente a data/hora exata em que o investidor concluiu a assinatura e enviou a proposta.

No painel de gerenciamento do empresário ([empresa.html](file:///c:/Users/Kaue_Martins/Desktop/New-startse-main/empresarios/templates/empresa.html#L170-L177)), cada solicitação de investimento pendente exibe de forma clara e dinâmica a informação temporal: `"Enviado em: DD/MM/AAAA às HH:MM"`.

---
*Manual técnico de inteligência artificial de KYC elaborado sob a coordenação de Barba-Branca.*
