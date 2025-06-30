# Plataforma de Crowdfunding - Django

Este projeto é uma plataforma de financiamento coletivo onde empreendedores podem cadastrar ideias e investidores podem apoiar.

## 🚀 Tecnologias
- Python 3.10+
- Django 4.x
- SQLite/PostgreSQL
- HTML, CSS, Bootstrap
- Git/GitHub

## ⚙️ Instalação local

```bash
git clone https://github.com/seu-usuario/seu-projeto.git
cd seu-projeto
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver




## 🧪 Testes

python manage.py test

## 🤝 Contribuindo


---

### 🗃️ 1.3. Estrutura de pastas
Adicione um arquivo `docs/estrutura.md` (ou no README) explicando **a organização do projeto**.

```markdown
## Estrutura de pastas

- empresario/ ➜ app para usuários que criam campanhas
- investidor/ ➜ app para usuários que investem nas campanhas
- core/ ➜ configurações globais
- templates/ ➜ arquivos HTML separados por app
