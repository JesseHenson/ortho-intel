# opportunity_data_models.py
"""
Opportunity-First Data Models for Competitive Intelligence
Integrates with existing clinical models while prioritizing actionable opportunities
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum

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

class OpportunityMatrix(BaseModel):
    """Model for opportunity impact vs difficulty matrix"""
    high_impact_easy: List[Dict[str, Union[str, float]]] = Field(description="High impact, easy implementation (Quick Wins)")
    high_impact_hard: List[Dict[str, Union[str, float]]] = Field(description="High impact, hard implementation (Strategic Investments)")
    low_impact_easy: List[Dict[str, Union[str, float]]] = Field(description="Low impact, easy implementation")
    low_impact_hard: List[Dict[str, Union[str, float]]] = Field(description="Low impact, hard implementation")

class CategoryOpportunity(BaseModel):
    """Model for category-specific opportunities (Brand, Product, Pricing, Market)"""
    opportunity: str = Field(description="Opportunity name")
    current_gap: str = Field(description="Current competitive gap identified")
    recommendation: str = Field(description="Specific recommendation")
    implementation: str = Field(description="Implementation approach")
    timeline: str = Field(description="Implementation timeline")
    investment: str = Field(description="Investment requirement with range")
    
    # Additional fields for enhanced analysis
    competitive_advantage: Optional[str] = Field(default=None, description="Competitive advantage gained")
    risk_factors: List[str] = Field(default=[], description="Implementation risks")
    success_metrics: List[str] = Field(default=[], description="Success measurement criteria")

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
    """Complete opportunity-first analysis response"""
    
    # Metadata
    analysis_metadata: Dict[str, Any] = Field(description="Analysis metadata (client, date, competitors, etc.)")
    
    # HERO: Top opportunities (primary focus)
    top_opportunities: List[StrategicOpportunity] = Field(description="Top 3-5 strategic opportunities")
    opportunity_matrix: OpportunityMatrix = Field(description="Impact vs difficulty matrix")
    
    # Category-specific opportunities
    brand_opportunities: List[CategoryOpportunity] = Field(description="Brand strategy opportunities")
    product_opportunities: List[CategoryOpportunity] = Field(description="Product innovation opportunities")
    pricing_opportunities: List[CategoryOpportunity] = Field(description="Pricing strategy opportunities")
    market_opportunities: List[CategoryOpportunity] = Field(description="Market expansion opportunities")
    
    # Supporting competitive intelligence
    competitive_landscape: Dict[str, CompetitorProfile] = Field(description="Competitive landscape analysis")
    executive_summary: ExecutiveSummary = Field(description="Executive summary and recommendations")
    
    # Legacy compatibility (maintain existing clinical analysis)
    clinical_gaps: List[Dict[str, Any]] = Field(default=[], description="Clinical gaps (legacy)")
    market_share_insights: List[Dict[str, Any]] = Field(default=[], description="Market share insights (legacy)")
    
    # Metadata
    research_timestamp: str = Field(description="Analysis timestamp")
    confidence_score: float = Field(default=7.5, description="Overall analysis confidence (1-10)")

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