# data_models.py
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

# Device Category Configuration
DEVICE_CATEGORIES = {
    "cardiovascular": {
        "name": "Cardiovascular Devices",
        "description": "Heart and vascular medical devices",
        "competitors": [
            "Medtronic", "Abbott", "Boston Scientific", "Edwards Lifesciences",
            "Biotronik", "LivaNova", "Terumo", "Cook Medical"
        ],
        "keywords": [
            "stent", "heart valve", "pacemaker", "defibrillator", "catheter",
            "angioplasty", "cardiac", "vascular", "coronary", "aortic"
        ]
    },
    "spine_fusion": {
        "name": "Spine Fusion Devices", 
        "description": "Spinal fusion and vertebral devices",
        "competitors": [
            "Stryker Spine", "Zimmer Biomet", "Orthofix", "NuVasive",
            "Medtronic Spine", "DePuy Synthes", "Globus Medical", "SeaSpine"
        ],
        "keywords": [
            "spine fusion", "vertebral", "spinal implant", "pedicle screw",
            "cervical", "lumbar", "thoracic", "disc replacement", "scoliosis"
        ]
    },
    "joint_replacement": {
        "name": "Joint Replacement Devices",
        "description": "Hip, knee, and other joint replacement devices", 
        "competitors": [
            "Stryker Ortho", "Zimmer Biomet", "DePuy Synthes", "Smith+Nephew",
            "Wright Medical", "MicroPort", "Conformis", "Exactech"
        ],
        "keywords": [
            "hip replacement", "knee replacement", "arthroplasty", "joint implant",
            "prosthetic", "orthopedic implant", "total knee", "total hip"
        ]
    },
    "diabetes_care": {
        "name": "Diabetes Care Devices",
        "description": "Glucose monitoring and insulin delivery devices",
        "competitors": [
            "Dexcom", "Abbott", "Medtronic Diabetes", "Tandem", "Insulet",
            "Roche", "LifeScan", "Ascensia", "Senseonics"
        ],
        "keywords": [
            "glucose monitoring", "CGM", "insulin pump", "diabetes", "blood glucose",
            "continuous glucose", "diabetic", "glycemic", "HbA1c"
        ]
    }
}

# Category Detection and Routing
class CategoryRouter:
    """Intelligent device category detection and routing"""
    
    @classmethod
    def detect_category(cls, competitors: List[str], context: str = "") -> str:
        """
        Detect device category based on competitors and context
        
        Args:
            competitors: List of competitor company names
            context: Additional context (focus area, description, etc.)
            
        Returns:
            Detected category name (defaults to 'spine_fusion' if uncertain)
        """
        category_scores = {}
        
        # Initialize scores for all categories
        for category in DEVICE_CATEGORIES:
            category_scores[category] = 0
        
        # Score based on competitor name matches
        for competitor in competitors:
            competitor_lower = competitor.lower()
            
            for category, config in DEVICE_CATEGORIES.items():
                for known_competitor in config["competitors"]:
                    known_lower = known_competitor.lower()
                    
                    # Exact match or partial match
                    if competitor_lower == known_lower:
                        category_scores[category] += 10  # Exact match
                    elif competitor_lower in known_lower or known_lower in competitor_lower:
                        category_scores[category] += 8   # Partial match
                    elif any(word in competitor_lower for word in known_lower.split()):
                        category_scores[category] += 5   # Word match
        
        # Score based on context keywords
        if context:
            context_lower = context.lower()
            
            for category, config in DEVICE_CATEGORIES.items():
                for keyword in config["keywords"]:
                    if keyword.lower() in context_lower:
                        category_scores[category] += 5
        
        # Find highest scoring category
        best_category = max(category_scores, key=category_scores.get)
        best_score = category_scores[best_category]
        
        # Fallback to spine_fusion if no clear winner (score < 5)
        if best_score < 5:
            return "spine_fusion"
        
        return best_category
    
    @classmethod
    def get_category_info(cls, category: str) -> Dict[str, Any]:
        """Get detailed information about a device category"""
        return DEVICE_CATEGORIES.get(category, DEVICE_CATEGORIES["spine_fusion"])
    
    @classmethod
    def get_all_categories(cls) -> List[str]:
        """Get list of all available categories"""
        return list(DEVICE_CATEGORIES.keys())

# LangGraph State Schema
class GraphState(TypedDict):
    """State schema for the competitive intelligence graph"""
    # Input data
    competitors: List[str]
    focus_area: str
    device_category: str  # Auto-detected device category
    
    # Research results
    search_queries: List[str]
    raw_research_results: List[Dict[str, Any]]
    
    # Analysis results (existing)
    clinical_gaps: List[Dict[str, Any]]
    market_opportunities: List[Dict[str, Any]]
    
    # NEW: Market intelligence analysis results
    market_share_insights: List[Dict[str, Any]]
    brand_positioning: List[Dict[str, Any]]
    product_feature_gaps: List[Dict[str, Any]]
    competitive_landscape: Optional[Dict[str, Any]]
    
    # NEW: Opportunity-first analysis results
    all_opportunities: List[Dict[str, Any]]
    top_opportunities: List[Dict[str, Any]]
    brand_opportunities: List[Dict[str, Any]]
    product_opportunities: List[Dict[str, Any]]
    pricing_opportunities: List[Dict[str, Any]]
    market_expansion_opportunities: List[Dict[str, Any]]
    executive_summary: Optional[Dict[str, Any]]
    competitive_profiles: Optional[Dict[str, Any]]
    
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

# NEW MARKET INTELLIGENCE MODELS
class MarketShareInsight(BaseModel):
    """Model for market share and positioning insights"""
    competitor: str = Field(description="Competitor company name")
    market_position: str = Field(description="Market position (leader, challenger, follower, niche)")
    estimated_market_share: Optional[str] = Field(description="Estimated market share percentage or range")
    revenue_estimate: Optional[str] = Field(description="Revenue estimates or indicators")
    growth_trend: str = Field(description="Growth trend (growing, stable, declining)")
    key_markets: List[str] = Field(description="Key geographic or segment markets")
    evidence: str = Field(description="Supporting evidence from research")
    source_url: Optional[str] = Field(description="Source URL for evidence")

class BrandPositioning(BaseModel):
    """Model for brand positioning analysis"""
    competitor: str = Field(description="Competitor company name")
    brand_message: str = Field(description="Primary brand messaging or value proposition")
    target_segments: List[str] = Field(description="Target customer segments")
    differentiation_factors: List[str] = Field(description="Key differentiation factors")
    brand_strengths: List[str] = Field(description="Identified brand strengths")
    brand_weaknesses: List[str] = Field(description="Identified brand weaknesses")
    evidence: str = Field(description="Supporting evidence from research")
    source_url: Optional[str] = Field(description="Source URL for evidence")

class ProductFeatureGap(BaseModel):
    """Model for product feature gap analysis"""
    competitor: str = Field(description="Competitor company name")
    product_category: str = Field(description="Product category being analyzed")
    competitor_advantages: List[str] = Field(description="Features where competitor has advantage")
    competitor_gaps: List[str] = Field(description="Features where competitor has gaps")
    feature_comparison: Dict[str, str] = Field(description="Feature-by-feature comparison")
    innovation_areas: List[str] = Field(description="Areas of recent innovation")
    evidence: str = Field(description="Supporting evidence from research")
    source_url: Optional[str] = Field(description="Source URL for evidence")

class CompetitiveLandscape(BaseModel):
    """Model for competitive landscape analysis"""
    market_overview: str = Field(description="Overall market landscape description")
    key_players: List[str] = Field(description="Key players in the market")
    market_dynamics: str = Field(description="Current market dynamics and trends")
    competitive_intensity: str = Field(description="Level of competitive intensity")
    barriers_to_entry: List[str] = Field(description="Barriers to entry in the market")
    opportunities: List[str] = Field(description="Strategic opportunities identified")
    threats: List[str] = Field(description="Competitive threats identified")
    evidence: str = Field(description="Supporting evidence from research")
    source_urls: List[str] = Field(description="Source URLs for evidence")

class CompetitorProfile(BaseModel):
    """Profile of a single competitor"""
    name: str
    clinical_gaps: List[ClinicalGap]
    recent_activities: List[str]
    regulatory_issues: List[str]

class CompetitorAnalysisResponse(BaseModel):
    """Response model for competitor analysis API"""
    competitors_analyzed: List[str]
    
    # Existing analysis results
    clinical_gaps: List[ClinicalGap] = Field(description="Identified clinical gaps")
    market_opportunities: List[MarketOpportunity] = Field(description="Identified opportunities")
    
    # NEW: Market intelligence results
    market_share_insights: List[MarketShareInsight] = Field(default=[], description="Market share and positioning insights")
    brand_positioning: List[BrandPositioning] = Field(default=[], description="Brand positioning analysis")
    product_feature_gaps: List[ProductFeatureGap] = Field(default=[], description="Product feature gap analysis")
    competitive_landscape: Optional[CompetitiveLandscape] = Field(default=None, description="Competitive landscape overview")
    
    summary: str = Field(description="Executive summary of findings")
    research_timestamp: str = Field(description="When the analysis was performed")
    
    class Config:
        json_encoders = {
            # Add custom encoders if needed
        }

# Search Query Templates
class SearchTemplates:
    """Predefined search query templates for different research areas"""
    
    # Category-specific search templates
    CATEGORY_TEMPLATES = {
        "cardiovascular": {
            "clinical_limitations": "{competitor} stent complications heart valve failure rates",
            "fda_issues": "{competitor} FDA warning letters recalls cardiovascular devices",
            "market_gaps": "unmet needs cardiovascular surgery cardiac device limitations",
            "innovation_pipeline": "{competitor} new cardiovascular devices pipeline 2024",
            "competitive_landscape": "{competitor} market share cardiovascular stent valve"
        },
        "spine_fusion": {
            "clinical_limitations": "{competitor} spine fusion clinical limitations complications",
            "fda_issues": "{competitor} FDA warning letters recalls spine orthopedic",
            "market_gaps": "unmet needs spine_fusion surgery clinical challenges",
            "innovation_pipeline": "{competitor} new products pipeline spine orthopedic 2024",
            "competitive_landscape": "{competitor} market share spine fusion devices"
        },
        "joint_replacement": {
            "clinical_limitations": "{competitor} hip knee replacement complications failure rates",
            "fda_issues": "{competitor} FDA warning letters recalls orthopedic implants",
            "market_gaps": "unmet needs joint replacement arthroplasty challenges",
            "innovation_pipeline": "{competitor} new orthopedic implants pipeline 2024",
            "competitive_landscape": "{competitor} market share joint replacement devices"
        },
        "diabetes_care": {
            "clinical_limitations": "{competitor} CGM insulin pump accuracy complications",
            "fda_issues": "{competitor} FDA warning letters recalls diabetes devices",
            "market_gaps": "unmet needs diabetes care glucose monitoring challenges",
            "innovation_pipeline": "{competitor} new diabetes devices pipeline 2024",
            "competitive_landscape": "{competitor} market share diabetes care devices"
        }
    }
    
    # Legacy templates for backward compatibility
    CLINICAL_LIMITATIONS = "{competitor} spine fusion clinical limitations complications"
    FDA_ISSUES = "{competitor} FDA warning letters recalls spine orthopedic"
    MARKET_GAPS = "unmet needs {focus_area} surgery clinical challenges"
    COMPETITIVE_LANDSCAPE = "{competitor} market share spine fusion devices"
    INNOVATION_PIPELINE = "{competitor} new products pipeline spine orthopedic 2024"
    
    @classmethod
    def get_competitor_queries(cls, competitor: str, focus_area: str, device_category: str = None) -> List[str]:
        """
        Generate all search queries for a specific competitor
        
        Args:
            competitor: Competitor company name
            focus_area: Focus area (for backward compatibility)
            device_category: Device category (if None, defaults to spine_fusion)
        """
        # Use device_category if provided, otherwise fallback to spine_fusion for compatibility
        category = device_category or "spine_fusion"
        
        # Get category-specific templates
        templates = cls.CATEGORY_TEMPLATES.get(category, cls.CATEGORY_TEMPLATES["spine_fusion"])
        
        return [
            templates["clinical_limitations"].format(competitor=competitor),
            templates["fda_issues"].format(competitor=competitor),
            templates["innovation_pipeline"].format(competitor=competitor)
        ]
    
    @classmethod
    def get_market_queries(cls, focus_area: str, device_category: str = None) -> List[str]:
        """
        Generate market-focused search queries
        
        Args:
            focus_area: Focus area (for backward compatibility)
            device_category: Device category (if None, defaults to spine_fusion)
        """
        # Use device_category if provided, otherwise fallback to spine_fusion for compatibility
        category = device_category or "spine_fusion"
        
        # Get category-specific templates
        templates = cls.CATEGORY_TEMPLATES.get(category, cls.CATEGORY_TEMPLATES["spine_fusion"])
        
        return [
            templates["market_gaps"],
            templates["competitive_landscape"].format(competitor="market analysis")
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