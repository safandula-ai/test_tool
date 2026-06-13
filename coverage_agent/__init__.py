"""UI/API coverage discovery and gap analysis tools."""

from coverage_agent.decorators import CoverageMetadata, Presence, covers
from coverage_agent.gap_analysis import GapAnalysisEngine
from coverage_agent.template_engine import DynamicSuiteAssembler, TemplateRegistry

__all__ = [
    "CoverageMetadata",
    "DynamicSuiteAssembler",
    "GapAnalysisEngine",
    "Presence",
    "TemplateRegistry",
    "covers",
]
