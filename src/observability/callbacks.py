"""Gerenciamento de Callbacks de Observabilidade e Tracing (Langfuse & LangSmith)."""

from __future__ import annotations

import os

from langchain_core.callbacks import BaseCallbackHandler


def get_observability_callbacks() -> list[BaseCallbackHandler]:
    """Retorna a lista de callback handlers configurados para tracing distribuído.

    Ativa Langfuse se as chaves públicas/secretas estiverem no ambiente;
    Ativa LangSmith se LANGSMITH_API_KEY estiver presente.
    """
    callbacks: list[BaseCallbackHandler] = []

    # 1. Integração com Langfuse
    langfuse_pk = os.getenv("LANGFUSE_PUBLIC_KEY")
    langfuse_sk = os.getenv("LANGFUSE_SECRET_KEY")
    if langfuse_pk and langfuse_sk:
        try:
            from langfuse.callback import CallbackHandler as LangfuseCallbackHandler

            host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
            callbacks.append(
                LangfuseCallbackHandler(
                    public_key=langfuse_pk,
                    secret_key=langfuse_sk,
                    host=host,
                )
            )
        except ImportError:
            pass

    # 2. Integração com LangSmith
    langsmith_key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")
    if langsmith_key:
        try:
            from langchain_core.tracers import LangChainTracer

            project = os.getenv("LANGCHAIN_PROJECT", "retailsense-ai")
            callbacks.append(LangChainTracer(project_name=project))
        except ImportError:
            pass

    return callbacks
