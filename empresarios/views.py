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
import google.generativeai as genai
# ============================================================================
from .utils import realizar_due_diligence, validar_cnpj_api



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

        if not nome or not cnpj or not site or not descricao or not data_final or not percentual_equity or not valor or not pitch or not logo:
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos.')
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

def listar_empresas(request):
    if  not request.user.is_authenticated:
        return redirect('/usuarios/logar')
    if request.method == "GET":
        nome_empresa = request.GET.get('empresa')
        empresas = Empresas.objects.filter(user=request.user)

        if nome_empresa:
            empresas = empresas.filter(nome__icontains=nome_empresa)

        return render(request, 'listar_empresas.html', {'empresas': empresas, 'nome_empresa': nome_empresa})
    
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

def gerenciar_proposta(request, id):
    acao = request.GET.get('acao')
    pi = PropostaInvestimento.objects.get(id=id)
    
    if acao.lower() == 'aceitar':
        messages.add_message(request, constants.SUCCESS, 'Proposta aceita')
        pi.status = 'PA'
    elif acao.lower() == 'recusar' or acao.lower() == 'negar':
        messages.add_message(request, constants.SUCCESS, 'Proposta recusada!')
        pi.status = 'PR'
    
    pi.save()
    return redirect(f"/empresarios/empresa/{pi.empresa.id}")

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
        # USA GOOGLE GEMINI
        try:
            genai.configure(api_key=api_key)
            model_gemini = genai.GenerativeModel("gemini-1.5-flash")
            response = model_gemini.generate_content(prompt)
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
        except Exception as e:
            analysis = f"Erro ao gerar análise: {str(e)}"

    return render(request, 'analise_ia_empresario.html', {'analysis': analysis, 'empresa': empresa})

