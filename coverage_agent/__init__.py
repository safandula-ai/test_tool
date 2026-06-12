"""UI/API coverage discovery and gap analysis tools."""

from coverage_agent.decorators import CoverageMetadata, covers
from coverage_agent.gap_analysis import GapAnalysisEngine

__all__ = ["CoverageMetadata", "GapAnalysisEngine", "covers"]
