"""
PRD (Product Requirements Document) generation utilities.

Generates a lightweight PRD markdown from:
- Extracted requirements (Phase 3 output)
- Optional graph schema analysis (Phase 2 output)

This generator is intentionally simple and deterministic to make unit
testing reliable. It can be extended later with LLM-powered rewriting.
"""

from dataclasses import dataclass
from typing import Optional, List

from ..documents.models import ExtractedRequirements, Requirement, Priority
from ..schema.models import GraphSchema, SchemaAnalysis


@dataclass
class PRDSection:
    """Represents a PRD section with a title and body."""

    title: str
    body: str


class PRDGenerator:
    """
    Generates a markdown PRD from extracted requirements and optional schema analysis.

    Example:
        >>> generator = PRDGenerator()
        >>> md = generator.generate_prd(extracted_requirements, schema, analysis)
        >>> print(md)
    """

    def __init__(
        self,
        include_schema_summary: bool = True,
        include_risks: bool = True,
        include_constraints: bool = True,
    ):
        self.include_schema_summary = include_schema_summary
        self.include_risks = include_risks
        self.include_constraints = include_constraints

    def generate_prd(
        self,
        extracted: ExtractedRequirements,
        schema: Optional[GraphSchema] = None,
        schema_analysis: Optional[SchemaAnalysis] = None,
        product_name: str = "Graph Analytics AI Project",
    ) -> str:
        """Generate a PRD markdown string."""
        sections: List[PRDSection] = []

        sections.append(self._build_overview(product_name, extracted))
        sections.append(self._build_objectives(extracted))
        sections.append(self._build_requirements(extracted))
        sections.append(self._build_stakeholders(extracted))

        if self.include_constraints:
            sections.append(self._build_constraints(extracted))

        if self.include_risks:
            sections.append(self._build_risks(extracted))

        if self.include_schema_summary and schema:
            sections.append(self._build_schema(schema, schema_analysis))

        return self._render_markdown(sections)

    # ---- Builders ---------------------------------------------------------

    def _build_overview(
        self, product_name: str, extracted: ExtractedRequirements
    ) -> PRDSection:
        summary = extracted.summary or "No executive summary provided."
        domain = extracted.domain or "General"
        body = (
            f"**Product:** {product_name}\n"
            f"**Domain:** {domain}\n"
            f"**Documents analyzed:** {len(extracted.documents)}\n\n"
            f"{summary}"
        )
        return PRDSection("1. Overview", body)

    def _build_objectives(self, extracted: ExtractedRequirements) -> PRDSection:
        if not extracted.objectives:
            body = "_No objectives identified._"
            return PRDSection("2. Objectives", body)

        lines = []
        for obj in extracted.objectives:
            lines.append(f"- **{obj.id} – {obj.title}** ({obj.priority.value})")
            lines.append(f"  - {obj.description}")
            if obj.success_criteria:
                criteria = "; ".join(obj.success_criteria)
                lines.append(f"  - Success criteria: {criteria}")
            if obj.related_requirements:
                lines.append(
                    f"  - Related requirements: {', '.join(obj.related_requirements)}"
                )
        return PRDSection("2. Objectives", "\n".join(lines))

    def _build_requirements(self, extracted: ExtractedRequirements) -> PRDSection:
        if not extracted.requirements:
            return PRDSection("3. Requirements", "_No requirements identified._")

        # Sort by priority (Critical > High > Medium > Low > Unknown)
        def priority_order(req: Requirement) -> int:
            order = {
                Priority.CRITICAL: 0,
                Priority.HIGH: 1,
                Priority.MEDIUM: 2,
                Priority.LOW: 3,
                Priority.UNKNOWN: 4,
            }
            return order.get(req.priority, 4)

        sorted_reqs = sorted(extracted.requirements, key=priority_order)

        lines = []
        for req in sorted_reqs:
            lines.append(
                f"- **{req.id}** [{req.priority.value}] ({req.requirement_type.value})"
            )
            lines.append(f"  - {req.text}")
            if req.stakeholders:
                lines.append(f"  - Stakeholders: {', '.join(req.stakeholders)}")
            if req.dependencies:
                lines.append(f"  - Depends on: {', '.join(req.dependencies)}")
        return PRDSection("3. Requirements", "\n".join(lines))

    def _build_stakeholders(self, extracted: ExtractedRequirements) -> PRDSection:
        if not extracted.stakeholders:
            return PRDSection("4. Stakeholders", "_No stakeholders identified._")

        lines = []
        for sh in extracted.stakeholders:
            role = f" ({sh.role})" if sh.role else ""
            org = f" – {sh.organization}" if sh.organization else ""
            lines.append(f"- **{sh.name}**{role}{org}")
            if sh.interests:
                lines.append(f"  - Interests: {', '.join(sh.interests)}")
            if sh.requirements:
                lines.append(f"  - Requirements: {', '.join(sh.requirements)}")
        return PRDSection("4. Stakeholders", "\n".join(lines))

    def _build_constraints(self, extracted: ExtractedRequirements) -> PRDSection:
        if not extracted.constraints:
            return PRDSection("5. Constraints", "_No constraints identified._")
        lines = [f"- {c}" for c in extracted.constraints]
        return PRDSection("5. Constraints", "\n".join(lines))

    def _build_risks(self, extracted: ExtractedRequirements) -> PRDSection:
        if not extracted.risks:
            return PRDSection("6. Risks", "_No risks identified._")
        lines = [f"- {r}" for r in extracted.risks]
        return PRDSection("6. Risks", "\n".join(lines))

    def _build_schema(
        self, schema: GraphSchema, analysis: Optional[SchemaAnalysis]
    ) -> PRDSection:
        lines = []
        lines.append(
            f"- Vertex collections: {len(schema.vertex_collections)} "
            f"({', '.join(schema.vertex_collections.keys())})"
        )
        lines.append(
            f"- Edge collections: {len(schema.edge_collections)} "
            f"({', '.join(schema.edge_collections.keys())})"
        )
        lines.append(f"- Total documents: {schema.total_documents:,}")
        lines.append(f"- Total edges: {schema.total_edges:,}")

        if analysis:
            lines.append(f"- Domain: {analysis.domain or 'n/a'}")
            lines.append(f"- Complexity: {analysis.complexity_score:.1f}/10")
            if analysis.key_entities:
                lines.append(f"- Key entities: {', '.join(analysis.key_entities)}")
            if analysis.key_relationships:
                lines.append(
                    f"- Key relationships: {', '.join(analysis.key_relationships)}"
                )
            if analysis.suggested_analyses:
                sugg = ", ".join(
                    s.get("title", s.get("type", "analysis"))
                    for s in analysis.suggested_analyses
                )
                lines.append(f"- Suggested analyses: {sugg}")

        return PRDSection("7. Graph Schema (Summary)", "\n".join(lines))

    # ---- Rendering --------------------------------------------------------

    def _render_markdown(self, sections: List[PRDSection]) -> str:
        parts = ["# Product Requirements Document\n"]
        for section in sections:
            parts.append(f"## {section.title}\n")
            parts.append(f"{section.body}\n")
        return "\n".join(parts).strip() + "\n"


def generate_prd_markdown(
    extracted: ExtractedRequirements,
    schema: Optional[GraphSchema] = None,
    schema_analysis: Optional[SchemaAnalysis] = None,
    product_name: str = "Graph Analytics AI Project",
) -> str:
    """
    Convenience function to generate PRD markdown.
    """
    generator = PRDGenerator()
    return generator.generate_prd(
        extracted=extracted,
        schema=schema,
        schema_analysis=schema_analysis,
        product_name=product_name,
    )
