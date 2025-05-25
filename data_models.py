# data_models.py
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

# LangGraph State Schema
class GraphState(TypedDict):
    """State schema for the competitive intelligence graph"""
    # Input data
    competitors: List[str]
    focus_area: str
    
    # Research results
    search_queries: List[str]
    raw_research_results: List[Dict[str, Any]]
    
    # Analysis results
    clinical_gaps: List[Dict[str, Any]]
    market_opportunities: List[Dict[str, Any]]
    
    # Final output
    final_report: Optional[Dict[str, Any]]
    
    # Metadata
    current_competitor: Optional[str]
    research_iteration: int
    error_messages: List[str]

# API Request/Response Models
class CompetitorAnalysisRequest(BaseModel):
    """Request model for competitor analysis API"""
    competitors: List[str] = Field(
        description="List of competitor company names to analyze",
        min_items=1,
        max_items=5
    )
    focus_area: str = Field(
        default="spine_fusion",
        description="Medical device focus area"
    )

class ClinicalGap(BaseModel):
    """Model for identified clinical gaps"""
    competitor: str = Field(description="Competitor company name")
    gap_type: str = Field(description="Type of gap (clinical, regulatory, market)")
    description: str = Field(description="Description of the gap")
    evidence: str = Field(description="Supporting evidence from research")
    severity: str = Field(description="Gap severity: high, medium, low")
    source_url: Optional[str] = Field(description="Source URL for evidence")

class MarketOpportunity(BaseModel):
    """Model for identified market opportunities"""
    opportunity_type: str = Field(description="Type of opportunity")
    description: str = Field(description="Description of the opportunity")
    market_size_indicator: Optional[str] = Field(description="Indication of market size")
    competitive_landscape: str = Field(description="Current competitive situation")
    evidence: str = Field(description="Supporting evidence")
    source_url: Optional[str] = Field(description="Source URL for evidence")

class CompetitorProfile(BaseModel):
    """Profile of a single competitor"""
    name: str
    clinical_gaps: List[ClinicalGap]
    recent_activities: List[str]
    regulatory_issues: List[str]

class CompetitorAnalysisResponse(BaseModel):
    """Response model for competitor analysis API"""
    competitors_analyzed: List[str]
    clinical_gaps: List[ClinicalGap] = Field(description="Identified clinical gaps")
    market_opportunities: List[MarketOpportunity] = Field(description="Identified opportunities")
    summary: str = Field(description="Executive summary of findings")
    research_timestamp: str = Field(description="When the analysis was performed")
    
    class Config:
        json_encoders = {
            # Add custom encoders if needed
        }

# Search Query Templates
class SearchTemplates:
    """Predefined search query templates for different research areas"""
    
    CLINICAL_LIMITATIONS = "{competitor} spine fusion clinical limitations complications"
    FDA_ISSUES = "{competitor} FDA warning letters recalls spine orthopedic"
    MARKET_GAPS = "unmet needs {focus_area} surgery clinical challenges"
    COMPETITIVE_LANDSCAPE = "{competitor} market share spine fusion devices"
    INNOVATION_PIPELINE = "{competitor} new products pipeline spine orthopedic 2024"
    
    @classmethod
    def get_competitor_queries(cls, competitor: str, focus_area: str) -> List[str]:
        """Generate all search queries for a specific competitor"""
        return [
            cls.CLINICAL_LIMITATIONS.format(competitor=competitor),
            cls.FDA_ISSUES.format(competitor=competitor),
            cls.INNOVATION_PIPELINE.format(competitor=competitor)
        ]
    
    @classmethod
    def get_market_queries(cls, focus_area: str) -> List[str]:
        """Generate market-focused search queries"""
        return [
            cls.MARKET_GAPS.format(focus_area=focus_area),
            f"{focus_area} surgery challenges limitations 2024"
        ]

# Analysis Result Processing
class AnalysisProcessor:
    """Helper class for processing raw research results into structured insights"""
    
    @staticmethod
    def extract_clinical_gaps(research_results: List[Dict], competitor: str) -> List[ClinicalGap]:
        """Extract clinical gaps from raw research results"""
        gaps = []
        
        for result in research_results:
            content = result.get('content', '')
            url = result.get('url', '')
            
            # Look for gap indicators in content
            gap_keywords = ['limitation', 'complication', 'failure', 'recall', 'warning']
            
            if any(keyword in content.lower() for keyword in gap_keywords):
                gap = ClinicalGap(
                    competitor=competitor,
                    gap_type="clinical",
                    description=content[:200] + "..." if len(content) > 200 else content,
                    evidence=content[:500],
                    severity="medium",  # Default, could be enhanced with NLP
                    source_url=url
                )
                gaps.append(gap)
        
        return gaps
    
    @staticmethod
    def extract_market_opportunities(research_results: List[Dict]) -> List[MarketOpportunity]:
        """Extract market opportunities from raw research results"""
        opportunities = []
        
        for result in research_results:
            content = result.get('content', '')
            url = result.get('url', '')
            
            # Look for opportunity indicators
            opportunity_keywords = ['unmet need', 'gap', 'opportunity', 'emerging', 'trend']
            
            if any(keyword in content.lower() for keyword in opportunity_keywords):
                opportunity = MarketOpportunity(
                    opportunity_type="market_gap",
                    description=content[:200] + "..." if len(content) > 200 else content,
                    market_size_indicator="TBD",
                    competitive_landscape="Underserved",
                    evidence=content[:500],
                    source_url=url
                )
                opportunities.append(opportunity)
        
        return opportunities

# Configuration
class Config:
    """Application configuration"""
    MAX_COMPETITORS = 5
    MAX_SEARCH_RESULTS = 5
    FOCUS_AREAS = ["spine_fusion", "joint_replacement", "trauma", "sports_medicine"]
    
    # Tavily settings
    TAVILY_MAX_RESULTS = 5
    TAVILY_SEARCH_DEPTH = "advanced"
    
    # Report settings
    MIN_GAPS_FOR_REPORT = 2
    MIN_OPPORTUNITIES_FOR_REPORT = 1