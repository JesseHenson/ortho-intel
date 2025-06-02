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
from .source_models import (
    SourceCollection, AnalysisMetadata, ProgressiveDisclosureModel, 
    DetailLevel, SourceCitation, SourceAnalysisResult, SourceType,
    ComprehensiveAnalysisMetadata, LangGraphNodeExecution, AnalysisMetadata,
    TavilySourceMetadata, SourceCollectionAnalyzer
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
    
    Enhanced with real source data integration and methodology transparency.
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
    
    # Real source integration (computed from actual source_collection)
    source_quality_indicator: Optional[str] = Field(default="⚪", description="Source quality visual indicator")
    methodology_confidence: Optional[float] = Field(default=7.0, description="Methodology confidence score (1-10)", ge=1, le=10)
    evidence_strength: Optional[str] = Field(default="Moderate", description="Evidence strength assessment")
    
    # Enhanced display helpers (computed from real data)
    credibility_indicator: Optional[str] = Field(default="⚪", description="Visual credibility indicator")
    source_count_display: Optional[str] = Field(default="No sources", description="Source count display text")
    
    # Progressive disclosure flags (computed from real analysis)
    has_detailed_analysis: bool = Field(default=True, description="Whether detailed analysis is available")
    has_source_analysis: bool = Field(default=True, description="Whether source analysis is available")
    has_methodology_trace: bool = Field(default=True, description="Whether methodology trace is available")
    
    # Real data summary fields
    primary_evidence_type: Optional[str] = Field(default=None, description="Primary type of evidence (e.g., 'Academic Research', 'Industry Report')")
    source_diversity_score: Optional[float] = Field(default=5.0, description="Source diversity score (1-10)", ge=1, le=10)
    analysis_completeness: Optional[float] = Field(default=7.0, description="Analysis completeness score (1-10)", ge=1, le=10)
    
    @model_validator(mode='after')
    def set_enhanced_display_fields(self):
        """Set enhanced display fields based on real source collection and analysis data"""
        
        # Source collection analysis
        if self.source_collection and self.source_collection.sources:
            sources = self.source_collection.sources
            
            # Calculate real credibility indicator
            avg_credibility = sum(source.credibility_score for source in sources) / len(sources)
            
            if avg_credibility >= 8.0:
                self.credibility_indicator = "🟢"
                self.source_quality_indicator = "🟢"
                self.evidence_strength = "Strong"
            elif avg_credibility >= 6.0:
                self.credibility_indicator = "🟡"
                self.source_quality_indicator = "🟡"
                self.evidence_strength = "Moderate"
            else:
                self.credibility_indicator = "🔴"
                self.source_quality_indicator = "🔴"
                self.evidence_strength = "Weak"
            
            # Calculate real source count display
            source_count = len(sources)
            if source_count == 1:
                self.source_count_display = "1 source"
            elif source_count <= 5:
                self.source_count_display = f"{source_count} sources"
            else:
                self.source_count_display = f"{source_count} sources (comprehensive)"
            
            # Determine primary evidence type
            source_types = [source.source_type for source in sources]
            type_counts = {}
            for source_type in source_types:
                type_counts[source_type.value] = type_counts.get(source_type.value, 0) + 1
            
            if type_counts:
                most_common_type = max(type_counts.keys(), key=lambda x: type_counts[x])
                self.primary_evidence_type = most_common_type.replace("_", " ").title()
            
            # Calculate source diversity
            unique_types = len(set(source_types))
            unique_domains = len(set(source.domain for source in sources))
            self.source_diversity_score = min(10.0, (unique_types * 2 + unique_domains) * 1.5)
            
            # Set flags based on real data
            self.has_source_analysis = True
            high_quality_sources = len([s for s in sources if s.credibility_score >= 7.0])
            self.analysis_completeness = min(10.0, (high_quality_sources / len(sources)) * 10)
            
        else:
            # Fallback for opportunities without sources
            self.credibility_indicator = "⚪"
            self.source_quality_indicator = "⚪"
            self.source_count_display = "No sources"
            self.evidence_strength = "Limited"
            self.primary_evidence_type = "Analysis-based"
            self.source_diversity_score = 3.0
            self.analysis_completeness = 5.0
            self.has_source_analysis = False
        
        # Methodology confidence based on analysis metadata
        if hasattr(self, 'analysis_metadata') and self.analysis_metadata:
            self.methodology_confidence = getattr(self.analysis_metadata, 'overall_confidence', 7.0)
            self.has_methodology_trace = True
        else:
            self.methodology_confidence = 7.0
            self.has_methodology_trace = False
        
        return self
    
    def get_quality_summary(self) -> Dict[str, Any]:
        """Get a comprehensive quality summary for this opportunity"""
        return {
            "overall_quality": self.evidence_strength,
            "source_indicators": {
                "credibility": self.credibility_indicator,
                "quality": self.source_quality_indicator,
                "count": self.source_count_display,
                "diversity": f"{self.source_diversity_score:.1f}/10"
            },
            "methodology_indicators": {
                "confidence": f"{self.methodology_confidence:.1f}/10",
                "completeness": f"{self.analysis_completeness:.1f}/10",
                "has_trace": self.has_methodology_trace
            },
            "evidence_profile": {
                "primary_type": self.primary_evidence_type,
                "strength": self.evidence_strength
            }
        }

class OpportunityDetail(OpportunitySummary):
    """
    Detail-level opportunity information for expanded views.
    
    Enhanced with comprehensive source analysis, methodology insights,
    and detailed implementation guidance derived from real research data.
    """
    
    # Extended opportunity information
    description: str = Field(description="Comprehensive opportunity description")
    expected_revenue_impact: str = Field(description="Expected revenue impact range")
    implementation_timeline: str = Field(description="Detailed implementation timeline")
    
    # Strategic context (derived from real source analysis)
    market_driver: str = Field(description="Key market driver behind this opportunity")
    competitive_advantage: str = Field(description="Competitive advantage gained")
    risk_assessment: str = Field(description="Key implementation risks identified")
    
    # Source-derived insights
    evidence_summary: Optional[str] = Field(default=None, description="Summary of supporting evidence")
    source_highlights: List[str] = Field(default_factory=list, description="Key insights from sources")
    methodology_summary: Optional[str] = Field(default=None, description="Summary of analysis methodology")
    
    # Real data quality indicators
    source_credibility_breakdown: Optional[Dict[str, int]] = Field(default_factory=dict, description="Breakdown of source credibility levels")
    evidence_type_distribution: Optional[Dict[str, int]] = Field(default_factory=dict, description="Distribution of evidence types")
    geographic_coverage: Optional[List[str]] = Field(default_factory=list, description="Geographic regions covered by sources")
    
    # Implementation guidance (derived from source analysis)
    next_steps: List[str] = Field(default_factory=list, description="Recommended next steps")
    key_stakeholders: List[str] = Field(default_factory=list, description="Key stakeholders to engage")
    success_metrics: List[str] = Field(default_factory=list, description="Metrics to track success")
    
    # Enhanced methodology insights
    search_strategy_used: Optional[str] = Field(default=None, description="Search strategy used for this opportunity")
    analysis_approach: Optional[str] = Field(default=None, description="Analysis approach taken")
    validation_methods: Optional[List[str]] = Field(default_factory=list, description="Methods used to validate findings")
    
    @model_validator(mode='after')
    def set_detail_level_enhancements(self):
        """Enhance detail-level fields based on real source and methodology data"""
        
        # Call parent validator first
        super().set_enhanced_display_fields()
        
        # Source analysis enhancements
        if self.source_collection and self.source_collection.sources:
            sources = self.source_collection.sources
            
            # Generate evidence summary from real sources
            high_quality_sources = [s for s in sources if s.credibility_score >= 7.0]
            if high_quality_sources:
                source_types = [s.source_type.value.replace("_", " ").title() for s in high_quality_sources]
                unique_types = list(set(source_types))
                self.evidence_summary = f"Evidence based on {len(high_quality_sources)} high-quality sources including {', '.join(unique_types[:3])}{'...' if len(unique_types) > 3 else ''}."
            
            # Extract source highlights from content snippets
            self.source_highlights = []
            for source in sources[:5]:  # Top 5 sources
                if source.content_snippet:
                    # Extract first meaningful sentence
                    sentences = source.content_snippet.split('. ')
                    if sentences and len(sentences[0]) > 50:
                        self.source_highlights.append(f"• {sentences[0].strip()}...")
            
            # Build credibility breakdown
            self.source_credibility_breakdown = {
                "High (8-10)": len([s for s in sources if s.credibility_score >= 8.0]),
                "Medium (6-7.9)": len([s for s in sources if 6.0 <= s.credibility_score < 8.0]),
                "Low (1-5.9)": len([s for s in sources if s.credibility_score < 6.0])
            }
            
            # Build evidence type distribution
            type_counts = {}
            for source in sources:
                type_name = source.source_type.value.replace("_", " ").title()
                type_counts[type_name] = type_counts.get(type_name, 0) + 1
            self.evidence_type_distribution = type_counts
            
            # Extract geographic coverage from domains/content
            self.geographic_coverage = self._extract_geographic_coverage(sources)
            
        # Methodology analysis enhancements
        if hasattr(self, 'analysis_metadata') and self.analysis_metadata:
            metadata = self.analysis_metadata
            
            # Extract methodology summary
            if hasattr(metadata, 'search_strategy'):
                self.search_strategy_used = metadata.search_strategy
            
            if hasattr(metadata, 'gap_analysis_method'):
                self.analysis_approach = f"Gap analysis using {metadata.gap_analysis_method}"
            
            if hasattr(metadata, 'langgraph_nodes_executed'):
                nodes = metadata.langgraph_nodes_executed
                self.methodology_summary = f"Analysis completed through {len(nodes)} specialized nodes: {', '.join(nodes[:3])}{'...' if len(nodes) > 3 else ''}"
            
            # Set validation methods based on processing
            self.validation_methods = [
                "Source credibility assessment",
                "Cross-reference validation",
                "Competitive analysis review"
            ]
            
            if hasattr(metadata, 'total_searches_performed') and metadata.total_searches_performed > 5:
                self.validation_methods.append("Comprehensive market research")
        
        return self
    
    def _extract_geographic_coverage(self, sources: List[SourceCitation]) -> List[str]:
        """Extract geographic coverage from source domains and content"""
        geographic_indicators = []
        
        # Common geographic indicators in domains and content
        geo_patterns = {
            'US/North America': ['.com', 'fda.gov', 'nih.gov', 'united states', 'america', 'usa'],
            'Europe': ['.eu', '.uk', '.de', '.fr', 'europe', 'european', 'brexit'],
            'Global': ['global', 'worldwide', 'international', 'multinational'],
            'Asia-Pacific': ['.jp', '.cn', '.au', 'asia', 'china', 'japan', 'australia']
        }
        
        for region, patterns in geo_patterns.items():
            for source in sources:
                domain_content = f"{source.domain} {source.content_snippet}".lower()
                if any(pattern in domain_content for pattern in patterns):
                    if region not in geographic_indicators:
                        geographic_indicators.append(region)
                    break
        
        return geographic_indicators or ["Market region analysis pending"]
    
    def get_detailed_quality_assessment(self) -> Dict[str, Any]:
        """Get detailed quality assessment for this opportunity"""
        base_assessment = self.get_quality_summary()
        
        return {
            **base_assessment,
            "detailed_indicators": {
                "credibility_breakdown": self.source_credibility_breakdown,
                "evidence_distribution": self.evidence_type_distribution,
                "geographic_coverage": self.geographic_coverage,
                "methodology_transparency": {
                    "search_strategy": self.search_strategy_used,
                    "analysis_approach": self.analysis_approach,
                    "validation_methods": self.validation_methods
                }
            },
            "implementation_readiness": {
                "next_steps_defined": len(self.next_steps) > 0,
                "stakeholders_identified": len(self.key_stakeholders) > 0,
                "success_metrics_available": len(self.success_metrics) > 0
            }
        }

class OpportunityFull(OpportunityDetail):
    """
    Complete opportunity information including full source analysis and methodology transparency.
    
    Provides comprehensive details for deep analysis, due diligence,
    and detailed planning. Includes complete methodology tracking,
    comprehensive source analysis, and full reasoning chains.
    Loaded on-demand for performance.
    """
    
    # Complete source information with enhanced analysis
    detailed_source_analysis: Optional[SourceAnalysisResult] = Field(
        default=None, 
        description="Detailed analysis of supporting sources with credibility assessment"
    )
    
    # Comprehensive methodology tracking
    comprehensive_methodology: Optional[ComprehensiveAnalysisMetadata] = Field(
        default=None,
        description="Complete methodology tracking from LangGraph pipeline"
    )
    
    # Node-by-node execution details
    langgraph_execution_trace: Optional[List[LangGraphNodeExecution]] = Field(
        default_factory=list,
        description="Detailed trace of LangGraph node executions"
    )
    
    # Reasoning and decision audit trail
    reasoning_chains: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Complete reasoning chains for transparency"
    )
    
    decision_audit_trail: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Audit trail of key decisions made during analysis"
    )
    
    # Extended analysis with full context
    detailed_analysis: Optional[str] = Field(
        default=None, 
        description="Comprehensive analysis with methodology, assumptions, and full context"
    )
    
    # Market context with source attribution
    market_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Detailed market context with source attributions and competitive landscape"
    )
    
    # Complete competitive intelligence
    competitive_intelligence: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Full competitive intelligence with source traceability"
    )
    
    # Implementation planning with methodology
    implementation_roadmap: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Detailed implementation roadmap with methodology-based milestones"
    )
    
    # Financial modeling with source backing
    financial_projections: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Financial projections with source-backed assumptions"
    )
    
    # Stakeholder analysis with evidence
    stakeholder_impact: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Impact on different stakeholders with supporting evidence"
    )
    
    # Quality assurance and validation
    quality_assurance_report: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Quality assurance documentation and validation results"
    )
    
    # Cross-validation results
    cross_validation_results: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Results of cross-validation checks and peer review"
    )
    
    # Performance metrics for methodology
    methodology_performance_metrics: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Performance metrics for the analysis methodology"
    )
    
    @model_validator(mode='after')
    def set_full_analysis_enhancements(self):
        """Enhance full-level fields with complete methodology and source integration"""
        
        # Call parent validator first
        super().set_detail_level_enhancements()
        
        # Comprehensive methodology integration
        if self.comprehensive_methodology:
            metadata = self.comprehensive_methodology
            
            # Set LangGraph execution trace
            self.langgraph_execution_trace = metadata.node_executions
            
            # Set reasoning chains
            self.reasoning_chains = metadata.reasoning_chains
            
            # Set decision audit trail
            self.decision_audit_trail = metadata.decision_audit_trail
            
            # Create quality assurance report
            self.quality_assurance_report = {
                "validation_steps": metadata.quality_assurance.validation_steps,
                "bias_mitigation": metadata.quality_assurance.bias_mitigation_strategies,
                "confidence_assessment": metadata.quality_assurance.confidence_assessment_method,
                "overall_score": metadata.overall_confidence
            }
            
            # Create methodology performance metrics
            self.methodology_performance_metrics = {
                "processing_time": f"{metadata.total_processing_time:.2f}s",
                "sources_analyzed": metadata.total_sources_analyzed,
                "high_quality_sources": metadata.high_quality_sources_count,
                "ai_interactions": metadata.ai_interactions_count,
                "data_transformations": metadata.data_transformations_count,
                "search_efficiency": f"{metadata.search_success_rate:.1%}" if hasattr(metadata, 'search_success_rate') else "Not available"
            }
        
        # Enhanced source analysis integration
        if self.source_collection and self.source_collection.sources:
            sources = self.source_collection.sources
            
            # Create detailed source analysis if not provided
            if not self.detailed_source_analysis:
                self.detailed_source_analysis = SourceAnalysisResult(
                    total_sources=len(sources),
                    credible_sources=len([s for s in sources if s.credibility_score >= 7.0]),
                    source_types=[s.source_type.value for s in sources],
                    geographic_coverage=self.geographic_coverage or [],
                    quality_score=sum(s.credibility_score for s in sources) / len(sources),
                    reliability_assessment="High" if sum(s.credibility_score for s in sources) / len(sources) >= 8.0 else "Moderate",
                    bias_indicators=[],
                    source_diversity_score=self.source_diversity_score or 5.0,
                    recommendations=[]
                )
            
            # Create comprehensive market context with source attribution
            if not self.market_context:
                self.market_context = {
                    "market_size_indicators": self._extract_market_indicators(sources),
                    "competitive_landscape": self._extract_competitive_insights(sources),
                    "technology_trends": self._extract_technology_trends(sources),
                    "regulatory_environment": self._extract_regulatory_insights(sources),
                    "source_attribution": {
                        source.url: {
                            "domain": source.domain,
                            "credibility": source.credibility_score,
                            "relevance": source.relevance_score,
                            "contribution": source.content_snippet[:100] + "..." if source.content_snippet else ""
                        }
                        for source in sources[:10]  # Top 10 sources
                    }
                }
            
            # Create competitive intelligence with full traceability
            if not self.competitive_intelligence:
                self.competitive_intelligence = {
                    "competitor_analysis": self._create_competitor_analysis(sources),
                    "market_positioning": self._extract_positioning_insights(sources),
                    "opportunity_gaps": self._identify_opportunity_gaps(sources),
                    "threat_assessment": self._assess_competitive_threats(sources),
                    "source_traceability": {
                        "primary_sources": [s.url for s in sources if s.credibility_score >= 8.0],
                        "supporting_sources": [s.url for s in sources if 6.0 <= s.credibility_score < 8.0],
                        "methodology": self.analysis_approach,
                        "validation_approach": self.validation_methods
                    }
                }
        
        return self
    
    def _extract_market_indicators(self, sources: List[SourceCitation]) -> Dict[str, Any]:
        """Extract market size and growth indicators from sources"""
        market_keywords = ['market size', 'growth rate', 'cagr', 'revenue', 'billion', 'million']
        indicators = {}
        
        for source in sources:
            if source.content_snippet:
                content_lower = source.content_snippet.lower()
                for keyword in market_keywords:
                    if keyword in content_lower:
                        indicators[f"market_indicator_{len(indicators)}"] = {
                            "source": source.url,
                            "snippet": source.content_snippet[:200],
                            "credibility": source.credibility_score
                        }
                        break
        
        return indicators
    
    def _extract_competitive_insights(self, sources: List[SourceCitation]) -> Dict[str, Any]:
        """Extract competitive landscape insights from sources"""
        competitive_keywords = ['competitor', 'market share', 'leading', 'dominant', 'challenge']
        insights = {}
        
        for source in sources:
            if source.content_snippet:
                content_lower = source.content_snippet.lower()
                if any(keyword in content_lower for keyword in competitive_keywords):
                    insights[f"competitive_insight_{len(insights)}"] = {
                        "source": source.url,
                        "insight": source.content_snippet[:300],
                        "credibility": source.credibility_score
                    }
        
        return insights
    
    def _extract_technology_trends(self, sources: List[SourceCitation]) -> Dict[str, Any]:
        """Extract technology trend insights from sources"""
        tech_keywords = ['innovation', 'technology', 'digital', 'ai', 'automation', 'advancement']
        trends = {}
        
        for source in sources:
            if source.content_snippet:
                content_lower = source.content_snippet.lower()
                if any(keyword in content_lower for keyword in tech_keywords):
                    trends[f"tech_trend_{len(trends)}"] = {
                        "source": source.url,
                        "trend": source.content_snippet[:250],
                        "credibility": source.credibility_score
                    }
        
        return trends
    
    def _extract_regulatory_insights(self, sources: List[SourceCitation]) -> Dict[str, Any]:
        """Extract regulatory environment insights from sources"""
        reg_keywords = ['regulation', 'fda', 'approval', 'compliance', 'regulatory', 'guideline']
        insights = {}
        
        for source in sources:
            if source.content_snippet:
                content_lower = source.content_snippet.lower()
                if any(keyword in content_lower for keyword in reg_keywords):
                    insights[f"regulatory_insight_{len(insights)}"] = {
                        "source": source.url,
                        "insight": source.content_snippet[:200],
                        "credibility": source.credibility_score
                    }
        
        return insights
    
    def _create_competitor_analysis(self, sources: List[SourceCitation]) -> Dict[str, Any]:
        """Create comprehensive competitor analysis from sources"""
        return {
            "methodology": "Source-based competitive analysis",
            "source_count": len(sources),
            "analysis_depth": "Comprehensive" if len(sources) >= 10 else "Moderate",
            "competitive_factors": self._extract_competitive_factors(sources)
        }
    
    def _extract_competitive_factors(self, sources: List[SourceCitation]) -> List[Dict[str, Any]]:
        """Extract competitive factors from source content"""
        factors = []
        factor_keywords = ['strength', 'weakness', 'advantage', 'disadvantage', 'position', 'strategy']
        
        for source in sources[:5]:  # Top 5 sources
            if source.content_snippet:
                content_lower = source.content_snippet.lower()
                for keyword in factor_keywords:
                    if keyword in content_lower:
                        factors.append({
                            "factor": keyword.title(),
                            "evidence": source.content_snippet[:150],
                            "source": source.url,
                            "credibility": source.credibility_score
                        })
                        break
        
        return factors
    
    def _extract_positioning_insights(self, sources: List[SourceCitation]) -> Dict[str, Any]:
        """Extract market positioning insights from sources"""
        return {
            "positioning_strategy": "Evidence-based positioning",
            "market_segments": self._identify_market_segments(sources),
            "differentiation_factors": self._extract_differentiation_factors(sources)
        }
    
    def _identify_market_segments(self, sources: List[SourceCitation]) -> List[str]:
        """Identify market segments mentioned in sources"""
        segment_keywords = ['segment', 'market', 'demographic', 'target', 'customer']
        segments = []
        
        for source in sources:
            if source.content_snippet and any(keyword in source.content_snippet.lower() for keyword in segment_keywords):
                segments.append(f"Segment identified in {source.domain}")
        
        return segments
    
    def _extract_differentiation_factors(self, sources: List[SourceCitation]) -> List[str]:
        """Extract differentiation factors from sources"""
        diff_keywords = ['unique', 'different', 'innovative', 'first', 'leading', 'superior']
        factors = []
        
        for source in sources:
            if source.content_snippet:
                content_lower = source.content_snippet.lower()
                for keyword in diff_keywords:
                    if keyword in content_lower:
                        factors.append(f"Differentiation factor from {source.domain}")
                        break
        
        return factors
    
    def _identify_opportunity_gaps(self, sources: List[SourceCitation]) -> Dict[str, Any]:
        """Identify opportunity gaps from source analysis"""
        return {
            "gap_identification_method": "Source content analysis",
            "gaps_identified": len([s for s in sources if 'gap' in s.content_snippet.lower() if s.content_snippet]),
            "opportunity_indicators": self._extract_opportunity_indicators(sources)
        }
    
    def _extract_opportunity_indicators(self, sources: List[SourceCitation]) -> List[str]:
        """Extract opportunity indicators from sources"""
        opp_keywords = ['opportunity', 'potential', 'gap', 'unmet', 'need', 'demand']
        indicators = []
        
        for source in sources:
            if source.content_snippet:
                content_lower = source.content_snippet.lower()
                for keyword in opp_keywords:
                    if keyword in content_lower:
                        indicators.append(f"Opportunity indicator from {source.domain}")
                        break
        
        return indicators
    
    def _assess_competitive_threats(self, sources: List[SourceCitation]) -> Dict[str, Any]:
        """Assess competitive threats from sources"""
        threat_keywords = ['threat', 'risk', 'challenge', 'competition', 'disrupt']
        threats = []
        
        for source in sources:
            if source.content_snippet:
                content_lower = source.content_snippet.lower()
                if any(keyword in content_lower for keyword in threat_keywords):
                    threats.append({
                        "threat_indicator": source.content_snippet[:100],
                        "source": source.url,
                        "credibility": source.credibility_score
                    })
        
        return {
            "threat_assessment_method": "Source-based threat analysis",
            "threats_identified": len(threats),
            "threat_details": threats[:5]  # Top 5 threats
        }
    
    def get_comprehensive_transparency_report(self) -> Dict[str, Any]:
        """Get complete transparency report for this opportunity analysis"""
        base_report = self.get_detailed_quality_assessment()
        
        return {
            **base_report,
            "methodology_transparency": {
                "langgraph_execution": {
                    "nodes_executed": len(self.langgraph_execution_trace) if self.langgraph_execution_trace else 0,
                    "total_processing_time": self.methodology_performance_metrics.get("processing_time") if self.methodology_performance_metrics else "Not available",
                    "decision_points": len(self.decision_audit_trail) if self.decision_audit_trail else 0
                },
                "reasoning_transparency": {
                    "reasoning_chains": len(self.reasoning_chains) if self.reasoning_chains else 0,
                    "decision_audit_available": bool(self.decision_audit_trail),
                    "quality_assurance_performed": bool(self.quality_assurance_report)
                },
                "source_transparency": {
                    "detailed_analysis_available": bool(self.detailed_source_analysis),
                    "market_context_sourced": bool(self.market_context),
                    "competitive_intelligence_backed": bool(self.competitive_intelligence)
                }
            },
            "validation_and_quality": {
                "cross_validation_performed": bool(self.cross_validation_results),
                "performance_metrics_available": bool(self.methodology_performance_metrics),
                "quality_assurance_score": self.quality_assurance_report.get("overall_score") if self.quality_assurance_report else None
            }
        }

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