"""Nó de Síntese Executiva & Next Best Action (SynthesizerAgent).

Interpreta os resultados tabulares e semânticos, gerando insights de alto nível
para liderança de CX/Varejo com recomendações preditivas para continuidade analítica.
"""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.agents.state import AgentState, ExecutiveSummaryOutput
from src.core.llm_provider import get_chat_model

SYSTEM_SYNTHESIZER_PROMPT = """Você é o Chief Customer Experience Officer (CXO) & Analista Sênior de BI do RetailSense AI.
Sua missão é interpretar os dados brutos e entregar uma síntese executiva ágil, precisa e sem rodeios.

DIRETRIZES DE COMUNICAÇÃO:
1. Responda DIRETAMENTE à pergunta nos primeiros períodos, citando números-chave e porcentagens.
2. Forneça de 2 a 3 destaques objetivos (bullet points).
3. Forneça exatamente 3 perguntas analíticas curtas e investigativas para aprofundamento.
4. Seja conciso: priorize clareza executiva e velocidade."""


def synthesizer_node(state: AgentState) -> dict[str, Any]:
    """Nó do LangGraph que sintetiza os dados em resposta executiva rica."""
    user_query = state.get("user_query") or ""
    sql_result = state.get("sql_result")
    sql_query = state.get("sql_query")
    sql_err = state.get("sql_validation_error")
    intent = state.get("intent", "QUANTITATIVE_SQL")

    # 1. Tratamento para conversa informal / saudações
    if intent == "CASUAL_CHAT":
        chat_reply = (
            "Olá! Sou o **RetailSense AI**, seu copiloto analítico para o catálogo de e-commerce "
            "com mais de 204 mil avaliações de clientes.\n\n"
            "Você pode me fazer perguntas quantitativas ou qualitativas, por exemplo:\n"
            "- *'Qual é a média geral das notas e quantas avaliações 5 estrelas temos?'*\n"
            "- *'Quais são os 5 produtos com maior volume de avaliações?'*\n"
            "- *'Quais categorias ou produtos possuem as piores notas?'*"
        )
        return {
            "final_response": chat_reply,
            "next_best_actions": [
                "Qual é a nota média geral?",
                "Quais os 5 produtos mais avaliados?",
                "Distribuição de notas de 1 a 5 estrelas.",
            ],
            "messages": [AIMessage(content=chat_reply)],
        }

    # 2. Tratamento para erro irrecuperável após 3 tentativas
    if sql_err and not sql_result:
        error_reply = (
            f"Não foi possível concluir a consulta ao banco de dados com segurança após tentativas automáticas.\n\n"
            f"**Motivo:** `{sql_err}`\n\n"
            "Por favor, tente reformular a pergunta ou especificar os campos desejados."
        )
        return {
            "final_response": error_reply,
            "next_best_actions": [
                "Qual é a avaliação média dos produtos?",
                "Liste as primeiras 10 avaliações com nota 1.",
                "Quantos produtos únicos existem na base?",
            ],
            "messages": [AIMessage(content=error_reply)],
        }

    # 3. Síntese executiva com dados apurados
    llm = get_chat_model(tier="fast", temperature=0.2)
    sample_data = (
        str(sql_result[:10]) if sql_result else "Nenhum registro encontrado para estes filtros."
    )

    user_context = f"""Pergunta do usuário: '{user_query}'
Query SQL executada com sucesso:
```sql
{sql_query or "N/A"}
```
Resultados brutos retornados pelo banco (amostra de até 10 linhas):
{sample_data}
"""

    prompt_messages = [
        SystemMessage(content=SYSTEM_SYNTHESIZER_PROMPT),
        HumanMessage(content=user_context),
    ]

    try:
        structured_llm = llm.with_structured_output(ExecutiveSummaryOutput)
        output: ExecutiveSummaryOutput = structured_llm.invoke(prompt_messages)
        actions = [a.question for a in output.suggested_actions]
        bullets = "\n".join([f"- {f}" for f in output.key_findings])
        actions_formatted = "\n".join(
            [f"- 💡 **{a.question}** ({a.business_rationale})" for a in output.suggested_actions]
        )

        final_markdown = (
            f"{output.executive_summary}\n\n"
            f"### 📌 Principais Destaques:\n{bullets}\n\n"
            f"### 💡 Próximas Análises Sugeridas:\n{actions_formatted}"
        )
    except Exception:
        raw_res = llm.invoke(prompt_messages)
        content = raw_res.content if hasattr(raw_res, "content") else str(raw_res)
        final_markdown = content
        actions = [
            "Quais os produtos com maior volume nessa categoria?",
            "Qual a distribuição de notas entre 1 e 5 estrelas?",
            "Existe correlação com votos úteis (helpful_vote)?",
        ]

    return {
        "final_response": final_markdown,
        "next_best_actions": actions,
        "messages": [AIMessage(content=final_markdown)],
    }
