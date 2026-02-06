from __future__ import annotations

from typing import Optional, Any

import json
from jsonschema import validate as jsonschema_validate

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.schemas.extraction import EngineeringLogic
from app.services.llm_router import get_llm

SYSTEM_PROMPT = """
You are an expert knowledge extraction agent for construction and manufacturing.
Given layout-aware markdown or structured text, extract the decision logic and
return ONLY a JSON object matching the provided schema.

Rules:
- Use specific, concrete wording from the source.
- Prefer concise lists over paragraphs.
- Use relation types from the allowed enum.
- If a field is unknown, return an empty list or null, not a guess.
""".strip()


def build_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "Source content:\n\n{content}"),
        ]
    )


async def extract_engineering_logic(
    content: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> EngineeringLogic:
    llm = get_llm(provider=provider, model=model, temperature=0)
    prompt = build_prompt()

    resolved_provider = (provider or "").lower()
    if not resolved_provider:
        resolved_provider = "deepseek" if model and "deepseek" in model.lower() else "ollama"

    # DeepSeek API does not always support response_format JSON schema.
    # Use a parser-based prompt to ensure JSON output.
    if resolved_provider == "deepseek":
        parser = PydanticOutputParser(pydantic_object=EngineeringLogic)
        prompt_with_format = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("human", "Source content:\n\n{content}\n\n{format_instructions}"),
            ]
        )
        chain = prompt_with_format | llm | parser
        return await chain.ainvoke(
            {"content": content, "format_instructions": parser.get_format_instructions()}
        )

    chain = prompt | llm.with_structured_output(EngineeringLogic)
    result: EngineeringLogic = await chain.ainvoke({"content": content})
    return result


async def extract_with_agent(
    content: str,
    agent: dict,
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> dict:
    llm = get_llm(provider=provider, model=model, temperature=0)
    schema = agent.get("schema_json") or {}
    agent_prompt = agent.get("prompt") or ""
    output_language = _normalize_language(agent.get("output_language") or "zh")

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                "User agent prompt:\\n{agent_prompt}\\n\\n"
                "Output language (use Traditional Chinese if Chinese is requested): {output_language}\\n\\n"
                "JSON Schema:\\n{schema_json}\\n\\n"
                "Source content:\\n{content}\\n\\n"
                "Return ONLY JSON that matches the schema.",
            ),
        ]
    )

    result = await (prompt | llm).ainvoke(
        {
            "agent_prompt": agent_prompt,
            "output_language": output_language,
            "schema_json": json.dumps(schema, ensure_ascii=False),
            "content": content,
        }
    )
    text = result.content if hasattr(result, "content") else str(result)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            data = json.loads(text[start : end + 1])
        else:
            raise

    # validate if schema provided (sanitize nulls -> defaults or drop)
    if schema:
        data = _sanitize_instance(schema, data)
        jsonschema_validate(instance=data, schema=schema)
    return data


def _normalize_language(language: str) -> str:
    if not language:
        return "zh-Hant"
    lower = language.lower().replace("_", "-")
    if lower in ("zh", "zh-hant", "zh-tw", "zh-hk"):
        return "zh-Hant"
    return language


def _sanitize_instance(schema: dict, data: Any) -> Any:
    if not isinstance(schema, dict) or not isinstance(data, dict):
        return data

    required = set(schema.get("required") or [])
    properties = schema.get("properties") or {}
    for key, prop_schema in properties.items():
        if key not in data:
            continue
        value = data.get(key)
        if value is None:
            if key in required:
                data[key] = _default_for_schema(prop_schema)
            else:
                data.pop(key, None)
                continue
        # recurse for objects
        if isinstance(value, dict):
            data[key] = _sanitize_instance(prop_schema or {}, value)
        # handle array of objects
        if isinstance(value, list):
            item_schema = (prop_schema or {}).get("items") if isinstance(prop_schema, dict) else None
            if isinstance(item_schema, dict):
                data[key] = [
                    _sanitize_instance(item_schema, item) if isinstance(item, dict) else item
                    for item in value
                    if item is not None
                ]
    return data


def _default_for_schema(schema: dict) -> Any:
    if not isinstance(schema, dict):
        return ""
    if "default" in schema:
        return schema["default"]
    schema_type = schema.get("type")
    if isinstance(schema_type, list):
        schema_type = next((t for t in schema_type if t != "null"), None)
    if schema_type == "string":
        return ""
    if schema_type == "number":
        return 0
    if schema_type == "integer":
        return 0
    if schema_type == "boolean":
        return False
    if schema_type == "array":
        return []
    if schema_type == "object":
        return {}
    return ""
