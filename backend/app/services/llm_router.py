from __future__ import annotations

from typing import Optional

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from app.utils.settings import settings


def get_llm(provider: Optional[str] = None, model: Optional[str] = None, temperature: float = 0):
    resolved_provider = (provider or settings.resolved_llm_provider).lower()

    if resolved_provider == "ollama":
        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=model or settings.ollama_model,
            temperature=temperature,
        )

    if resolved_provider == "deepseek":
        if not settings.deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY is required for deepseek provider")
        return ChatOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            model=model or settings.deepseek_model,
            temperature=temperature,
        )

    raise ValueError(f"Unsupported LLM provider: {resolved_provider}")
