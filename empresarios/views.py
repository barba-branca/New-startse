from django.shortcuts import render, redirect
from .models import Empresas, Documento, Metricas
from django.contrib import messages
from django.contrib.messages import constants
from investidores.models import PropostaInvestimento
from django.http import HttpResponse, Http404
from django.conf import settings
import requests
import os
import traceback
# ============================================================================
# OPÇÃO DE IA: Descomente a linha abaixo para usar Google Gemini ao invés do Ollama
from google import genai
# ============================================================================
from .utils import realizar_due_diligence, validar_cnpj_api



from functools import wraps

def empresario_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'perfil') and request.user.perfil.role == 'I':
            messages.add_message(request, constants.WARNING, 'Esta área é de acesso exclusivo para Empresários. Você foi redirecionado.')
            return redirect('/investidores/painel/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@empresario_required
def cadastrar_empresa(request):
    if  not request.user.is_authenticated:
        return redirect('/usuarios/logar')

    if request.method == "GET":      
        return render(request,'cadastrar_empresa.html',
                      {'tempo_existencia': Empresas.tempo_existencia_choices,
                       'areas': Empresas.area_choices})
    
    elif request.method == "POST":
        nome = request.POST.get('nome')
        cnpj = request.POST.get('cnpj')
        site = request.POST.get('site')
        tempo_existencia = request.POST.get('tempo_existencia')
        descricao = request.POST.get('descricao')
        data_final = request.POST.get('data_final')
        percentual_equity = request.POST.get('percentual_equity')
        estagio = request.POST.get('estagio')
        area = request.POST.get('area')
        publico_alvo = request.POST.get('publico_alvo')
        valor = request.POST.get('valor')
        pitch = request.FILES.get('pitch')
        logo = request.FILES.get('logo')

        missing = []
        for key, val in {
            'nome': nome,
            'cnpj': cnpj,
            'site': site,
            'tempo_existencia': tempo_existencia,
            'descricao': descricao,
            'area': area,
            'publico_alvo': publico_alvo,
            'estagio': estagio,
            'data_final': data_final,
            'percentual_equity': percentual_equity,
            'valor': valor,
            'pitch': pitch,
            'logo': logo,
        }.items():
            if val is None or val == '':
                missing.append(key)

        if missing:
            messages.add_message(
                request,
                constants.ERROR,
                'Preencha todos os campos. Faltando: ' + ', '.join(missing)
            )
            return redirect('/empresarios/cadastrar_empresa')

        try:
            # Validar CNPJ via API
            resultado_cnpj = validar_cnpj_api(cnpj)
            
            if not resultado_cnpj.get('valido', False):
                erro_cnpj = resultado_cnpj.get('erro', 'CNPJ inválido')
                messages.add_message(request, constants.ERROR, f'Erro no CNPJ: {erro_cnpj}')
                return redirect('/empresarios/cadastrar_empresa')
            
            # Se o CNPJ foi validado com sucesso e tem dados, mostra informação
            if resultado_cnpj.get('razao_social'):
                messages.add_message(request, constants.INFO, 
                    f"CNPJ validado: {resultado_cnpj.get('razao_social')} - {resultado_cnpj.get('situacao', 'N/A')}")
            
            # Validar campos numéricos
            try:
                percentual_equity_int = int(percentual_equity)
                if percentual_equity_int <= 0 or percentual_equity_int > 100:
                    messages.add_message(request, constants.ERROR, 'Percentual deve ser entre 0 e 100')
                    return redirect('/empresarios/cadastrar_empresa')
            except (ValueError, TypeError):
                messages.add_message(request, constants.ERROR, 'Percentual de equity inválido')
                return redirect('/empresarios/cadastrar_empresa')

            try:
                valor_decimal = float(valor)
                if valor_decimal <= 0:
                    messages.add_message(request, constants.ERROR, 'O valor deve ser positivo')
                    return redirect('/empresarios/cadastrar_empresa')
            except (ValueError, TypeError):
                messages.add_message(request, constants.ERROR, 'Valor a captar inválido')
                return redirect('/empresarios/cadastrar_empresa')

            # Validar data
            if not data_final:
                messages.add_message(request, constants.ERROR, 'Data final é obrigatória')
                return redirect('/empresarios/cadastrar_empresa')
            
            # Validar estágio
            if not estagio:
                messages.add_message(request, constants.ERROR, 'Selecione o estágio da empresa')
                return redirect('/empresarios/cadastrar_empresa')

            empresa = Empresas(
                user=request.user,
                nome=nome,
                cnpj=cnpj,
                site=site,
                tempo_existencia=tempo_existencia,
                descricao=descricao,
                data_final_captacao=data_final,
                percentual_equity=percentual_equity_int,
                estagio=estagio,
                area=area,
                publico_alvo=publico_alvo,
                valor=valor_decimal,
                taxa_intermediacao=valor_decimal * 0.02,
                valor_liquido=valor_decimal - (valor_decimal * 0.02),
                pitch=pitch,
                logo=logo
            )
            
            empresa.save()
            realizar_due_diligence(empresa)
            
        except ValueError as e:
            messages.add_message(request, constants.ERROR, f'Valor inválido: {str(e)}')
            return redirect('/empresarios/cadastrar_empresa')
        except Exception as e:
            # Log do erro para debugging
            print(f"[ERRO CADASTRO EMPRESA] {type(e).__name__}: {str(e)}")
            print(traceback.format_exc())
            
            # Mensagem mais informativa (sem expor detalhes sensíveis)
            erro_tipo = type(e).__name__
            if 'date' in str(e).lower() or 'data' in str(e).lower():
                messages.add_message(request, constants.ERROR, 'Erro: Data inválida. Use o formato correto.')
            elif 'null' in str(e).lower() or 'none' in str(e).lower() or 'required' in str(e).lower():
                messages.add_message(request, constants.ERROR, 'Erro: Preencha todos os campos obrigatórios.')
            elif 'file' in str(e).lower() or 'upload' in str(e).lower():
                messages.add_message(request, constants.ERROR, 'Erro: Problema no upload de arquivos. Tente novamente.')
            else:
                messages.add_message(request, constants.ERROR, f'Erro no cadastro ({erro_tipo}). Verifique os dados e tente novamente.')
            return redirect('/empresarios/cadastrar_empresa')
        
        messages.add_message(request, constants.SUCCESS, 'Empresa criada com sucesso')
        return redirect('/empresarios/cadastrar_empresa')

import logging
import traceback
import sys
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

@login_required(login_url='/usuarios/logar')
@empresario_required
def listar_empresas(request):
    try:
        # Log de diagnóstico
        logger.info(f"User: {request.user.id}, Authenticated: {request.user.is_authenticated}")
        
        nome_empresa = request.GET.get('empresa', '')
        
        # Testa a query primeiro
        try:
            empresas = Empresas.objects.filter(user=request.user)
            logger.info(f"Empresas encontradas: {empresas.count()}")
            
            if nome_empresa:
                empresas = empresas.filter(nome__icontains=nome_empresa)
                logger.info(f"Após filtro por nome: {empresas.count()}")
        except Exception as db_error:
            logger.error(f"Erro no banco de dados: {db_error}")
            return HttpResponse(
                f"<h1>Erro no banco de dados</h1><pre>{traceback.format_exc()}</pre>",
                status=500
            )
        
        # Testa renderização com o template
        context = {
            'empresas': empresas,
            'nome_empresa': nome_empresa,
        }
        
        return render(request, 'listar_empresas.html', context)
        
    except Exception as e:
        # Log completo
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_details = {
            'tipo': str(exc_type),
            'mensagem': str(e),
            'traceback': traceback.format_exc(),
            'user_id': request.user.id if request.user.is_authenticated else 'Anônimo',
        }
        
        logger.error(f"Erro fatal em listar_empresas: {error_details}")
        
        # Retorna HTML simples (não use render aqui!)
        return HttpResponse(
            f"""
            <html>
            <head><title>Erro 500</title></head>
            <body>
                <h1>Erro no servidor</h1>
                <h2>Tipo: {error_details['tipo']}</h2>
                <p><strong>Mensagem:</strong> {error_details['mensagem']}</p>
                <pre>{error_details['traceback']}</pre>
            </body>
            </html>
            """,
            content_type="text/html",
            status=500
        )
    
@empresario_required
def empresa(request, id):
    empresa = Empresas.objects.get(id=id)
    if empresa.user != request.user:
        messages.add_message(request,constants.ERROR, 'Essa empresa nao é sua.')
        return redirect(f'/empresarios/listar_empresas')
    

    if request.method == "GET":
        documentos = Documento.objects.filter(empresa=empresa)
        propostas_investimentos = PropostaInvestimento.objects.filter(empresa=empresa)
        
        
        proposta_investimentos_enviada = propostas_investimentos.filter(status='PE')

        # Valuation Projection Logic
        current_valuation = float(empresa.valuation)
        valuation_labels = ['Atual']
        valuation_data = [current_valuation]

        for i in range(1, 6):
            valuation_labels.append(f'{2024 + i}') # Assuming current year is 2024, can be dynamic
            valuation_data.append(current_valuation * (1.2 ** i)) # 20% annual growth

        return render(request, 'empresa.html', {
            'empresa': empresa,
            'documentos': documentos,
            'proposta_investimentos_enviada': proposta_investimentos_enviada,
            'valuation_labels': valuation_labels,
            'valuation_data': valuation_data
        })
        
def add_doc(request, id):
    empresa = Empresas.objects.get(id=id)
    titulo = request.POST.get('titulo')
    arquivo = request.FILES.get('arquivo')
    extensao = arquivo.name.split('.')

    if empresa.user != request.user:
        messages.add_message(request,constants.ERROR, 'Essa empresa nao é sua.')
        return redirect(f'/empresarios/listar_empresas')

    if extensao[-1] != 'pdf':
        messages.add_message(request, constants.ERROR, "Envie apenas PDF's" )
        return redirect(f'/empresarios/empresa/{id}')

    if not arquivo:
        messages.add_message(request, constants.ERROR, 'Envie um arquivo.')
        return redirect(f'/empresarios/empresa/{id}')

    documento = Documento(
        empresa=empresa,
        titulo=titulo,
        arquivo=arquivo
    )

    documento.save()

    messages.add_message(request, constants.SUCCESS, 'Arquivo cadastrado com sucesso')
    return redirect(f'/empresarios/empresa/{id}')

def excluir_dc(request, id):
    documento = Documento.objects.get(id=id)
    if documento.empresa.user != request.user:
        messages.add_message(request, constants.ERROR, "Esse documento não é seu")
        return redirect(f'/empresarios/empresa/{documento.empresa.id}')
    
    documento.delete()
    messages.add_message(request, constants.SUCCESS, 'documento deletado com sucesso.')
    return redirect(f'/empresarios/empresa/{documento.empresa.id}')

def add_metrica(request, id):
    empresa = Empresas.objects.get(id=id)
    titulo = request.POST.get('titulo')
    valor = request.POST.get('valor')
    
    metrica = Metricas(
        empresa=empresa,
        titulo=titulo,
        valor=valor
    )
    metrica.save()
    
    messages.add_message(request, constants.SUCCESS, "Métrica cadastrada com sucesso")
    return redirect(f'/empresarios/empresa/{empresa.id}')

@empresario_required
def gerenciar_proposta(request, id):
    acao = request.GET.get('acao')
    pi = PropostaInvestimento.objects.get(id=id)
    
    if acao.lower() == 'aceitar':
        from decimal import Decimal
        import stripe
        
        stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
        
        valor_total = float(pi.valor)
        taxa_plataforma = valor_total * 0.02 # 2% Platform Fee
        valor_empreendedor = valor_total - taxa_plataforma
        try:
            # 1. Cria ou busca o Customer do investidor (trata e-mail vazio)
            email_investidor = pi.investidor.email
            if not email_investidor or '@' not in str(email_investidor):
                email_investidor = f"investidor_{pi.investidor.id}@newstartse.com.br"
                
            nome_investidor = f"{pi.investidor.first_name} {pi.investidor.last_name}".strip()
            if not nome_investidor:
                nome_investidor = pi.investidor.username
                
            customer = stripe.Customer.create(
                email=email_investidor,
                name=nome_investidor
            )
            
            # 2. Cria conta conectada para o empresário (dono da startup)
            email_empresario = pi.empresa.user.email
            if not email_empresario or '@' not in str(email_empresario):
                email_empresario = f"empresario_{pi.empresa.user.id}@newstartse.com.br"
                
            connected_account = stripe.Account.create(
                type='custom',
                country='BR',
                email=email_empresario,
                capabilities={
                    'card_payments': {'requested': True},
                    'transfers': {'requested': True},
                },
            )
            
            # 3. Cria a cobrança com split de pagamento (Destination Charge)
            amount_cents = int(valor_total * 100)
            fee_cents = int(taxa_plataforma * 100)
            
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='brl',
                customer=customer.id,
                application_fee_amount=fee_cents,
                transfer_data={
                    'destination': connected_account.id,
                },
                description=f"Aporte na startup {pi.empresa.nome} - Proposta #{pi.id}",
                confirm=True,
                payment_method="pm_card_visa", # Cartão de testes padrão do Stripe
            )
            
            pi.status = 'PA'
            pi.save()
            
            # Atualiza os valores na empresa
            pi.empresa.taxa_intermediacao = pi.empresa.taxa_intermediacao + Decimal(str(taxa_plataforma))
            pi.empresa.valor_liquido = pi.empresa.valor_liquido + Decimal(str(valor_empreendedor))
            pi.empresa.save()
            
            messages.add_message(request, constants.SUCCESS, f'Proposta aceita com sucesso! Débito automático de R$ {valor_total:,.2f} efetuado via Stripe com Split de 2% de taxa.')
            
        except Exception as stripe_error:
            # Fallback local se o Stripe falhar ou não estiver configurado
            pi.status = 'PA'
            pi.save()
            
            pi.empresa.taxa_intermediacao = pi.empresa.taxa_intermediacao + Decimal(str(taxa_plataforma))
            pi.empresa.valor_liquido = pi.empresa.valor_liquido + Decimal(str(valor_empreendedor))
            pi.empresa.save()
            
            print(f"[STRIPE SPLIT ERROR] {str(stripe_error)}")
            messages.add_message(request, constants.SUCCESS, f'Proposta aceita! (Nota: O processamento do Split Stripe foi simulado localmente com 2% de taxa: {str(stripe_error)})')
            
    elif acao.lower() == 'recusar' or acao.lower() == 'negar':
        messages.add_message(request, constants.SUCCESS, 'Proposta recusada!')
        pi.status = 'PR'
        pi.save()
        
    return redirect(f"/empresarios/empresa/{pi.empresa.id}")

@empresario_required
def analise_ia_empresario(request, id):
    """
    Análise de pitch usando IA
    
    OPÇÕES DISPONÍVEIS:
    1. Ollama (Open Source - Local) - Ativo por padrão
    2. Google Gemini (API) - Comentado abaixo
    """
    empresa = Empresas.objects.get(id=id)
    if empresa.user != request.user:
        messages.add_message(request, constants.ERROR, "Você não tem permissão para analisar esta empresa.")
        return redirect(f'/empresarios/listar_empresas')

    prompt = f"""Você é um investidor experiente analisando um pitch de startup.

Analise a seguinte empresa:

**Nome:** {empresa.nome}
**Área de Atuação:** {empresa.get_area_display()}
**Descrição:** {empresa.descricao}
**Estágio:** {empresa.get_estagio_display()}
**Valuation Esperado:** R$ {empresa.valuation}

Por favor, forneça uma análise completa incluindo:

## 💪 3 Pontos Fortes
Liste 3 pontos fortes do seu negócio/pitch.

## 📈 3 Melhorias Sugeridas
Liste 3 melhorias que você poderia fazer no negócio ou na descrição.

## 💡 Dica Final
Dê uma dica valiosa para melhorar as chances de conseguir investimento.

Responda em português brasileiro de forma clara e profissional."""

    # ============================================================================
    # LÓGICA DE IA: Tenta Gemini primeiro, se tiver API Key, senão usa Ollama
    # ============================================================================
    
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if api_key:
        # USA GOOGLE GEMINI (MODERNO)
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            analysis = response.text
        except Exception as e:
            analysis = f"Erro ao gerar análise com Gemini: {str(e)}"
    else:
        # USA OLLAMA (Local)
        ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        model_ollama = os.environ.get("OLLAMA_MODEL", "llama3.2")
        
        try:
            response = requests.post(
                f"{ollama_url}/api/generate",
                json={
                    "model": model_ollama,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result.get("response", "Não foi possível gerar a análise.")
            else:
                analysis = f"Erro ao conectar com Ollama: Status {response.status_code}. Verifique se o Ollama está rodando."
                
        except requests.exceptions.ConnectionError:
            analysis = """⚠️ **Ollama não está rodando!**

Para usar a Análise de IA, siga os passos:

1. **Instale o Ollama:** https://ollama.ai/download
2. **Baixe um modelo:** `ollama pull llama3.2`
3. **O Ollama rodará automaticamente em segundo plano**

Após isso, a análise funcionará automaticamente."""
        except requests.exceptions.Timeout:
            analysis = """⚠️ **Tempo limite esgotado (Timeout)!**

O Ollama demorou mais de 2 minutos para processar a resposta. Isso geralmente ocorre se:
1. **O processamento está sendo rodado em CPU lenta** (sem placa de vídeo dedicada).
2. **O modelo está sendo carregado na memória pela primeira vez**.

**Como resolver:**
- **Recomendado**: Edite o arquivo `.env` na raiz do projeto e altere o `OLLAMA_MODEL` para o modelo mais leve de 1B de parâmetros que você já tem instalado:
  ```env
  OLLAMA_MODEL=llama3.2:1b
  ```
- Alternativamente, tente novamente em alguns instantes, pois a segunda execução costuma ser muito mais rápida após o modelo ser carregado na RAM."""
        except Exception as e:
            analysis = f"Erro ao gerar análise: {str(e)}"

    return render(request, 'analise_ia_empresario.html', {'analysis': analysis, 'empresa': empresa})

