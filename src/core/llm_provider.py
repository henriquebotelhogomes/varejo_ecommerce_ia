"""Factory Agnóstica de Modelos de Linguagem (LLM Provider).

Gerencia a inicialização e o roteamento inteligente de modelos entre Google Gemini,
OpenCode Go (DeepSeek V4.1 Flash/Pro) e Groq, otimizando latência e custo (FinOps).
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel

load_dotenv()


def get_active_model_info(tier: str = "fast") -> dict[str, str]:
    """Retorna metadados do provedor e modelo atualmente roteados para o tier."""
    provider = os.getenv("LLM_PROVIDER", "auto").lower()
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    opencode_key = os.getenv("OPENCODE_API_KEY") or os.getenv("OPENCODE_GO_API_KEY")

    if (provider in ("gemini", "google") or provider == "auto") and gemini_key:
        model = os.getenv(
            "GEMINI_FAST_MODEL" if tier == "fast" else "GEMINI_REASONING_MODEL",
            "gemini-2.5-flash" if tier == "fast" else "gemini-2.5-pro",
        )
        return {"provider": "Google Gemini", "model": model, "tier": tier}

    if (provider in ("opencode", "deepseek", "qwen") or provider == "auto") and opencode_key:
        model = os.getenv(
            "OPENCODE_FAST_MODEL" if tier == "fast" else "OPENCODE_REASONING_MODEL",
            "deepseek-v4.1-flash" if tier == "fast" else "deepseek-v4-pro",
        )
        return {"provider": "OpenCode Go", "model": model, "tier": tier}

    return {"provider": "Mock/Fallback", "model": "fake-model", "tier": tier}


def get_chat_model(tier: str = "fast", temperature: float = 0.0) -> BaseChatModel:
    """Retorna uma instância configurada do LLM com base no tier e credenciais ativas.

    Args:
        tier: 'fast' para alta velocidade e baixo custo (Gemini Flash, DeepSeek V4.1 Flash);
              'reasoning' para queries complexas (DeepSeek V4 Pro, Qwen3.8 Max, Kimi K3).
        temperature: Temperatura do modelo (0.0 padrão para determinismo).

    Returns:
        Instância de BaseChatModel pronta para invocação ou structured outputs.
    """
    provider = os.getenv("LLM_PROVIDER", "auto").lower()
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    opencode_key = os.getenv("OPENCODE_API_KEY") or os.getenv("OPENCODE_GO_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    # 1. Rota Google Gemini (Padrão quando ativo ou explícito)
    if (provider in ("gemini", "google") or provider == "auto") and gemini_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            model_name = os.getenv(
                "GEMINI_FAST_MODEL" if tier == "fast" else "GEMINI_REASONING_MODEL",
                "gemini-2.5-flash" if tier == "fast" else "gemini-2.5-pro",
            )
            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=gemini_key,
                temperature=temperature,
            )
        except ImportError:
            pass

    # 2. Rota OpenCode Go (DeepSeek V4.1 Flash / DeepSeek V4 Pro / Qwen3.8 Max)
    if (provider in ("opencode", "deepseek", "qwen") or provider == "auto") and opencode_key:
        try:
            from langchain_openai import ChatOpenAI

            base_url = (
                os.getenv("OPENCODE_BASE_URL")
                or os.getenv("OPENCODE_GO_BASE_URL")
                or os.getenv("OPENCODE_API_BASE", "https://api.opencode.ai/v1")
            )
            model_name = os.getenv(
                "OPENCODE_FAST_MODEL" if tier == "fast" else "OPENCODE_REASONING_MODEL",
                "deepseek-v4.1-flash" if tier == "fast" else "deepseek-v4-pro",
            )
            return ChatOpenAI(
                model=model_name,
                api_key=opencode_key,
                base_url=base_url,
                temperature=temperature,
            )
        except ImportError:
            pass

    # 3. Rota OpenRouter (Modelos Gratuitos e Fronteira)
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if (provider == "openrouter" or provider == "auto") and openrouter_key:
        try:
            from langchain_openai import ChatOpenAI

            default_free_model = os.getenv(
                "OPENROUTER_MODEL",
                "nvidia/nemotron-3-ultra-550b-a55b:free"
                if tier == "reasoning"
                else "openrouter/free",
            )
            return ChatOpenAI(
                model=default_free_model,
                api_key=openrouter_key,
                base_url="https://openrouter.ai/api/v1",
                temperature=temperature,
            )
        except ImportError:
            pass

    # 4. Rota Groq (Llama 3.3)
    if (provider == "groq" or provider == "auto") and groq_key:
        try:
            from langchain_groq import ChatGroq

            return ChatGroq(
                model="llama-3.3-70b-versatile",
                groq_api_key=groq_key,
                temperature=temperature,
            )
        except ImportError:
            pass

    # 5. Fallback para testes sem chave / Mock Provider
    from langchain_core.language_models import FakeListChatModel

    fake_responses = [
        '{"intent": "QUANTITATIVE_SQL", "confidence": 0.95, "reasoning": "Dúvida sobre métricas de avaliação", "extracted_entities": []}',
        '{"sql_query": "SELECT AVG(rating) as media FROM avaliacoes", "tables_used": ["avaliacoes"], "is_aggregation": true, "explanation": "Média de notas"}',
        '{"executive_summary": "A média geral apurada foi de 4.2 estrelas.", "key_findings": ["Alta satisfação global"], "suggested_actions": [{"question": "Quais as 5 piores?", "business_rationale": "Investigar churn"}, {"question": "Quais os produtos mais avaliados?", "business_rationale": "Volume"}, {"question": "Média por ano?", "business_rationale": "Tendência"}]}',
    ]
    return FakeListChatModel(responses=fake_responses)


def get_evals_judge_model() -> BaseChatModel:
    """Retorna modelo independente para atuar como Juiz (LLM-as-a-Judge) nas avaliações Ragas.

    Prioriza OpenRouter com modelo de 550B parâmetros (NVIDIA Nemotron 3 Ultra) para
    evitar viés de auto-aprovação contra as respostas geradas pelo Gemini ou DeepSeek.
    """
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_key:
        try:
            from langchain_openai import ChatOpenAI

            judge_model = os.getenv("EVALS_JUDGE_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free")
            return ChatOpenAI(
                model=judge_model,
                api_key=openrouter_key,
                base_url="https://openrouter.ai/api/v1",
                temperature=0.0,
            )
        except Exception:
            pass

    # Fallback para o tier de raciocínio principal
    return get_chat_model(tier="reasoning", temperature=0.0)
