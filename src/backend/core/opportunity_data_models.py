# opportunity_data_models.py
"""
Opportunity-First Data Models for Competitive Intelligence
Integrates with existing clinical models while prioritizing actionable opportunities
Enhanced with progressive disclosure and source citation support
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, model_validator
from enum import Enum
from datetime import datetime

# Import source models for integration
from src.backend.core.source_models import (
    SourceCollection, AnalysisMetadata, ProgressiveDisclosureModel, 
    DetailLevel, SourceCitation, SourceAnalysisResult, SourceType
)

# Opportunity Classification Enums
class OpportunityCategory(str, Enum):
    """Categories of strategic opportunities"""
    PRODUCT_INNOVATION = "Product Innovation"
    BRAND_STRATEGY = "Brand Strategy" 
    MARKET_POSITIONING = "Market Positioning"
    PRICING_STRATEGY = "Pricing Strategy"
    MARKET_EXPANSION = "Market Expansion"
    OPERATIONAL_EFFICIENCY = "Operational Efficiency"

class ImplementationDifficulty(str, Enum):
    """Implementation difficulty levels"""
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"

class InvestmentLevel(str, Enum):
    """Investment requirement levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class CompetitiveRisk(str, Enum):
    """Competitive risk levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

# Core Opportunity Models
class StrategicOpportunity(BaseModel):
    """Model for top-level strategic opportunities"""
    id: int = Field(description="Unique opportunity identifier")
    title: str = Field(description="Clear, actionable opportunity title")
    category: OpportunityCategory = Field(description="Opportunity category")
    description: str = Field(description="Detailed opportunity description")
    
    # Scoring and prioritization
    opportunity_score: float = Field(description="Overall opportunity score (1-10)", ge=1, le=10)
    implementation_difficulty: ImplementationDifficulty = Field(description="Implementation difficulty")
    time_to_market: str = Field(description="Estimated time to market (e.g., '6-12 months')")
    investment_level: InvestmentLevel = Field(description="Required investment level")
    competitive_risk: CompetitiveRisk = Field(description="Risk of competitive response")
    
    # Business impact
    potential_impact: str = Field(description="Quantified business impact (revenue, market share, etc.)")
    next_steps: List[str] = Field(description="Immediate actionable next steps")
    supporting_evidence: str = Field(description="Evidence supporting the opportunity")
    
    # Metadata
    source_urls: List[str] = Field(default=[], description="Source URLs for evidence")
    confidence_level: float = Field(default=7.0, description="Confidence in opportunity (1-10)", ge=1, le=10)

# Progressive Disclosure Opportunity Models
class OpportunitySummary(ProgressiveDisclosureModel):
    """
    Summary-level opportunity information for list views and initial display.
    
    Provides essential information for quick scanning and decision-making
    without overwhelming detail.
    """
    
    # Essential display information
    title: str = Field(description="Clear, actionable opportunity title")
    category: OpportunityCategory = Field(description="Opportunity category")
    
    # Key metrics for quick assessment
    opportunity_score: float = Field(description="Overall opportunity score (1-10)", ge=1, le=10)
    implementation_difficulty: ImplementationDifficulty = Field(description="Implementation difficulty")
    time_to_market: str = Field(description="Estimated time to market")
    
    # UI display helpers (computed from source_collection)
    credibility_indicator: Optional[str] = Field(default="⚪", description="Visual credibility indicator")
    source_count_display: Optional[str] = Field(default="No sources", description="Source count display text")
    
    # Progressive disclosure flags
    has_detailed_analysis: bool = Field(default=True, description="Whether detailed analysis is available")
    has_source_analysis: bool = Field(default=True, description="Whether source analysis is available")
    
    @model_validator(mode='after')
    def set_display_fields(self):
        """Set display fields based on source collection"""
        if self.source_collection:
            # Set credibility indicator
            avg_cred = self.source_collection.average_credibility or 5.0
            if avg_cred >= 8:
                self.credibility_indicator = "🟢"  # High credibility
            elif avg_cred >= 6:
                self.credibility_indicator = "🟡"  # Medium credibility
            else:
                self.credibility_indicator = "🔴"  # Low credibility
            
            # Set source count display
            count = self.source_collection.total_sources or 0
            if count == 0:
                self.source_count_display = "No sources"
            elif count == 1:
                self.source_count_display = "1 source"
            else:
                self.source_count_display = f"{count} sources"
        else:
            self.credibility_indicator = "⚪"  # No data
            self.source_count_display = "No sources"
        
        return self

class OpportunityDetail(OpportunitySummary):
    """
    Detailed opportunity information for expanded views.
    
    Includes implementation details, business impact, and next steps
    while maintaining performance for interactive disclosure.
    """
    
    # Detailed description and context
    description: str = Field(description="Detailed opportunity description")
    
    # Business impact and investment
    investment_level: InvestmentLevel = Field(description="Required investment level")
    competitive_risk: CompetitiveRisk = Field(description="Risk of competitive response")
    potential_impact: str = Field(description="Quantified business impact")
    
    # Actionable information
    next_steps: List[str] = Field(description="Immediate actionable next steps")
    supporting_evidence: str = Field(description="Evidence supporting the opportunity")
    
    # Enhanced metadata
    confidence_level: float = Field(default=7.0, description="Confidence in opportunity (1-10)", ge=1, le=10)
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    # Risk and success factors
    risk_factors: List[str] = Field(default=[], description="Identified risk factors")
    success_metrics: List[str] = Field(default=[], description="Success measurement criteria")
    competitive_advantage: Optional[str] = Field(default=None, description="Competitive advantage gained")

class OpportunityFull(OpportunityDetail):
    """
    Complete opportunity information including full source analysis.
    
    Provides comprehensive details for deep analysis, due diligence,
    and detailed planning. Loaded on-demand for performance.
    """
    
    # Complete source information
    detailed_source_analysis: Optional[SourceAnalysisResult] = Field(
        default=None, 
        description="Detailed analysis of supporting sources"
    )
    
    # Extended analysis
    detailed_analysis: Optional[str] = Field(
        default=None, 
        description="Comprehensive analysis with methodology and assumptions"
    )
    
    # Market context
    market_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Detailed market context and competitive landscape"
    )
    
    # Implementation planning
    implementation_roadmap: List[Dict[str, Any]] = Field(
        default=[],
        description="Detailed implementation roadmap with milestones"
    )
    
    # Financial modeling
    financial_projections: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Financial projections and ROI analysis"
    )
    
    # Stakeholder analysis
    stakeholder_impact: List[Dict[str, Any]] = Field(
        default=[],
        description="Impact on different stakeholders"
    )

class OpportunityMatrix(BaseModel):
    """Model for opportunity impact vs difficulty matrix"""
    high_impact_easy: List[Dict[str, Union[str, float]]] = Field(description="High impact, easy implementation (Quick Wins)")
    high_impact_hard: List[Dict[str, Union[str, float]]] = Field(description="High impact, hard implementation (Strategic Investments)")
    low_impact_easy: List[Dict[str, Union[str, float]]] = Field(description="Low impact, easy implementation")
    low_impact_hard: List[Dict[str, Union[str, float]]] = Field(description="Low impact, hard implementation")

class CategoryOpportunity(ProgressiveDisclosureModel):
    """
    Model for category-specific opportunities (Brand, Product, Pricing, Market)
    Enhanced with progressive disclosure and source tracking capabilities.
    """
    
    # Core opportunity information
    opportunity: str = Field(description="Opportunity name")
    current_gap: str = Field(description="Current competitive gap identified")
    recommendation: str = Field(description="Specific recommendation")
    implementation: str = Field(description="Implementation approach")
    timeline: str = Field(description="Implementation timeline")
    investment: str = Field(description="Investment requirement with range")
    
    # Enhanced analysis fields
    competitive_advantage: Optional[str] = Field(default=None, description="Competitive advantage gained")
    risk_factors: List[str] = Field(default=[], description="Identified risk factors")
    success_metrics: List[str] = Field(default=[], description="Success measurement criteria")
    
    # Progressive disclosure enhancements
    priority_score: float = Field(default=5.0, description="Priority score (1-10)", ge=1, le=10)
    confidence_score: float = Field(default=7.0, description="Confidence score (1-10)", ge=1, le=10)
    
    # Source tracking
    supporting_sources: List[str] = Field(default=[], description="URLs of supporting sources")
    key_evidence: List[str] = Field(default=[], description="Key evidence points")
    
    # Metadata
    category_type: str = Field(description="Category type (Brand, Product, Pricing, Market)")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Set detail level based on available information
        if self.source_collection and len(self.source_collection.sources) > 0:
            self.detail_level = DetailLevel.FULL
        elif self.key_evidence:
            self.detail_level = DetailLevel.DETAIL
        else:
            self.detail_level = DetailLevel.SUMMARY

class CompetitorProfile(BaseModel):
    """Enhanced competitor profile for opportunity analysis"""
    name: str = Field(description="Competitor name")
    market_share: str = Field(description="Market share percentage or estimate")
    strengths: List[str] = Field(description="Key competitive strengths")
    weaknesses: List[str] = Field(description="Identified weaknesses")
    opportunities_against: List[str] = Field(description="Opportunities to compete against this competitor")
    
    # Market intelligence
    recent_moves: List[str] = Field(default=[], description="Recent strategic moves")
    innovation_gaps: List[str] = Field(default=[], description="Innovation gaps identified")
    pricing_strategy: Optional[str] = Field(default=None, description="Pricing strategy insights")

class ExecutiveSummary(BaseModel):
    """Executive summary for opportunity-first reports"""
    key_insight: str = Field(description="Primary strategic insight")
    top_3_opportunities: List[str] = Field(description="Top 3 opportunity titles")
    immediate_actions: List[str] = Field(description="Immediate actions to take")
    strategic_focus: str = Field(description="Recommended strategic focus area")
    competitive_advantage: str = Field(description="Key competitive advantage to pursue")
    
    # Business metrics
    revenue_potential: Optional[str] = Field(description="Total revenue potential estimate")
    market_share_opportunity: Optional[str] = Field(description="Market share opportunity")
    investment_required: Optional[str] = Field(description="Total investment required")

# Enhanced Response Model for Opportunity-First Analysis
class OpportunityAnalysisResponse(BaseModel):
    """
    Complete opportunity-first analysis response with progressive disclosure support.
    
    Provides tiered access to opportunity information, from summary views
    to detailed analysis with full source citations.
    """
    
    # Metadata
    analysis_metadata: AnalysisMetadata = Field(description="Analysis metadata (client, date, competitors, etc.)")
    
    # HERO: Top opportunities (primary focus) - Progressive Disclosure
    top_opportunities_summary: List[OpportunitySummary] = Field(
        description="Top 3-5 strategic opportunities (summary level)"
    )
    top_opportunities_detail: Optional[List[OpportunityDetail]] = Field(
        default=None,
        description="Top opportunities with detailed information (loaded on demand)"
    )
    top_opportunities_full: Optional[List[OpportunityFull]] = Field(
        default=None,
        description="Top opportunities with complete analysis (loaded on demand)"
    )
    
    # Opportunity matrix and prioritization
    opportunity_matrix: OpportunityMatrix = Field(description="Impact vs difficulty matrix")
    
    # Category-specific opportunities with progressive disclosure
    brand_opportunities: List[CategoryOpportunity] = Field(description="Brand strategy opportunities")
    product_opportunities: List[CategoryOpportunity] = Field(description="Product innovation opportunities")
    pricing_opportunities: List[CategoryOpportunity] = Field(description="Pricing strategy opportunities")
    market_opportunities: List[CategoryOpportunity] = Field(description="Market expansion opportunities")
    
    # Supporting competitive intelligence
    competitive_landscape: Dict[str, CompetitorProfile] = Field(description="Competitive landscape analysis")
    executive_summary: ExecutiveSummary = Field(description="Executive summary and recommendations")
    
    # Source analysis and credibility
    overall_source_analysis: Optional[SourceAnalysisResult] = Field(
        default=None,
        description="Overall source quality and credibility analysis"
    )
    
    # Legacy compatibility (maintain existing clinical analysis)
    clinical_gaps: List[Dict[str, Any]] = Field(default=[], description="Clinical gaps (legacy)")
    market_share_insights: List[Dict[str, Any]] = Field(default=[], description="Market share insights (legacy)")
    
    # Enhanced metadata
    research_timestamp: str = Field(description="Analysis timestamp")
    confidence_score: float = Field(default=7.5, description="Overall analysis confidence (1-10)")
    
    # Progressive disclosure control
    default_detail_level: DetailLevel = Field(
        default=DetailLevel.SUMMARY,
        description="Default detail level for initial display"
    )
    
    def get_opportunities_by_level(self, level: DetailLevel) -> List[Union[OpportunitySummary, OpportunityDetail, OpportunityFull]]:
        """
        Get top opportunities at specified detail level.
        
        Args:
            level: Desired detail level
            
        Returns:
            List of opportunities at the specified detail level
        """
        if level == DetailLevel.SUMMARY:
            return self.top_opportunities_summary
        elif level == DetailLevel.DETAIL and self.top_opportunities_detail:
            return self.top_opportunities_detail
        elif level == DetailLevel.FULL and self.top_opportunities_full:
            return self.top_opportunities_full
        else:
            # Fallback to summary if requested level not available
            return self.top_opportunities_summary
    
    def get_credibility_summary(self) -> Dict[str, Any]:
        """
        Get overall credibility summary for the analysis.
        
        Returns:
            Dictionary with credibility metrics and indicators
        """
        if not self.overall_source_analysis:
            return {
                "status": "No source analysis available",
                "indicator": "⚪",
                "score": 5.0
            }
        
        return {
            "overall_credibility": self.overall_source_analysis.overall_credibility.value,
            "source_quality_score": self.overall_source_analysis.source_quality_score,
            "consensus_level": self.overall_source_analysis.source_consensus,
            "has_primary_sources": self.overall_source_analysis.has_primary_sources,
            "has_recent_sources": self.overall_source_analysis.has_recent_sources
        }

# Data Transformation Utilities
class OpportunityTransformer:
    """Utilities for transforming between clinical-focused and opportunity-first data"""
    
    @staticmethod
    def clinical_gaps_to_opportunities(clinical_gaps: List[Dict[str, Any]]) -> List[StrategicOpportunity]:
        """Transform clinical gaps into strategic opportunities"""
        opportunities = []
        
        for i, gap in enumerate(clinical_gaps):
            # Transform clinical gap into opportunity
            opportunity = StrategicOpportunity(
                id=i + 1,
                title=f"Address {gap.get('gap_type', 'Clinical')} Gap",
                category=OpportunityCategory.PRODUCT_INNOVATION,
                description=f"Opportunity to address: {gap.get('description', 'Clinical limitation')}",
                opportunity_score=OpportunityTransformer._calculate_opportunity_score(gap),
                implementation_difficulty=OpportunityTransformer._map_difficulty(gap.get('severity', 'medium')),
                time_to_market="12-24 months",
                investment_level=InvestmentLevel.MEDIUM,
                competitive_risk=CompetitiveRisk.MEDIUM,
                potential_impact="Market differentiation opportunity",
                next_steps=[
                    "Conduct detailed market research",
                    "Develop technical solution",
                    "Validate with key customers"
                ],
                supporting_evidence=gap.get('evidence', 'Clinical research indicates opportunity'),
                source_urls=[gap.get('source_url')] if gap.get('source_url') else []
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    @staticmethod
    def market_insights_to_opportunities(market_insights: List[Dict[str, Any]]) -> List[StrategicOpportunity]:
        """Transform market insights into strategic opportunities"""
        opportunities = []
        
        for i, insight in enumerate(market_insights):
            opportunity = StrategicOpportunity(
                id=len(opportunities) + 1,
                title=f"Market Position Opportunity",
                category=OpportunityCategory.MARKET_POSITIONING,
                description=f"Leverage market position: {insight.get('market_position', 'Market opportunity')}",
                opportunity_score=8.0,  # Default high score for market opportunities
                implementation_difficulty=ImplementationDifficulty.MEDIUM,
                time_to_market="6-12 months",
                investment_level=InvestmentLevel.MEDIUM,
                competitive_risk=CompetitiveRisk.MEDIUM,
                potential_impact=insight.get('revenue_estimate', 'Significant market opportunity'),
                next_steps=[
                    "Develop market strategy",
                    "Identify key customers",
                    "Create go-to-market plan"
                ],
                supporting_evidence=insight.get('evidence', 'Market analysis indicates opportunity'),
                source_urls=[insight.get('source_url')] if insight.get('source_url') else []
            )
            opportunities.append(opportunity)
        
        return opportunities
    
    @staticmethod
    def _calculate_opportunity_score(gap: Dict[str, Any]) -> float:
        """Calculate opportunity score based on gap severity and evidence"""
        severity = gap.get('severity', 'medium').lower()
        severity_scores = {'high': 8.5, 'medium': 7.0, 'low': 5.5}
        return severity_scores.get(severity, 7.0)
    
    @staticmethod
    def _map_difficulty(severity: str) -> ImplementationDifficulty:
        """Map gap severity to implementation difficulty"""
        severity_lower = severity.lower()
        if severity_lower == 'high':
            return ImplementationDifficulty.HARD
        elif severity_lower == 'medium':
            return ImplementationDifficulty.MEDIUM
        else:
            return ImplementationDifficulty.EASY

# Opportunity Ranking and Prioritization
class OpportunityRanker:
    """Utilities for ranking and prioritizing opportunities"""
    
    @staticmethod
    def rank_opportunities(opportunities: List[StrategicOpportunity]) -> List[StrategicOpportunity]:
        """Rank opportunities by composite score"""
        def composite_score(opp: StrategicOpportunity) -> float:
            # Weight: 40% opportunity score, 30% implementation ease, 20% competitive risk, 10% confidence
            difficulty_scores = {'Easy': 10, 'Medium': 6, 'Hard': 3}
            risk_scores = {'Low': 10, 'Medium': 6, 'High': 3}
            
            score = (
                opp.opportunity_score * 0.4 +
                difficulty_scores.get(opp.implementation_difficulty.value, 6) * 0.3 +
                risk_scores.get(opp.competitive_risk.value, 6) * 0.2 +
                opp.confidence_level * 0.1
            )
            return score
        
        return sorted(opportunities, key=composite_score, reverse=True)
    
    @staticmethod
    def create_opportunity_matrix(opportunities: List[StrategicOpportunity]) -> OpportunityMatrix:
        """Create impact vs difficulty matrix from opportunities"""
        matrix_data = {
            "high_impact_easy": [],
            "high_impact_hard": [],
            "low_impact_easy": [],
            "low_impact_hard": []
        }
        
        for opp in opportunities:
            impact = opp.opportunity_score
            difficulty_map = {'Easy': 2, 'Medium': 5, 'Hard': 8}
            difficulty = difficulty_map.get(opp.implementation_difficulty.value, 5)
            
            item = {"name": opp.title, "impact": impact, "difficulty": difficulty}
            
            if impact >= 7.5 and difficulty <= 4:
                matrix_data["high_impact_easy"].append(item)
            elif impact >= 7.5 and difficulty > 4:
                matrix_data["high_impact_hard"].append(item)
            elif impact < 7.5 and difficulty <= 4:
                matrix_data["low_impact_easy"].append(item)
            else:
                matrix_data["low_impact_hard"].append(item)
        
        return OpportunityMatrix(**matrix_data)

# Integration with existing GraphState
def enhance_graph_state_with_opportunities(state: Dict[str, Any]) -> Dict[str, Any]:
    """Enhance existing GraphState with opportunity-first fields"""
    
    # Add opportunity-first fields to existing state
    enhanced_state = state.copy()
    enhanced_state.update({
        # Opportunity-first primary data
        "top_opportunities": [],
        "opportunity_matrix": None,
        "brand_opportunities": [],
        "product_opportunities": [],
        "pricing_opportunities": [],
        "market_expansion_opportunities": [],
        
        # Enhanced executive summary
        "executive_summary": None,
        "competitive_profiles": {},
        
        # Analysis metadata
        "opportunity_analysis_complete": False,
        "opportunity_confidence_score": 0.0
    })
    
    return enhanced_state 

# Progressive Disclosure Transformation Utilities
class OpportunityDisclosureTransformer:
    """
    Utilities for transforming opportunities between different disclosure levels.
    
    Handles conversion from legacy StrategicOpportunity models to progressive
    disclosure models and between different detail levels.
    """
    
    @staticmethod
    def strategic_to_summary(opportunity: StrategicOpportunity) -> OpportunitySummary:
        """Convert StrategicOpportunity to OpportunitySummary"""
        return OpportunitySummary(
            id=opportunity.id,
            title=opportunity.title,
            category=opportunity.category,
            opportunity_score=opportunity.opportunity_score,
            implementation_difficulty=opportunity.implementation_difficulty,
            time_to_market=opportunity.time_to_market,
            detail_level=DetailLevel.SUMMARY,
            # Create basic source collection from URLs
            source_collection=SourceCollection(
                sources=[
                    SourceCitation(
                        url=url,
                        title=f"Source {i+1}",
                        domain=url.split('/')[2] if '/' in url else url,
                        content_snippet=opportunity.supporting_evidence[:200] if opportunity.supporting_evidence else "",
                        source_type=SourceType.UNKNOWN,
                        credibility_score=opportunity.confidence_level,
                        relevance_score=8.0,
                        retrieved_at=datetime.now()
                    ) for i, url in enumerate(opportunity.source_urls)
                ] if opportunity.source_urls else []
            ) if opportunity.source_urls else None
        )
    
    @staticmethod
    def strategic_to_detail(opportunity: StrategicOpportunity) -> OpportunityDetail:
        """Convert StrategicOpportunity to OpportunityDetail"""
        summary = OpportunityDisclosureTransformer.strategic_to_summary(opportunity)
        
        # Get summary data and update with detail-specific fields
        summary_data = summary.model_dump()
        summary_data.update({
            'description': opportunity.description,
            'investment_level': opportunity.investment_level,
            'competitive_risk': opportunity.competitive_risk,
            'potential_impact': opportunity.potential_impact,
            'next_steps': opportunity.next_steps,
            'supporting_evidence': opportunity.supporting_evidence,
            'confidence_level': opportunity.confidence_level,
            'detail_level': DetailLevel.DETAIL
        })
        
        return OpportunityDetail(**summary_data)
    
    @staticmethod
    def strategic_to_full(
        opportunity: StrategicOpportunity, 
        detailed_analysis: Optional[str] = None,
        source_analysis: Optional[SourceAnalysisResult] = None
    ) -> OpportunityFull:
        """Convert StrategicOpportunity to OpportunityFull with optional enhancements"""
        detail = OpportunityDisclosureTransformer.strategic_to_detail(opportunity)
        
        # Get detail data and update with full-specific fields
        detail_data = detail.model_dump()
        detail_data.update({
            'detailed_analysis': detailed_analysis,
            'detailed_source_analysis': source_analysis,
            'detail_level': DetailLevel.FULL
        })
        
        return OpportunityFull(**detail_data)
    
    @staticmethod
    def enhance_with_sources(
        opportunity: Union[OpportunitySummary, OpportunityDetail, OpportunityFull],
        sources: List[SourceCitation]
    ) -> Union[OpportunitySummary, OpportunityDetail, OpportunityFull]:
        """Enhance opportunity with source collection"""
        if sources:
            source_collection = SourceCollection(sources=sources)
            opportunity.source_collection = source_collection
            opportunity.has_source_analysis = True
        
        return opportunity
    
    @staticmethod
    def create_analysis_metadata(
        client_name: str,
        competitors: List[str],
        analysis_type: str = "competitive_intelligence"
    ) -> AnalysisMetadata:
        """Create analysis metadata for opportunity analysis"""
        return AnalysisMetadata(
            analysis_id=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            analysis_type=analysis_type,
            pipeline_version="1.0.0",
            primary_model="gpt-4",  # Default, should be configurable
            started_at=datetime.now(),
            confidence_score=7.5,
            completeness_score=8.0,
            source_coverage=7.0,
            client_name=client_name
        )

# Enhanced Graph State Integration
def enhance_graph_state_with_progressive_disclosure(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance existing GraphState with progressive disclosure fields.
    
    Maintains backward compatibility while adding new progressive disclosure
    capabilities for opportunities and source tracking.
    """
    
    # Add progressive disclosure fields to existing state
    enhanced_state = state.copy()
    enhanced_state.update({
        # Progressive disclosure opportunity data
        "top_opportunities_summary": [],
        "top_opportunities_detail": None,
        "top_opportunities_full": None,
        
        # Enhanced opportunity matrix and categories
        "opportunity_matrix": None,
        "brand_opportunities": [],
        "product_opportunities": [],
        "pricing_opportunities": [],
        "market_expansion_opportunities": [],
        
        # Source analysis and credibility
        "overall_source_analysis": None,
        "source_collections": {},
        
        # Enhanced executive summary and metadata
        "executive_summary": None,
        "competitive_profiles": {},
        "analysis_metadata": None,
        
        # Progressive disclosure control
        "default_detail_level": DetailLevel.SUMMARY,
        "available_detail_levels": [DetailLevel.SUMMARY, DetailLevel.DETAIL, DetailLevel.FULL],
        
        # Analysis status and quality
        "opportunity_analysis_complete": False,
        "opportunity_confidence_score": 0.0,
        "source_analysis_complete": False,
        "credibility_analysis_complete": False
    })
    
    return enhanced_state

# Backward Compatibility Utilities
class BackwardCompatibilityTransformer:
    """
    Utilities for maintaining backward compatibility with existing systems.
    
    Converts between legacy models and new progressive disclosure models
    to ensure existing integrations continue to work.
    """
    
    @staticmethod
    def progressive_to_legacy_response(
        progressive_response: OpportunityAnalysisResponse
    ) -> Dict[str, Any]:
        """Convert progressive disclosure response to legacy format"""
        
        # Convert summary opportunities back to StrategicOpportunity format
        legacy_opportunities = []
        for summary in progressive_response.top_opportunities_summary:
            legacy_opp = StrategicOpportunity(
                id=summary.id,
                title=summary.title,
                category=summary.category,
                description="",  # Will be populated from detail level if available
                opportunity_score=summary.opportunity_score,
                implementation_difficulty=summary.implementation_difficulty,
                time_to_market=summary.time_to_market,
                investment_level=InvestmentLevel.MEDIUM,  # Default
                competitive_risk=CompetitiveRisk.MEDIUM,  # Default
                potential_impact="",  # Will be populated from detail level
                next_steps=[],  # Will be populated from detail level
                supporting_evidence="",  # Will be populated from sources
                source_urls=[s.url for s in summary.source_collection.sources] if summary.source_collection else [],
                confidence_level=summary.source_collection.average_credibility if summary.source_collection else 7.0
            )
            legacy_opportunities.append(legacy_opp)
        
        # Create legacy response structure
        legacy_response = {
            "analysis_metadata": progressive_response.analysis_metadata.model_dump() if progressive_response.analysis_metadata else {},
            "top_opportunities": [opp.model_dump() for opp in legacy_opportunities],
            "opportunity_matrix": progressive_response.opportunity_matrix.model_dump() if progressive_response.opportunity_matrix else {},
            "brand_opportunities": [opp.model_dump() for opp in progressive_response.brand_opportunities],
            "product_opportunities": [opp.model_dump() for opp in progressive_response.product_opportunities],
            "pricing_opportunities": [opp.model_dump() for opp in progressive_response.pricing_opportunities],
            "market_opportunities": [opp.model_dump() for opp in progressive_response.market_opportunities],
            "competitive_landscape": progressive_response.competitive_landscape,
            "executive_summary": progressive_response.executive_summary.model_dump() if progressive_response.executive_summary else {},
            "clinical_gaps": progressive_response.clinical_gaps,
            "market_share_insights": progressive_response.market_share_insights,
            "research_timestamp": progressive_response.research_timestamp,
            "confidence_score": progressive_response.confidence_score
        }
        
        return legacy_response
    
    @staticmethod
    def legacy_to_progressive_response(
        legacy_response: Dict[str, Any]
    ) -> OpportunityAnalysisResponse:
        """Convert legacy response to progressive disclosure format"""
        
        # Convert legacy opportunities to progressive format
        summary_opportunities = []
        if "top_opportunities" in legacy_response:
            for opp_data in legacy_response["top_opportunities"]:
                if isinstance(opp_data, dict):
                    # Create StrategicOpportunity from dict first
                    strategic_opp = StrategicOpportunity(**opp_data)
                    # Convert to summary
                    summary = OpportunityDisclosureTransformer.strategic_to_summary(strategic_opp)
                    summary_opportunities.append(summary)
        
        # Create analysis metadata
        metadata = None
        if "analysis_metadata" in legacy_response and legacy_response["analysis_metadata"]:
            metadata_dict = legacy_response["analysis_metadata"]
            if isinstance(metadata_dict, dict):
                # Ensure required fields are present
                metadata_dict.setdefault("analysis_id", f"legacy_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                metadata_dict.setdefault("analysis_type", "competitive_intelligence")
                metadata_dict.setdefault("pipeline_version", "legacy")
                metadata_dict.setdefault("primary_model", "unknown")
                metadata_dict.setdefault("started_at", datetime.now())
                metadata_dict.setdefault("confidence_score", 7.0)
                metadata_dict.setdefault("completeness_score", 7.0)
                metadata_dict.setdefault("source_coverage", 6.0)
                
                metadata = AnalysisMetadata(**metadata_dict)
        
        # Create progressive response
        progressive_response = OpportunityAnalysisResponse(
            analysis_metadata=metadata or OpportunityDisclosureTransformer.create_analysis_metadata(
                client_name="Legacy Client",
                competitors=[],
                analysis_type="legacy_conversion"
            ),
            top_opportunities_summary=summary_opportunities,
            opportunity_matrix=OpportunityMatrix(**legacy_response.get("opportunity_matrix", {})) if legacy_response.get("opportunity_matrix") else OpportunityMatrix(
                high_impact_easy=[],
                high_impact_hard=[],
                low_impact_easy=[],
                low_impact_hard=[]
            ),
            brand_opportunities=[CategoryOpportunity(**opp, category_type="Brand") for opp in legacy_response.get("brand_opportunities", [])],
            product_opportunities=[CategoryOpportunity(**opp, category_type="Product") for opp in legacy_response.get("product_opportunities", [])],
            pricing_opportunities=[CategoryOpportunity(**opp, category_type="Pricing") for opp in legacy_response.get("pricing_opportunities", [])],
            market_opportunities=[CategoryOpportunity(**opp, category_type="Market") for opp in legacy_response.get("market_opportunities", [])],
            competitive_landscape=legacy_response.get("competitive_landscape", {}),
            executive_summary=ExecutiveSummary(**legacy_response["executive_summary"]) if legacy_response.get("executive_summary") else ExecutiveSummary(
                key_insight="Legacy analysis",
                top_3_opportunities=[],
                immediate_actions=[],
                strategic_focus="",
                competitive_advantage=""
            ),
            clinical_gaps=legacy_response.get("clinical_gaps", []),
            market_share_insights=legacy_response.get("market_share_insights", []),
            research_timestamp=legacy_response.get("research_timestamp", datetime.now().isoformat()),
            confidence_score=legacy_response.get("confidence_score", 7.0)
        )
        
        return progressive_response 