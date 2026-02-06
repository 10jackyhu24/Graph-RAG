from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.agent_service import generate_schema, build_agent_payload
from app.services.postgres_service import (
    get_connection,
    ensure_schema,
    insert_agent,
    list_agents,
    get_agent,
    deactivate_agent,
    delete_agent,
)

router = APIRouter()


class AgentCreateRequest(BaseModel):
    tenant_id: str
    name: str
    description: str | None = None
    prompt: str
    output_language: str = "zh"
    llm_provider: str | None = None
    llm_model: str | None = None
    base_agent_id: str | None = None
    visibility: str = "private"


@router.post("/agents")
async def create_agent(payload: AgentCreateRequest):
    conn = get_connection()
    schema = ensure_schema(conn, payload.tenant_id)

    base_version = 0
    if payload.base_agent_id:
        base_agent = get_agent(conn, schema, payload.base_agent_id)
        base_version = base_agent.get("version", 0) if base_agent else 0

    try:
        schema_json = await generate_schema(
            requirement=payload.prompt,
            language=payload.output_language,
            provider=payload.llm_provider,
            model=payload.llm_model,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    agent = build_agent_payload(
        name=payload.name,
        description=payload.description,
        prompt=payload.prompt,
        schema_json=schema_json,
        output_language=payload.output_language,
        version=base_version + 1 if base_version else 1,
        parent_id=payload.base_agent_id,
        visibility=payload.visibility,
    )

    insert_agent(conn, schema, agent)
    conn.close()

    return agent


@router.get("/agents")
def list_all_agents(tenant_id: str, include_inactive: bool = False):
    conn = get_connection()
    schema = ensure_schema(conn, tenant_id)
    agents = list_agents(conn, schema, include_inactive=include_inactive)
    conn.close()
    return agents


@router.get("/agents/{agent_id}")
def get_agent_detail(agent_id: str, tenant_id: str):
    conn = get_connection()
    schema = ensure_schema(conn, tenant_id)
    agent = get_agent(conn, schema, agent_id)
    conn.close()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.post("/agents/{agent_id}/deactivate")
def deactivate(agent_id: str, tenant_id: str):
    conn = get_connection()
    schema = ensure_schema(conn, tenant_id)
    deactivate_agent(conn, schema, agent_id)
    conn.close()
    return {"status": "ok"}


@router.delete("/agents/{agent_id}")
def delete(agent_id: str, tenant_id: str):
    conn = get_connection()
    schema = ensure_schema(conn, tenant_id)
    delete_agent(conn, schema, agent_id)
    conn.close()
    return {"status": "ok"}
