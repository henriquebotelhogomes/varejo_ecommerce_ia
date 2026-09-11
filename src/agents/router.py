"""Nó Classificador de Intenções (IntentRouter).

Analisa a requisição do usuário e o histórico de mensagens para determinar se o
fluxo deve seguir a trilha quantitativa (SQL), qualitativa (RAG), híbrida ou chat informal.
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.state import AgentState, IntentClassificationOutput
from src.core.llm_provider import get_chat_model

SYSTEM_ROUTER_PROMPT = """Você é o Classificador de Intenção Semântica do RetailSense AI.
Sua função é rotear com precisão cirúrgica a pergunta do usuário para a trilha correta:

1. 'QUANTITATIVE_SQL': Se a pergunta pede números, métricas, agregações, médias, rankings, contagens ou filtros tabulares na base de dados de avaliações da Amazon.
   Exemplos: "Qual a nota média?", "Top 5 produtos com mais reviews", "Quantas notas 1 existem?".

2. 'QUALITATIVE_RAG': Se a pergunta busca opiniões, sentimentos, reclamações específicas, motivos de insatisfação ou tópicos mencionados em texto livre.
   Exemplos: "Do que os clientes reclamam sobre a bateria?", "O que falam da durabilidade?".

3. 'HYBRID': Se a pergunta requer explicitamente números E análise de texto livre combinados.
   Exemplos: "Qual a média de estrelas e o que dizem as piores reviews?".

4. 'CASUAL_CHAT': Saudações, despedidas ou dúvidas gerais sobre como usar o copiloto.
   Exemplos: "Olá", "Quem é você?", "Como posso usar esta ferramenta?".

Classifique estritamente seguindo o contrato estruturado."""


def intent_router_node(state: AgentState) -> dict[str, str]:
    """Nó do LangGraph que classifica a intenção da mensagem corrente."""
    user_query = (state.get("user_query") or "").strip()
    query_lower = user_query.lower()

    # Atalho FinOps: Saudações e apresentações simples não precisam gastar tokens de classificação
    greetings = [
        "olá",
        "ola",
        "oi",
        "oi!",
        "olá!",
        "bom dia",
        "boa tarde",
        "boa noite",
        "quem é você",
        "quem e voce",
        "hello",
        "hi",
    ]
    if any(query_lower.startswith(g) for g in greetings) and len(user_query.split()) <= 6:
        return {"intent": "CASUAL_CHAT"}

    # Fast-Path FinOps & Latência: Padrões analíticos quantitativos canônicos evitam 2 a 3 segundos de chamada LLM
    import re

    sql_patterns = [
        r"^(top|ranking)\s+\d+",
        r"^(quais|quais\s+são|liste)\s+(os|as)?\s*(\d+)?\s*(produtos|itens|avaliações|marcas)",
        r"^qual\s+(é\s+)?(a\s+)?(nota|média|media|avaliação|distribuição|total)",
        r"^quant(os|as)\s+(produtos|avaliações|reviews|clientes|votos|notas)",
        r"(distribuição|distribuicao)\s+(de\s+notas|por\s+estrela)",
        r"(mais\s+avaliad|piores\s+notas|melhores\s+notas|maior\s+volume|votos\s+úteis|votos\s+uteis)",
    ]
    for pattern in sql_patterns:
        if re.search(pattern, query_lower):
            return {"intent": "QUANTITATIVE_SQL"}

    messages = state.get("messages", [])

    llm = get_chat_model(tier="fast", temperature=0.0)

    # Prepara mensagens para contexto recente (últimas 3 mensagens)
    prompt_messages = [SystemMessage(content=SYSTEM_ROUTER_PROMPT)]
    for msg in messages[-3:]:
        prompt_messages.append(msg)
    prompt_messages.append(HumanMessage(content=user_query))

    try:
        structured_llm = llm.with_structured_output(IntentClassificationOutput)
        result: IntentClassificationOutput = structured_llm.invoke(prompt_messages)
        intent = result.intent
    except Exception:
        # Fallback resiliente via parsing ou invocação direta
        raw_res = llm.invoke(prompt_messages)
        content = raw_res.content if hasattr(raw_res, "content") else str(raw_res)

        if "QUANTITATIVE_SQL" in content:
            intent = "QUANTITATIVE_SQL"
        elif "QUALITATIVE_RAG" in content:
            intent = "QUALITATIVE_RAG"
        elif "HYBRID" in content:
            intent = "HYBRID"
        elif any(c in user_query.lower() for c in ["olá", "ola", "oi", "bom dia", "quem é"]):
            intent = "CASUAL_CHAT"
        else:
            intent = "QUANTITATIVE_SQL"

    return {"intent": intent}
