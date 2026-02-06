from __future__ import annotations

from collections import Counter
from typing import Dict, List, Any

import ifcopenshell
import ifcopenshell.util.element as ifc_element


class IfcExtractionResult:
    def __init__(self, components: List[Dict[str, Any]], summary: str) -> None:
        self.components = components
        self.summary = summary


def extract_ifc_summary(file_path: str, max_components: int = 200) -> IfcExtractionResult:
    model = ifcopenshell.open(file_path)
    components: List[Dict[str, Any]] = []

    for element in model.by_type("IfcProduct"):
        global_id = getattr(element, "GlobalId", None)
        name = getattr(element, "Name", None)
        if not global_id:
            continue

        psets = ifc_element.get_psets(element)
        components.append(
            {
                "global_id": global_id,
                "name": name,
                "type": element.is_a(),
                "psets": psets,
            }
        )

    type_counts = Counter([c["type"] for c in components])

    summary_lines = ["IFC Component Type Counts:"]
    for type_name, count in type_counts.most_common(30):
        summary_lines.append(f"- {type_name}: {count}")

    summary_lines.append("\nSample Components:")
    for comp in components[:max_components]:
        pset_keys = list((comp.get("psets") or {}).keys())
        summary_lines.append(
            f"- {comp.get('type')} | {comp.get('name')} | {comp.get('global_id')} | Psets: {pset_keys}"
        )

    summary = "\n".join(summary_lines)
    return IfcExtractionResult(components=components, summary=summary)
