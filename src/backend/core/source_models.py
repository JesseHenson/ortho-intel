"""
Source Citation and Metadata Models for Progressive Disclosure
Supports credibility scoring, source tracking, and detailed analysis metadata
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, HttpUrl, validator, model_validator
from datetime import datetime
from enum import Enum

# Source Type Classifications
class SourceType(str, Enum):
    """Types of information sources"""
    ACADEMIC_PAPER = "Academic Paper"
    INDUSTRY_REPORT = "Industry Report"
    NEWS_ARTICLE = "News Article"
    COMPANY_WEBSITE = "Company Website"
    PRESS_RELEASE = "Press Release"
    REGULATORY_FILING = "Regulatory Filing"
    PATENT_DOCUMENT = "Patent Document"
    CONFERENCE_PRESENTATION = "Conference Presentation"
    MARKET_RESEARCH = "Market Research"
    SOCIAL_MEDIA = "Social Media"
    BLOG_POST = "Blog Post"
    UNKNOWN = "Unknown"

class CredibilityLevel(str, Enum):
    """Source credibility levels"""
    VERY_HIGH = "Very High"  # 9-10: Peer-reviewed, regulatory
    HIGH = "High"           # 7-8: Established industry sources
    MEDIUM = "Medium"       # 5-6: General news, company sources
    LOW = "Low"            # 3-4: Blogs, social media
    VERY_LOW = "Very Low"  # 1-2: Unverified sources

class RelevanceLevel(str, Enum):
    """Content relevance levels"""
    HIGHLY_RELEVANT = "Highly Relevant"    # 9-10: Direct match
    RELEVANT = "Relevant"                  # 7-8: Strong connection
    SOMEWHAT_RELEVANT = "Somewhat Relevant" # 5-6: Partial match
    MARGINALLY_RELEVANT = "Marginally Relevant" # 3-4: Weak connection
    NOT_RELEVANT = "Not Relevant"          # 1-2: No clear connection

# Core Source Models
class SourceCitation(BaseModel):
    """
    Comprehensive source citation with credibility and relevance scoring.
    
    Used for tracking information sources in competitive intelligence analysis,
    supporting progressive disclosure and source verification.
    """
    
    # Basic source information
    url: str = Field(description="Source URL")
    title: str = Field(description="Source title or headline")
    domain: str = Field(description="Source domain (e.g., 'reuters.com')")
    
    # Content metadata
    content_snippet: str = Field(description="Relevant content excerpt (max 500 chars)", max_length=500)
    full_content: Optional[str] = Field(default=None, description="Full content if available")
    
    # Classification and scoring
    source_type: SourceType = Field(description="Type of source")
    credibility_score: float = Field(description="Credibility score (1-10)", ge=1, le=10)
    credibility_level: Optional[CredibilityLevel] = Field(default=None, description="Credibility level category")
    relevance_score: float = Field(description="Relevance score (1-10)", ge=1, le=10)
    relevance_level: Optional[RelevanceLevel] = Field(default=None, description="Relevance level category")
    
    # Temporal information
    retrieved_at: datetime = Field(description="When the source was retrieved")
    published_at: Optional[datetime] = Field(default=None, description="When the content was published")
    
    # Analysis metadata
    key_insights: List[str] = Field(default=[], description="Key insights extracted from source")
    supporting_quotes: List[str] = Field(default=[], description="Direct quotes supporting analysis")
    
    # Verification status
    verified: bool = Field(default=False, description="Whether source has been manually verified")
    verification_notes: Optional[str] = Field(default=None, description="Manual verification notes")
    
    @model_validator(mode='after')
    def set_credibility_and_relevance_levels(self):
        """Set credibility and relevance levels after initialization"""
        if self.credibility_level is None:
            score = self.credibility_score
            if score >= 9:
                self.credibility_level = CredibilityLevel.VERY_HIGH
            elif score >= 7:
                self.credibility_level = CredibilityLevel.HIGH
            elif score >= 5:
                self.credibility_level = CredibilityLevel.MEDIUM
            elif score >= 3:
                self.credibility_level = CredibilityLevel.LOW
            else:
                self.credibility_level = CredibilityLevel.VERY_LOW
        
        if self.relevance_level is None:
            score = self.relevance_score
            if score >= 9:
                self.relevance_level = RelevanceLevel.HIGHLY_RELEVANT
            elif score >= 7:
                self.relevance_level = RelevanceLevel.RELEVANT
            elif score >= 5:
                self.relevance_level = RelevanceLevel.SOMEWHAT_RELEVANT
            elif score >= 3:
                self.relevance_level = RelevanceLevel.MARGINALLY_RELEVANT
            else:
                self.relevance_level = RelevanceLevel.NOT_RELEVANT
        
        return self

class SourceCollection(BaseModel):
    """
    Collection of sources with aggregated metadata.
    
    Used for managing multiple sources supporting a single analysis point
    or opportunity, with overall credibility and coverage metrics.
    """
    
    sources: List[SourceCitation] = Field(description="List of source citations")
    
    # Aggregated metrics
    average_credibility: Optional[float] = Field(default=5.0, description="Average credibility score", ge=1, le=10)
    average_relevance: Optional[float] = Field(default=5.0, description="Average relevance score", ge=1, le=10)
    source_diversity: Optional[float] = Field(default=5.0, description="Source type diversity score (1-10)", ge=1, le=10)
    
    # Coverage analysis
    total_sources: Optional[int] = Field(default=0, description="Total number of sources")
    high_credibility_count: Optional[int] = Field(default=0, description="Number of high credibility sources (7+)")
    verified_count: Optional[int] = Field(default=0, description="Number of manually verified sources")
    
    # Content analysis
    key_themes: List[str] = Field(default=[], description="Key themes across sources")
    consensus_level: Optional[float] = Field(default=5.0, description="Level of consensus across sources (1-10)", ge=1, le=10)
    
    @model_validator(mode='after')
    def calculate_metrics(self):
        """Calculate aggregated metrics from sources"""
        if self.sources:
            # Calculate average credibility
            self.average_credibility = sum(s.credibility_score for s in self.sources) / len(self.sources)
            
            # Calculate average relevance
            self.average_relevance = sum(s.relevance_score for s in self.sources) / len(self.sources)
            
            # Calculate counts
            self.total_sources = len(self.sources)
            self.high_credibility_count = len([s for s in self.sources if s.credibility_score >= 7])
            self.verified_count = len([s for s in self.sources if s.verified])
        else:
            self.average_credibility = 5.0
            self.average_relevance = 5.0
            self.total_sources = 0
            self.high_credibility_count = 0
            self.verified_count = 0
        
        return self

# Analysis Metadata Models
class AnalysisMetadata(BaseModel):
    """
    Metadata for analysis processes and results.
    
    Tracks the analysis pipeline, AI models used, confidence levels,
    and processing timestamps for transparency and auditability.
    """
    
    # Analysis process information
    analysis_id: str = Field(description="Unique analysis identifier")
    analysis_type: str = Field(description="Type of analysis performed")
    pipeline_version: str = Field(description="Analysis pipeline version")
    
    # AI model information
    primary_model: str = Field(description="Primary AI model used")
    research_model: Optional[str] = Field(default=None, description="Research model used if applicable")
    model_parameters: Dict[str, Any] = Field(default={}, description="Model parameters used")
    
    # Timing information
    started_at: datetime = Field(description="Analysis start time")
    completed_at: Optional[datetime] = Field(default=None, description="Analysis completion time")
    processing_duration: Optional[float] = Field(default=None, description="Processing duration in seconds")
    
    # Quality metrics
    confidence_score: float = Field(description="Overall analysis confidence (1-10)", ge=1, le=10)
    completeness_score: float = Field(description="Analysis completeness (1-10)", ge=1, le=10)
    source_coverage: float = Field(description="Source coverage adequacy (1-10)", ge=1, le=10)
    
    # Error tracking
    warnings: List[str] = Field(default=[], description="Analysis warnings")
    errors: List[str] = Field(default=[], description="Analysis errors")
    
    # User context
    client_name: Optional[str] = Field(default=None, description="Client name for analysis")
    user_id: Optional[str] = Field(default=None, description="User who initiated analysis")
    
    @model_validator(mode='after')
    def calculate_duration(self):
        """Calculate processing duration if not provided"""
        if self.processing_duration is None and self.completed_at and self.started_at:
            delta = self.completed_at - self.started_at
            self.processing_duration = delta.total_seconds()
        return self

class DetailLevel(str, Enum):
    """Progressive disclosure detail levels"""
    SUMMARY = "summary"      # Basic information only
    DETAIL = "detail"        # Extended information
    FULL = "full"           # Complete information with sources

# Progressive Disclosure Base Model
class ProgressiveDisclosureModel(BaseModel):
    """
    Base model for progressive disclosure functionality.
    
    Provides common fields and methods for models that support
    different levels of detail disclosure.
    """
    
    # Core identification
    id: Union[int, str] = Field(description="Unique identifier")
    
    # Progressive disclosure metadata
    detail_level: DetailLevel = Field(default=DetailLevel.SUMMARY, description="Current detail level")
    available_levels: List[DetailLevel] = Field(
        default=[DetailLevel.SUMMARY, DetailLevel.DETAIL, DetailLevel.FULL],
        description="Available detail levels"
    )
    
    # Source and metadata tracking
    source_collection: Optional[SourceCollection] = Field(default=None, description="Associated sources")
    analysis_metadata: Optional[AnalysisMetadata] = Field(default=None, description="Analysis metadata")
    
    # Lazy loading indicators
    has_detailed_analysis: bool = Field(default=False, description="Whether detailed analysis is available")
    has_source_analysis: bool = Field(default=False, description="Whether source analysis is available")

# Source Analysis Models
class SourceAnalysisResult(BaseModel):
    """
    Results of detailed source analysis.
    
    Provides insights into source quality, consensus, and reliability
    for a specific analysis or opportunity.
    """
    
    # Overall assessment
    overall_credibility: CredibilityLevel = Field(description="Overall source credibility assessment")
    source_consensus: float = Field(description="Level of consensus across sources (1-10)", ge=1, le=10)
    information_gaps: List[str] = Field(default=[], description="Identified information gaps")
    
    # Source breakdown
    source_type_distribution: Dict[str, int] = Field(description="Distribution of source types")
    credibility_distribution: Dict[str, int] = Field(description="Distribution of credibility levels")
    
    # Quality indicators
    has_primary_sources: bool = Field(description="Whether primary sources are included")
    has_recent_sources: bool = Field(description="Whether recent sources are included")
    geographic_coverage: List[str] = Field(default=[], description="Geographic regions covered")
    
    # Recommendations
    source_quality_score: float = Field(description="Overall source quality score (1-10)", ge=1, le=10)
    recommendations: List[str] = Field(default=[], description="Recommendations for improving source quality")

# Utility Functions
class SourceCredibilityCalculator:
    """Utility class for calculating source credibility scores"""
    
    # Domain credibility mappings
    HIGH_CREDIBILITY_DOMAINS = {
        'pubmed.ncbi.nlm.nih.gov': 9.5,
        'fda.gov': 9.5,
        'who.int': 9.0,
        'reuters.com': 8.5,
        'bloomberg.com': 8.5,
        'wsj.com': 8.5,
        'nature.com': 9.0,
        'nejm.org': 9.5,
        'sec.gov': 9.0
    }
    
    MEDIUM_CREDIBILITY_DOMAINS = {
        'cnn.com': 6.5,
        'bbc.com': 7.5,
        'forbes.com': 7.0,
        'techcrunch.com': 6.5,
        'medscape.com': 7.5
    }
    
    @classmethod
    def calculate_credibility_score(cls, url: str, source_type: SourceType, content: str = "") -> float:
        """
        Calculate credibility score based on URL, source type, and content analysis.
        
        Args:
            url: Source URL
            source_type: Type of source
            content: Source content for analysis
            
        Returns:
            Credibility score from 1-10
        """
        from urllib.parse import urlparse
        
        domain = urlparse(url).netloc.lower()
        
        # Base score from domain
        if domain in cls.HIGH_CREDIBILITY_DOMAINS:
            base_score = cls.HIGH_CREDIBILITY_DOMAINS[domain]
        elif domain in cls.MEDIUM_CREDIBILITY_DOMAINS:
            base_score = cls.MEDIUM_CREDIBILITY_DOMAINS[domain]
        else:
            # Default scoring based on source type
            type_scores = {
                SourceType.ACADEMIC_PAPER: 8.5,
                SourceType.REGULATORY_FILING: 9.0,
                SourceType.INDUSTRY_REPORT: 7.5,
                SourceType.NEWS_ARTICLE: 6.5,
                SourceType.COMPANY_WEBSITE: 6.0,
                SourceType.PRESS_RELEASE: 5.5,
                SourceType.BLOG_POST: 4.0,
                SourceType.SOCIAL_MEDIA: 3.0
            }
            base_score = type_scores.get(source_type, 5.0)
        
        # Content quality adjustments (simplified)
        content_adjustment = 0
        if content:
            # Boost for citations, data, specific numbers
            if any(indicator in content.lower() for indicator in ['study', 'research', 'data', '%', '$']):
                content_adjustment += 0.5
            
            # Reduce for opinion words
            if any(indicator in content.lower() for indicator in ['believe', 'think', 'opinion', 'rumor']):
                content_adjustment -= 0.5
        
        final_score = max(1.0, min(10.0, base_score + content_adjustment))
        return round(final_score, 1)
    
    @classmethod
    def calculate_relevance_score(cls, content: str, query_terms: List[str]) -> float:
        """
        Calculate relevance score based on content and query terms.
        
        Args:
            content: Source content
            query_terms: Terms to match against
            
        Returns:
            Relevance score from 1-10
        """
        if not content or not query_terms:
            return 5.0
        
        content_lower = content.lower()
        matches = sum(1 for term in query_terms if term.lower() in content_lower)
        match_ratio = matches / len(query_terms)
        
        # Convert ratio to 1-10 scale
        relevance_score = 1 + (match_ratio * 9)
        return round(relevance_score, 1) 