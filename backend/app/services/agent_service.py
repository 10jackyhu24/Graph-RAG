from __future__ import annotations

import json
import uuid
from typing import Any, Optional

from langchain_core.prompts import ChatPromptTemplate

from app.services.llm_router import get_llm


SCHEMA_SYSTEM = """
You are a data architect for construction/manufacturing documents.
Given a user requirement, design a concise JSON Schema (Draft 7) for structured extraction.
Rules:
- Output ONLY valid JSON (no code fences).
- Use type: object with properties.
- Keep fields minimal and practical.
- Use string/number/boolean/array/object types.
""".strip()


def build_schema_prompt(requirement: str, language: str) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", SCHEMA_SYSTEM),
            (
                "human",
                "Requirement (language={language}):\n{requirement}\n\nReturn JSON schema:",
            ),
        ]
    )


async def generate_schema(requirement: str, language: str, provider: Optional[str], model: Optional[str]) -> dict:
    llm = get_llm(provider=provider, model=model, temperature=0)
    prompt = build_schema_prompt(requirement, language)
    result = await (prompt | llm).ainvoke({"requirement": requirement, "language": language})
    content = result.content if hasattr(result, "content") else str(result)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Fallback: try to extract JSON substring
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1:
            return json.loads(content[start : end + 1])
        raise


def build_agent_payload(
    name: str,
    description: str,
    prompt: str,
    schema_json: dict,
    output_language: str,
    version: int = 1,
    parent_id: str | None = None,
    visibility: str = "private",
) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "description": description,
        "prompt": prompt,
        "schema_json": schema_json,
        "output_language": output_language,
        "version": version,
        "parent_id": parent_id,
        "is_active": True,
        "visibility": visibility,
    }
