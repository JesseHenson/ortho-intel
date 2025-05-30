"""
Core Backend Components - Data models, business logic, and utilities
"""

# Core backend models and utilities
"""
Core data models and business logic for the medical device intelligence platform.
Includes both legacy clinical models and new progressive disclosure models.
"""

# Legacy clinical models
from .data_models import *

# Opportunity-focused models (legacy)
from .opportunity_data_models import (
    # Legacy models
    StrategicOpportunity,
    OpportunityMatrix,
    CategoryOpportunity,
    CompetitorProfile,
    ExecutiveSummary,
    OpportunityAnalysisResponse,
    
    # Progressive disclosure models
    OpportunitySummary,
    OpportunityDetail,
    OpportunityFull,
    
    # Transformation utilities
    OpportunityTransformer,
    OpportunityRanker,
    OpportunityDisclosureTransformer,
    BackwardCompatibilityTransformer,
    
    # Enhanced graph state
    enhance_graph_state_with_opportunities,
    enhance_graph_state_with_progressive_disclosure
)

# Source citation and metadata models
from .source_models import (
    # Core source models
    SourceCitation,
    SourceCollection,
    SourceAnalysisResult,
    AnalysisMetadata,
    
    # Progressive disclosure base
    ProgressiveDisclosureModel,
    DetailLevel,
    
    # Enums
    SourceType,
    CredibilityLevel,
    RelevanceLevel,
    
    # Utilities
    SourceCredibilityCalculator
) 