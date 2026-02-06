from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    document_id: str = Field(..., description="Unique document id (e.g., ECN-001)")
    document_title: str = Field(..., description="Human readable title")
    document_type: Optional[str] = Field(None, description="Document type, e.g., ECN, spec, meeting")
    vendor: Optional[str] = None
    product_or_topic: Optional[str] = None
    version: Optional[str] = None
    source: Optional[str] = Field(None, description="Source file name or system")


class EngineeringEntity(BaseModel):
    name: str
    type: Optional[str] = None
    description: Optional[str] = None


class CausalRelation(BaseModel):
    relation_type: Literal[
        "AFFECTS",
        "FOLLOWS",
        "CONFLICTS_WITH",
        "CAUSES",
        "DEPENDS_ON",
        "IMPACTS",
    ]
    source: str
    target: str
    evidence: Optional[str] = None


class EngineeringLogic(BaseModel):
    document_metadata: DocumentMetadata
    summary: str = Field(..., description="High level summary")
    decision_background: List[str] = Field(default_factory=list)
    key_clauses: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    risk_level: Optional[Literal["low", "medium", "high"]] = None
    entities: List[EngineeringEntity] = Field(default_factory=list)
    causal_relations: List[CausalRelation] = Field(default_factory=list)
    affected_components: List[str] = Field(default_factory=list)
    source_reference: Optional[str] = None
