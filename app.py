import os
import sqlite3
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Importações da nossa arquitetura modular
from src.database import preparar_banco_amazon

# =====================================================================
# 1. CONFIGURAÇÃO DA INTERFACE (STREAMLIT)
# =====================================================================
st.set_page_config(
    page_title="Copiloto de Varejo IA",
    page_icon="🛒",
    layout="wide"
)

# Carrega as variáveis de ambiente
load_dotenv()


# =====================================================================
# 2. CACHE & INICIALIZAÇÃO DE ESTADOS
# =====================================================================
@st.cache_resource
def iniciar_banco_dados():
    return preparar_banco_amazon()


@st.cache_resource
def get_llm():
    # Instancia o LLM uma única vez para máxima performance
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=0)


# Inicializa as variáveis da sessão
if "messages" not in st.session_state:
    st.session_state.messages = []

if "tokens_gastos" not in st.session_state:
    st.session_state.tokens_gastos = {"prompt": 0, "completion": 0}

if "latest_logs" not in st.session_state:
    st.session_state.latest_logs = "*Faça uma pergunta no chat para ver a geração da query SQL aqui.*"

# Variáveis para a funcionalidade Human-in-the-Loop (Segurança)
if "pending_sql" not in st.session_state:
    st.session_state.pending_sql = None

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# =====================================================================
# 3. BARRA LATERAL (SIDEBAR)
# =====================================================================
with st.sidebar:
    st.title("⚙️ Configurações")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("❌ ERRO: GROQ_API_KEY não encontrada.")
        st.stop()
    else:
        st.success("✅ API Groq Conectada")

    st.divider()

    with st.spinner("A verificar integridade dos dados..."):
        sucesso_db, msg_db = iniciar_banco_dados()
        if sucesso_db:
            st.success("Base de dados pronta.")
        else:
            st.error(msg_db)
            st.stop()

    st.divider()
    st.markdown("""
    **Dicas de Perguntas:**
    - *Qual é a média geral das notas?*
    - *Liste as notas e as quantidades correspondentes (Gráfico).*
    - *Quais os 5 produtos mais avaliados?*
    """)

# =====================================================================
# 4. ÁREA PRINCIPAL COM ABAS (TABS)
# =====================================================================
st.title("🛒 Copiloto de Dados - E-commerce")

# Novas Abas com foco em Produto e Data Science
tab_dashboard, tab_chat, tab_logs, tab_finops = st.tabs([
    "📈 Visão Geral (KPIs)",
    "💬 Chat e Análises",
    "🧠 Raciocínio (Logs)",
    "💰 Painel FinOps"
])

# ---------------------------------------------------------------------
# ABA 1: DASHBOARD DE KPIs (MÉTRICAS EM TEMPO REAL)
# ---------------------------------------------------------------------
with tab_dashboard:
    st.markdown("### Painel de Gestão")
    st.markdown("Estes indicadores são calculados em tempo real consultando a base de dados.")

    try:
        conn = sqlite3.connect("amazon_reviews.db")

        # Consultas de KPIs Rápidos
        total_reviews = pd.read_sql("SELECT COUNT(*) as count FROM avaliacoes", conn).iloc[0]['count']
        avg_rating = pd.read_sql("SELECT AVG(rating) as avg FROM avaliacoes", conn).iloc[0]['avg']
        five_star = pd.read_sql("SELECT COUNT(*) as count FROM avaliacoes WHERE rating = 5", conn).iloc[0]['count']

        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Avaliações", f"{total_reviews:,}")
        col2.metric("Média de Notas", f"{avg_rating:.2f} ⭐")
        col3.metric("Avaliações 5 Estrelas", f"{five_star:,}")

        st.divider()

        # Geração de Gráficos Nativos
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("**Distribuição de Notas dos Clientes**")
            df_ratings = pd.read_sql(
                "SELECT rating, COUNT(*) as quantidade FROM avaliacoes GROUP BY rating ORDER BY rating", conn)
            if not df_ratings.empty:
                st.bar_chart(df_ratings.set_index('rating'))

        with col_c2:
            st.markdown("**Identificadores Mais Frequentes (Amostra)**")
            colunas_existentes = pd.read_sql("PRAGMA table_info(avaliacoes)", conn)['name'].tolist()
            # Tenta encontrar a coluna de ID de produto baseada nos esquemas comuns da Amazon
            coluna_produto = 'parent_asin' if 'parent_asin' in colunas_existentes else (
                'asin' if 'asin' in colunas_existentes else None)

            if coluna_produto:
                df_prod = pd.read_sql(
                    f"SELECT {coluna_produto} as Produto, COUNT(*) as Qtd FROM avaliacoes GROUP BY {coluna_produto} ORDER BY Qtd DESC LIMIT 5",
                    conn)
                st.bar_chart(df_prod.set_index('Produto'))
            else:
                st.info("Distribuição de produtos indisponível (Coluna de ID não encontrada).")

        conn.close()
    except Exception as e:
        st.warning(f"O banco de dados ainda não foi criado ou ocorreu um erro: {e}")

# ---------------------------------------------------------------------
# ABA 2: CHAT DE DADOS (TEXT-TO-SQL + HITL + EXPORT + CHARTS)
# ---------------------------------------------------------------------
with tab_chat:
    # 1. Renderiza o histórico (Texto, Tabelas, Gráficos e Botões de Exportação)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Se a mensagem contiver um DataFrame, mostramos os extras visuais
            if "dataframe" in message and message["dataframe"] is not None:
                df_hist = message["dataframe"]

                with st.expander("📊 Ver Tabela de Dados e Gráficos"):
                    st.dataframe(df_hist)

                    # Funcionalidade 1: Exportar para CSV On-Demand
                    csv_data = df_hist.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Exportar Dados (CSV)",
                        data=csv_data,
                        file_name="analise_exportada.csv",
                        mime="text/csv",
                        key=f"dl_{id(message)}"  # Chave única obrigatória no Streamlit
                    )

                    # Funcionalidade 2: Geração Dinâmica de Gráficos (Heurística)
                    if len(df_hist.columns) >= 2 and len(df_hist) > 1:
                        df_plot = df_hist.set_index(df_hist.columns[0])
                        num_cols = df_plot.select_dtypes(include=['number']).columns
                        if len(num_cols) > 0:
                            st.markdown("**Visualização Automática:**")
                            st.bar_chart(df_plot[num_cols])

    # 2. Funcionalidade 3: Human-in-the-Loop com SELF-HEALING (Auto-Correção)
    if st.session_state.pending_sql:
        with st.chat_message("assistant"):
            st.warning(
                "🛡️ **Revisão de Segurança Necessária (Human-in-the-Loop)**\n\nO Agente IA gerou o código abaixo para consultar a base de dados. Aprove para executar:")
            st.code(st.session_state.pending_sql, language="sql")

            c1, c2 = st.columns(2)
            if c1.button("✅ Aprovar e Executar", use_container_width=True):
                with st.spinner("A executar a consulta com sistema de Auto-Correção (Self-Healing)..."):
                    conn = sqlite3.connect("amazon_reviews.db")
                    current_sql = st.session_state.pending_sql
                    df_resultado = None
                    sucesso = False

                    # --- NOVIDADE: LOOP DE SELF-HEALING (AUTO-CORREÇÃO) ---
                    # O sistema tentará corrigir erros de SQL automaticamente até 3 vezes
                    for tentativa in range(3):
                        try:
                            df_resultado = pd.read_sql(current_sql, conn)
                            sucesso = True
                            break  # O SQL funcionou perfeitamente!
                        except Exception as erro_sql:
                            if tentativa < 2:
                                st.toast(
                                    f"⚠️ Erro SQL detetado. A IA está a tentar corrigir autonomamente (Tentativa {tentativa + 1}/2)...")

                                # Recupera o esquema para o contexto
                                schema = pd.read_sql("PRAGMA table_info(avaliacoes)", conn)[
                                    ['name', 'type']].to_string()

                                # Prompt de Auto-Correção
                                fix_prompt = f"""A seguinte query SQL falhou com um erro:
                                Query Inválida: {current_sql}
                                Erro do Banco de Dados: {str(erro_sql)}

                                Esquema da Tabela 'avaliacoes':
                                {schema}

                                Corrija a query. Pode ser um erro de sintaxe ou nome de coluna inexistente.
                                Retorne APENAS a query SQL corrigida e válida. NADA MAIS. Não use blocos de código markdown."""

                                llm = get_llm()
                                res_fix = llm.invoke([HumanMessage(content=fix_prompt)])

                                # Monitorização FinOps
                                usage = res_fix.response_metadata.get("token_usage", {})
                                st.session_state.tokens_gastos["prompt"] += usage.get("prompt_tokens", 0)
                                st.session_state.tokens_gastos["completion"] += usage.get("completion_tokens", 0)

                                # Atualiza a query com a correção sugerida e regista nos logs
                                current_sql = res_fix.content.replace("```sql", "").replace("```", "").strip()
                                st.session_state.latest_logs += f"\n\n### 🔧 Auto-Correção Efetuada (Tentativa {tentativa + 1})\n**Erro Capturado:** `{str(erro_sql)}`\n**Nova Query Testada:**\n```sql\n{current_sql}\n```"
                            else:
                                st.error(
                                    f"❌ O Agente não conseguiu corrigir a query após 3 tentativas. Erro final: {str(erro_sql)}")
                                break
                    # -------------------------------------------------------

                    conn.close()

                    if sucesso:
                        # --- NOVIDADE: NEXT BEST ACTION (SUGESTÕES PREDITIVAS) ---
                        llm = get_llm()
                        sum_prompt = f"""A pergunta original do utilizador foi: '{st.session_state.pending_question}'. 
                        O banco de dados retornou a seguinte tabela de resultados:
                        {df_resultado.head(10).to_string()}

                        Tarefa 1: Crie um resumo profissional e focado em negócios com estes dados, respondendo diretamente à pergunta.
                        Tarefa 2: Ao final do seu resumo, adicione uma secção chamada "💡 **Próximas Análises Sugeridas**". Forneça 3 perguntas analíticas (em formato de lista com marcadores) que o utilizador poderia fazer a seguir para aprofundar os insights sobre estes dados recém-descobertos.
                        """
                        sum_res = llm.invoke([HumanMessage(content=sum_prompt)])

                        # Monitorização FinOps
                        usage = sum_res.response_metadata.get("token_usage", {})
                        st.session_state.tokens_gastos["prompt"] += usage.get("prompt_tokens", 0)
                        st.session_state.tokens_gastos["completion"] += usage.get("completion_tokens", 0)

                        # Guarda no histórico (incluindo o Dataframe e a versão final do SQL que funcionou)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": sum_res.content,
                            "dataframe": df_resultado,
                            "sql": current_sql
                        })

                        # Limpa o estado pendente e atualiza a tela
                        st.session_state.pending_sql = None
                        st.session_state.pending_question = None
                        st.rerun()
                    else:
                        # Se a auto-correção falhou totalmente
                        st.session_state.pending_sql = None
                        st.rerun()

            if c2.button("❌ Recusar", use_container_width=True):
                st.session_state.messages.append({"role": "assistant",
                                                  "content": "A execução da query foi bloqueada pelo utilizador por motivos de segurança."})
                st.session_state.pending_sql = None
                st.rerun()

    # 3. Caixa de Entrada do Utilizador (Se não houver aprovação pendente)
    else:
        if pergunta := st.chat_input("Ex: Qual é a avaliação média dos produtos?"):
            st.session_state.messages.append({"role": "user", "content": pergunta})
            st.session_state.pending_question = pergunta

            with st.chat_message("user"):
                st.markdown(pergunta)

            with st.chat_message("assistant"):
                with st.spinner("A traduzir a pergunta para código SQL..."):

                    # Lê dinamicamente as colunas do banco para dar contexto à IA
                    conn = sqlite3.connect("amazon_reviews.db")
                    schema = pd.read_sql("PRAGMA table_info(avaliacoes)", conn)[['name', 'type']].to_string()
                    conn.close()

                    # --- NOVIDADE: PIPELINE TEXT-TO-SQL COM MEMÓRIA CONVERSACIONAL ---
                    llm = get_llm()
                    sys_prompt = f"""Você é um Analista de Dados Especialista em SQLite.
                    Esquema da tabela 'avaliacoes':
                    {schema}

                    REGRAS:
                    1. Se a pergunta exigir dados da tabela, devolva APENAS a query SQL válida. Não use blocos de código markdown (```sql) ou explicações de texto. 
                    2. Se a pergunta se referir a algo dito anteriormente (ex: "e quais são os piores?", "quais os comentários dele?"), use o histórico da conversa para criar o SQL correto.
                    3. Nunca gere queries com UPDATE, DELETE, INSERT ou DROP.
                    4. Se a pergunta for um simples olá, responda começando EXATAMENTE com a palavra 'CHAT: '.
                    """

                    # Constrói o histórico de mensagens para dar "Memória" à IA
                    mensagens_llm = [SystemMessage(content=sys_prompt)]

                    # Pega apenas nas últimas 4 interações (para poupar tokens e focar no contexto recente)
                    for msg in st.session_state.messages[-4:]:
                        if msg["role"] == "user":
                            mensagens_llm.append(HumanMessage(content=msg["content"]))
                        elif msg["role"] == "assistant" and "dataframe" not in msg:
                            # Adicionamos respostas de chat normais.
                            # Limitamos o tamanho para evitar estourar o limite do LLM.
                            mensagens_llm.append(AIMessage(content=msg["content"][:300]))

                    # Adiciona a pergunta atual
                    mensagens_llm.append(HumanMessage(content=pergunta))

                    # Invoca o modelo com toda a memória
                    resposta_bruta = llm.invoke(mensagens_llm)
                    texto_resposta = resposta_bruta.content.strip()

                    # Monitorização FinOps
                    usage = resposta_bruta.response_metadata.get("token_usage", {})
                    st.session_state.tokens_gastos["prompt"] += usage.get("prompt_tokens", 0)
                    st.session_state.tokens_gastos["completion"] += usage.get("completion_tokens", 0)

                    if texto_resposta.startswith("CHAT:"):
                        # Se não precisar de SQL, responde direto
                        texto = texto_resposta.replace("CHAT:", "").strip()
                        st.session_state.messages.append({"role": "assistant", "content": texto})
                        st.markdown(texto)
                    else:
                        # Limpa eventuais marcadores markdown que o LLM possa ter injetado
                        clean_sql = texto_resposta.replace("```sql", "").replace("```", "").strip()

                        # Ativa o modo Human-in-the-Loop enviando o SQL para a variável pendente
                        st.session_state.pending_sql = clean_sql

                        # Atualiza os Logs (Aba 3) com o histórico de memória processado
                        contexto_memoria = "\n".join(
                            [f"- {m.type.capitalize()}: {m.content[:50]}..." for m in mensagens_llm if
                             m.type != "system"])

                        st.session_state.latest_logs = f"""### 🛠️ Tradução (Text-to-SQL com Memória)
**Pergunta Original:** {pergunta}

**Memória Ativada no Contexto:**
{contexto_memoria}

**Query Gerada Inicialmente:**
```sql
{clean_sql}
```
"""
                        st.rerun()

# ---------------------------------------------------------------------
# ABA 3: LOGS E RACIOCÍNIO (OBSERVABILIDADE)
# ---------------------------------------------------------------------
with tab_logs:
    st.markdown("### 🧠 Caixa Preta da Inteligência Artificial")
    st.markdown(
        "Acompanhe como a IA interpreta a estrutura do banco de dados e as exatas queries SQL que ela gera antes de pedir a sua aprovação.")
    st.divider()
    st.markdown(st.session_state.latest_logs)

# ---------------------------------------------------------------------
# ABA 4: PAINEL DE CUSTOS (FINOPS)
# ---------------------------------------------------------------------
with tab_finops:
    st.markdown("### Auditoria de Custos de Inteligência Artificial")

    p_tokens = st.session_state.tokens_gastos["prompt"]
    c_tokens = st.session_state.tokens_gastos["completion"]
    total_tokens = p_tokens + c_tokens

    # Preços Estimados: USD por 1 Milhão de Tokens
    preco_groq_prompt = 0.59
    preco_groq_completion = 0.79
    preco_gpt4_prompt = 5.00
    preco_gpt4_completion = 15.00

    custo_groq = (p_tokens / 1_000_000 * preco_groq_prompt) + (c_tokens / 1_000_000 * preco_groq_completion)
    custo_gpt4 = (p_tokens / 1_000_000 * preco_gpt4_prompt) + (c_tokens / 1_000_000 * preco_gpt4_completion)

    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Tokens Utilizados", f"{total_tokens:,}")
    col2.metric("Custo Real no Groq", f"${custo_groq:.4f}")
    col3.metric("Custo Estimado no GPT-4o", f"${custo_gpt4:.4f}")

    st.divider()
    if total_tokens > 0:
        st.success(
            f"💸 **Economia Acumulada:** Ao utilizar modelos eficientes, poupou **${(custo_gpt4 - custo_groq):.4f}** até ao momento.")
    else:
        st.info("Nenhuma interação realizada ainda. Faça uma pergunta na aba de Chat!")