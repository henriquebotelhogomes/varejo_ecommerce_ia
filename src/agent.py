from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent


def configurar_agente_sql():
    """
    Configura e devolve o Agente SQL (LangGraph) ligado ao SQLite e ao modelo Groq,
    juntamente com o System Prompt.
    """
    # Ligar o LangChain ao banco de dados SQLite local
    db = SQLDatabase.from_uri("sqlite:///amazon_reviews.db")

    # Inicializar o LLM via Groq (Llama 3.3)
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,  # Mantemos a temperatura a 0 para precisão absoluta nas queries SQL
    )

    # Criar as ferramentas SQL que o Agente poderá usar
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()

    # Prompt Especializado em Varejo / CX
    system_prompt = """
    Você é um Analista de Dados Sénior especializado em Customer Experience (CX) e Varejo.
    A sua função é analisar a base de dados de avaliações de produtos da Amazon respondendo às perguntas do utilizador.

    A tabela chama-se 'avaliacoes' e contém reviews reais de produtos.

    REGRAS:
    1. Sempre verifique o esquema (schema) da tabela antes de criar a query para saber os nomes corretos das colunas.
    2. Nunca execute queries de UPDATE, DELETE ou DROP (Apenas SELECT).
    3. Para análises de texto (ex: "quais as piores avaliações"), use a coluna que contém o texto da review e limite a 3-5 resultados para não exceder o limite de tokens.
    4. Responda em Português (Portugal) de forma clara e profissional.
    """

    # Cria o orquestrador do Agente
    agent = create_react_agent(llm, tools)

    return agent, system_prompt
