#!/bin/bash

# --- Script de Instalação Automática S.A.K.A. para Ubuntu VPS ---
# Autor: Antigravity AI
# Alvo: Ubuntu 22.04+ no Azure

echo "🚀 Iniciando instalação do Sistema S.A.K.A. (Sistema de Agentes Kamila Autônomos)..."

# 1. Atualizar o sistema
echo "📦 Atualizando pacotes do sistema..."
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependências básicas
echo "🛠️ Instalando Python e ferramentas essenciais..."
sudo apt install -y python3-pip python3-venv curl git build-essential

# 3. Instalar o Ollama (Provedor de LLM Local)
echo "🧠 Instalando Ollama..."
if ! command -v ollama &> /dev/null
then
    curl -fsSL https://ollama.com/install.sh | sh
    echo "✅ Ollama instalado com sucesso."
else
    echo "✅ Ollama já está instalado."
fi

# --- GARANTINDO A PORTA 11434 ABERTA NO UBUNTU ---
echo "🛡️ Configurando Firewall do Ubuntu (UFW)..."
sudo ufw allow 11434/tcp
sudo ufw allow ssh
sudo ufw --force enable

# --- CONFIGURANDO OLLAMA PARA ACEITAR CONEXÕES EXTERNAS ---
echo "⚙️ Configurando Ollama para escutar em todas as interfaces..."
sudo mkdir -p /etc/systemd/system/ollama.service.d
echo '[Service]
Environment="OLLAMA_HOST=0.0.0.0"' | sudo tee /etc/systemd/system/ollama.service.d/override.conf

# Reiniciar Ollama para aplicar as mudanças
sudo systemctl daemon-reload
sudo systemctl restart ollama

# 4. Baixar os modelos necessários
echo "📥 Baixando modelos LLM (llama3 e llava)..."
ollama pull llama3
ollama pull llava

# 5. Criar Ambiente Virtual Python
echo "🐍 Configurando ambiente Python..."
cd "$(dirname "$0")"
python3 -m venv venv
source venv/bin/activate

# 6. Instalar dependências do projeto
echo "📚 Instalando bibliotecas Python do S.A.K.A..."
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "⚠️ Arquivo requirements.txt não encontrado!"
fi

echo "------------------------------------------------------------"
echo "✅ INSTALAÇÃO E CONFIGURAÇÃO DE REDE CONCLUÍDAS!"
echo "------------------------------------------------------------"
echo "⚠️ NOTA IMPORTANTE PARA AZURE:"
echo "O script abriu a porta no Ubuntu, mas você também deve abrir"
echo "a porta 11434 no Portal do Azure (Network Security Group)."
echo "------------------------------------------------------------"
echo "Para rodar o sistema:"
echo "1. source venv/bin/activate"
echo "2. python3 main.py"
echo "------------------------------------------------------------"
