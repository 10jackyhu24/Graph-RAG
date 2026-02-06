from __future__ import annotations

import re
from typing import Dict, Any
import json

import psycopg
from psycopg import sql

from app.utils.settings import settings


def _sanitize_identifier(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", value.strip())
    cleaned = cleaned.strip("_")
    return cleaned or "default"


def _schema_name(tenant_id: str) -> str:
    return f"tenant_{_sanitize_identifier(tenant_id)}"


def get_connection():
    return psycopg.connect(settings.postgres_dsn, autocommit=True)


def ensure_schema(conn, tenant_id: str) -> str:
    schema = _schema_name(tenant_id)
    with conn.cursor() as cur:
        cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}")
                    .format(sql.Identifier(schema)))
        cur.execute(
            sql.SQL(
                """
                CREATE TABLE IF NOT EXISTS {}.documents (
                    id SERIAL PRIMARY KEY,
                    document_id TEXT,
                    document_title TEXT,
                    document_type TEXT,
                    summary TEXT,
                    risk_level TEXT,
                    source TEXT,
                    source_path TEXT,
                    raw_json JSONB,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            ).format(sql.Identifier(schema))
        )
        cur.execute(
            sql.SQL("ALTER TABLE {}.documents ADD COLUMN IF NOT EXISTS source_path TEXT")
            .format(sql.Identifier(schema))
        )
        cur.execute(
            sql.SQL(
                """
                CREATE TABLE IF NOT EXISTS {}.agents (
                    id UUID PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    prompt TEXT NOT NULL,
                    schema_json JSONB NOT NULL,
                    output_language TEXT DEFAULT 'zh',
                    version INT DEFAULT 1,
                    parent_id UUID,
                    is_active BOOLEAN DEFAULT TRUE,
                    visibility TEXT DEFAULT 'private',
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            ).format(sql.Identifier(schema))
        )
        cur.execute(
            sql.SQL("ALTER TABLE {}.agents ADD COLUMN IF NOT EXISTS version INT DEFAULT 1")
            .format(sql.Identifier(schema))
        )
        cur.execute(
            sql.SQL("ALTER TABLE {}.agents ADD COLUMN IF NOT EXISTS parent_id UUID")
            .format(sql.Identifier(schema))
        )
        cur.execute(
            sql.SQL("ALTER TABLE {}.agents ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE")
            .format(sql.Identifier(schema))
        )
        cur.execute(
            sql.SQL("ALTER TABLE {}.agents ADD COLUMN IF NOT EXISTS visibility TEXT DEFAULT 'private'")
            .format(sql.Identifier(schema))
        )
    return schema


def insert_document(conn, schema: str, payload: Dict[str, Any]) -> None:
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL(
                """
                INSERT INTO {}.documents
                (document_id, document_title, document_type, summary, risk_level, source, source_path, raw_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
            ).format(sql.Identifier(schema)),
            (
                payload.get("document_id"),
                payload.get("document_title"),
                payload.get("document_type"),
                payload.get("summary"),
                payload.get("risk_level"),
                payload.get("source"),
                payload.get("source_path"),
                json.dumps(payload.get("raw_json")),
            ),
        )


def insert_agent(conn, schema: str, payload: Dict[str, Any]) -> None:
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL(
                """
                INSERT INTO {}.agents
                (id, name, description, prompt, schema_json, output_language, version, parent_id, is_active, visibility)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
            ).format(sql.Identifier(schema)),
            (
                payload.get("id"),
                payload.get("name"),
                payload.get("description"),
                payload.get("prompt"),
                json.dumps(payload.get("schema_json")),
                payload.get("output_language"),
                payload.get("version", 1),
                payload.get("parent_id"),
                payload.get("is_active", True),
                payload.get("visibility", "private"),
            ),
        )


def list_agents(conn, schema: str, include_inactive: bool = False) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL(
                """
                SELECT id, name, description, prompt, schema_json, output_language, version, parent_id, is_active, visibility, created_at
                FROM {}.agents
                {}
                ORDER BY created_at DESC
                """
            ).format(
                sql.Identifier(schema),
                sql.SQL("") if include_inactive else sql.SQL("WHERE is_active = TRUE"),
            )
        )
        rows = cur.fetchall()
    return [
        {
            "id": str(r[0]),
            "name": r[1],
            "description": r[2],
            "prompt": r[3],
            "schema_json": r[4],
            "output_language": r[5],
            "version": r[6],
            "parent_id": str(r[7]) if r[7] else None,
            "is_active": r[8],
            "visibility": r[9],
            "created_at": r[10].isoformat() if r[10] else None,
        }
        for r in rows
    ]


def get_agent(conn, schema: str, agent_id: str) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL(
                """
                SELECT id, name, description, prompt, schema_json, output_language, version, parent_id, is_active, visibility, created_at
                FROM {}.agents
                WHERE id = %s
                """
            ).format(sql.Identifier(schema)),
            (agent_id,),
        )
        row = cur.fetchone()
    if not row:
        return None
    return {
        "id": str(row[0]),
        "name": row[1],
        "description": row[2],
        "prompt": row[3],
        "schema_json": row[4],
        "output_language": row[5],
        "version": row[6],
        "parent_id": str(row[7]) if row[7] else None,
        "is_active": row[8],
        "visibility": row[9],
        "created_at": row[10].isoformat() if row[10] else None,
    }


def deactivate_agent(conn, schema: str, agent_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("UPDATE {}.agents SET is_active = FALSE WHERE id = %s")
            .format(sql.Identifier(schema)),
            (agent_id,),
        )


def delete_agent(conn, schema: str, agent_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("DELETE FROM {}.agents WHERE id = %s")
            .format(sql.Identifier(schema)),
            (agent_id,),
        )


def list_documents(conn, schema: str, limit: int = 20) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL(
                """
                SELECT id, document_id, document_title, document_type, summary, risk_level, source, source_path, created_at
                FROM {}.documents
                ORDER BY created_at DESC
                LIMIT %s
                """
            ).format(sql.Identifier(schema)),
            (limit,),
        )
        rows = cur.fetchall()
    return [
        {
            "row_id": r[0],
            "document_id": r[1],
            "document_title": r[2],
            "document_type": r[3],
            "summary": r[4],
            "risk_level": r[5],
            "source": r[6],
            "source_path": r[7],
            "created_at": r[8].isoformat() if r[8] else None,
        }
        for r in rows
    ]


def get_document(conn, schema: str, document_id: str) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL(
                """
                SELECT id, document_id, document_title, document_type, summary, risk_level, source, source_path, raw_json
                FROM {}.documents
                WHERE document_id = %s
                """
            ).format(sql.Identifier(schema)),
            (document_id,),
        )
        row = cur.fetchone()
    if not row:
        return None
    return {
        "row_id": row[0],
        "document_id": row[1],
        "document_title": row[2],
        "document_type": row[3],
        "summary": row[4],
        "risk_level": row[5],
        "source": row[6],
        "source_path": row[7],
        "raw_json": row[8],
    }


def get_document_by_row_id(conn, schema: str, row_id: int) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL(
                """
                SELECT id, document_id, document_title, document_type, summary, risk_level, source, source_path, raw_json
                FROM {}.documents
                WHERE id = %s
                """
            ).format(sql.Identifier(schema)),
            (row_id,),
        )
        row = cur.fetchone()
    if not row:
        return None
    return {
        "row_id": row[0],
        "document_id": row[1],
        "document_title": row[2],
        "document_type": row[3],
        "summary": row[4],
        "risk_level": row[5],
        "source": row[6],
        "source_path": row[7],
        "raw_json": row[8],
    }


def delete_document(conn, schema: str, document_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("DELETE FROM {}.documents WHERE document_id = %s")
            .format(sql.Identifier(schema)),
            (document_id,),
        )


def delete_document_by_row_id(conn, schema: str, row_id: int) -> None:
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("DELETE FROM {}.documents WHERE id = %s")
            .format(sql.Identifier(schema)),
            (row_id,),
        )
