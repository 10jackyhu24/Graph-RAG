from __future__ import annotations

import re
import json
from typing import Any

from neo4j import GraphDatabase

from app.schemas.extraction import EngineeringLogic
from app.utils.settings import settings


def _sanitize_identifier(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", value.strip())
    cleaned = cleaned.strip("_")
    return cleaned or "default"


def _tenant_label(tenant_id: str) -> str:
    return f"Tenant_{_sanitize_identifier(tenant_id)}"


def get_driver():
    return GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )


def upsert_graph(tenant_id: str, extraction: EngineeringLogic, ifc_components: list | None = None) -> None:
    label = _tenant_label(tenant_id)
    driver = get_driver()

    doc = extraction.document_metadata

    with driver.session(database=settings.neo4j_database) as session:
        session.execute_write(
            _upsert_document,
            label,
            doc.document_id,
            doc.document_title,
            doc.document_type,
        )

        for entity in extraction.entities:
            session.execute_write(
                _upsert_entity,
                label,
                entity.name,
                entity.type,
                entity.description,
            )
            session.execute_write(
                _link_document_entity,
                label,
                doc.document_id,
                entity.name,
            )

        for component in extraction.affected_components:
            session.execute_write(
                _upsert_component,
                label,
                component,
            )
            session.execute_write(
                _link_document_component,
                label,
                doc.document_id,
                component,
            )

        for component in ifc_components or []:
            session.execute_write(
                _upsert_ifc_component,
                label,
                component,
            )
            session.execute_write(
                _link_document_ifc_component,
                label,
                doc.document_id,
                component.get("global_id"),
            )

        for relation in extraction.causal_relations:
            session.execute_write(
                _upsert_relation,
                label,
                relation.source,
                relation.target,
                relation.relation_type,
                relation.evidence,
            )

    driver.close()


def upsert_custom_document(tenant_id: str, extraction: dict) -> None:
    label = _tenant_label(tenant_id)
    driver = get_driver()
    document_id = extraction.get("document_id") or extraction.get("id") or "custom"
    title = extraction.get("document_title") or extraction.get("title") or "Custom Extraction"
    summary = extraction.get("summary") or ""
    raw_json = json.dumps(extraction, ensure_ascii=False)

    with driver.session(database=settings.neo4j_database) as session:
        session.execute_write(
            _upsert_custom_doc,
            label,
            document_id,
            title,
            summary,
            raw_json,
        )
    driver.close()


def delete_document(tenant_id: str, document_id: str) -> None:
    label = _tenant_label(tenant_id)
    driver = get_driver()
    with driver.session(database=settings.neo4j_database) as session:
        session.run(
            f"""
            MATCH (d:Document:{label} {{document_id: $document_id}})
            DETACH DELETE d
            """,
            document_id=document_id,
        )
    driver.close()


def _upsert_document(tx, label: str, document_id: str, title: str, doc_type: Any):
    query = f"""
    MERGE (d:Document:{label} {{document_id: $document_id}})
    SET d.title = $title,
        d.document_type = $doc_type,
        d.tenant_label = $label
    """
    tx.run(query, document_id=document_id, title=title, doc_type=doc_type, label=label)


def _upsert_entity(tx, label: str, name: str, entity_type: Any, description: Any):
    query = f"""
    MERGE (e:Entity:{label} {{name: $name}})
    SET e.type = $entity_type,
        e.description = $description,
        e.tenant_label = $label
    """
    tx.run(query, name=name, entity_type=entity_type, description=description, label=label)


def _link_document_entity(tx, label: str, document_id: str, name: str):
    query = f"""
    MATCH (d:Document:{label} {{document_id: $document_id}})
    MATCH (e:Entity:{label} {{name: $name}})
    MERGE (d)-[:MENTIONS]->(e)
    """
    tx.run(query, document_id=document_id, name=name)


def _upsert_component(tx, label: str, component_id: str):
    query = f"""
    MERGE (c:Component:{label} {{component_id: $component_id}})
    SET c.tenant_label = $label
    """
    tx.run(query, component_id=component_id, label=label)


def _link_document_component(tx, label: str, document_id: str, component_id: str):
    query = f"""
    MATCH (d:Document:{label} {{document_id: $document_id}})
    MATCH (c:Component:{label} {{component_id: $component_id}})
    MERGE (d)-[:IMPACTS]->(c)
    """
    tx.run(query, document_id=document_id, component_id=component_id)


def _upsert_ifc_component(tx, label: str, component: dict):
    query = f"""
    MERGE (c:IfcComponent:{label} {{global_id: $global_id}})
    SET c.name = $name,
        c.type = $type,
        c.psets = $psets,
        c.tenant_label = $label
    """
    tx.run(
        query,
        global_id=component.get("global_id"),
        name=component.get("name"),
        type=component.get("type"),
        psets=json.dumps(component.get("psets", {}), ensure_ascii=False),
        label=label,
    )


def _link_document_ifc_component(tx, label: str, document_id: str, global_id: str | None):
    if not global_id:
        return
    query = f"""
    MATCH (d:Document:{label} {{document_id: $document_id}})
    MATCH (c:IfcComponent:{label} {{global_id: $global_id}})
    MERGE (d)-[:HAS_IFC_COMPONENT]->(c)
    """
    tx.run(query, document_id=document_id, global_id=global_id)


def _upsert_relation(tx, label: str, source: str, target: str, relation_type: str, evidence: Any):
    query = f"""
    MERGE (s:Entity:{label} {{name: $source}})
    MERGE (t:Entity:{label} {{name: $target}})
    MERGE (s)-[r:RELATION {{type: $relation_type}}]->(t)
    SET r.evidence = $evidence
    """
    tx.run(query, source=source, target=target, relation_type=relation_type, evidence=evidence)


def _upsert_custom_doc(tx, label: str, document_id: str, title: str, summary: str, raw_json: str):
    query = f"""
    MERGE (d:Document:{label} {{document_id: $document_id}})
    SET d.title = $title,
        d.summary = $summary,
        d.raw_json = $raw_json,
        d.tenant_label = $label
    """
    tx.run(
        query,
        document_id=document_id,
        title=title,
        summary=summary,
        raw_json=raw_json,
        label=label,
    )
