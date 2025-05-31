"""
Enhanced Source Models for Progressive Disclosure System

Provides comprehensive source tracking, credibility analysis, and metadata
preservation throughout the LangGraph analysis pipeline.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, HttpUrl, validator, model_validator
from datetime import datetime
from enum import Enum

# Source Type Classifications
class SourceType(str, Enum):
    """Types of sources for credibility assessment"""
    ACADEMIC = "academic"
    INDUSTRY_REPORT = "industry_report"
    NEWS_ARTICLE = "news_article"
    COMPANY_WEBSITE = "company_website"
    REGULATORY = "regulatory"
    BLOG = "blog"
    UNKNOWN = "unknown"

class CredibilityLevel(str, Enum):
    """Source credibility levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"

class RelevanceLevel(str, Enum):
    """Content relevance levels"""
    HIGHLY_RELEVANT = "Highly Relevant"    # 9-10: Direct match
    RELEVANT = "Relevant"                  # 7-8: Strong connection
    SOMEWHAT_RELEVANT = "Somewhat Relevant" # 5-6: Partial match
    MARGINALLY_RELEVANT = "Marginally Relevant" # 3-4: Weak connection
    NOT_RELEVANT = "Not Relevant"          # 1-2: No clear connection

class DetailLevel(str, Enum):
    """Progressive disclosure detail levels"""
    SUMMARY = "summary"      # OpportunitySummary - Essential info only
    DETAIL = "detail"        # OpportunityDetail - Expanded information
    FULL = "full"           # OpportunityFull - Complete analysis

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
                self.credibility_level = CredibilityLevel.HIGH
            elif score >= 5:
                self.credibility_level = CredibilityLevel.MEDIUM
            elif score >= 3:
                self.credibility_level = CredibilityLevel.LOW
            else:
                self.credibility_level = CredibilityLevel.UNKNOWN
        
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
    Metadata about the analysis process for transparency and traceability.
    
    Documents how AI agents processed data through each LangGraph node
    to provide complete methodology transparency.
    """
    
    # Analysis context
    client_name: str = Field(description="Client name for this analysis")
    competitors_analyzed: List[str] = Field(description="List of competitors analyzed")
    device_category: str = Field(description="Medical device category")
    analysis_timestamp: datetime = Field(default_factory=datetime.now, description="When analysis was performed")
    
    # Search methodology
    total_searches_performed: int = Field(description="Total number of Tavily searches")
    unique_queries_used: List[str] = Field(description="All unique search queries used")
    search_strategy: str = Field(description="Description of search strategy employed")
    
    # Processing pipeline
    langgraph_nodes_executed: List[str] = Field(description="LangGraph nodes that were executed")
    processing_duration: Optional[float] = Field(default=None, description="Total processing time in seconds")
    ai_model_used: str = Field(default="gpt-4", description="AI model used for analysis")
    
    # Quality metrics
    overall_confidence: float = Field(description="Overall analysis confidence (1-10)", ge=1, le=10)
    source_quality_score: float = Field(description="Aggregated source quality score (1-10)", ge=1, le=10)
    analysis_completeness: float = Field(description="Completeness of analysis (1-10)", ge=1, le=10)
    
    # Methodology documentation
    gap_analysis_method: str = Field(description="Method used for competitive gap analysis")
    opportunity_generation_method: str = Field(description="Method used for opportunity generation")
    prioritization_criteria: List[str] = Field(description="Criteria used for opportunity prioritization")

# Source Analysis Models
class SourceAnalysisResult(BaseModel):
    """
    Comprehensive analysis result for a collection of sources.
    
    Provides aggregated insights about source quality, credibility,
    and relevance for progressive disclosure display.
    """
    
    # Source collection metadata
    total_sources: int = Field(description="Total number of sources analyzed")
    unique_domains: int = Field(description="Number of unique domains")
    search_queries_used: List[str] = Field(description="All search queries that generated these sources")
    
    # Quality metrics
    average_credibility: float = Field(description="Average credibility score", ge=1, le=10)
    average_relevance: float = Field(description="Average relevance score", ge=1, le=10)
    credibility_distribution: Dict[str, int] = Field(description="Count by credibility level")
    source_type_distribution: Dict[str, int] = Field(description="Count by source type")
    
    # Top sources
    highest_credibility_sources: List[SourceCitation] = Field(description="Top 3 most credible sources")
    most_relevant_sources: List[SourceCitation] = Field(description="Top 3 most relevant sources")
    
    # Analysis insights
    key_domains: List[str] = Field(description="Most frequently cited domains")
    coverage_assessment: str = Field(description="Assessment of topic coverage")
    reliability_assessment: str = Field(description="Overall reliability assessment")
    
    # Progressive disclosure helpers
    credibility_indicator: str = Field(description="Visual credibility indicator (🟢🟡🔴)")
    source_count_display: str = Field(description="Human-readable source count")
    quality_summary: str = Field(description="Brief quality summary for display")

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
                SourceType.ACADEMIC: 9.0,
                SourceType.REGULATORY: 9.5,
                SourceType.INDUSTRY_REPORT: 7.5,
                SourceType.NEWS_ARTICLE: 6.5,
                SourceType.COMPANY_WEBSITE: 5.5,
                SourceType.BLOG: 3.0,
                SourceType.UNKNOWN: 5.0
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

class TavilySourceMetadata(BaseModel):
    """
    Enhanced metadata for Tavily search results with full traceability.
    
    Captures all relevant information from Tavily searches to enable
    complete source traceability through the analysis pipeline.
    """
    
    # Core Tavily data
    url: str = Field(description="Source URL from Tavily")
    title: str = Field(description="Source title from Tavily")
    content: str = Field(description="Content snippet from Tavily")
    tavily_score: float = Field(description="Tavily relevance score", ge=0, le=1)
    
    # Search context
    search_query: str = Field(description="Original search query used")
    competitor: str = Field(description="Competitor being researched")
    search_timestamp: datetime = Field(default_factory=datetime.now, description="When search was performed")
    
    # Enhanced metadata
    domain: str = Field(description="Extracted domain name")
    source_type: SourceType = Field(default=SourceType.UNKNOWN, description="Classified source type")
    credibility_level: CredibilityLevel = Field(default=CredibilityLevel.UNKNOWN, description="Assessed credibility")
    credibility_score: float = Field(default=5.0, description="Numerical credibility score (1-10)", ge=1, le=10)
    
    # Content analysis
    content_length: int = Field(description="Length of content snippet")
    relevance_score: float = Field(default=7.0, description="Assessed relevance to query (1-10)", ge=1, le=10)
    key_topics: List[str] = Field(default=[], description="Extracted key topics from content")
    
    # Processing metadata
    processed_at: datetime = Field(default_factory=datetime.now, description="When metadata was processed")
    analysis_notes: Optional[str] = Field(default=None, description="Additional analysis notes")

class OpportunitySourceLink(BaseModel):
    """
    Links opportunities to their supporting sources with analysis context.
    
    Enables complete traceability from opportunities back to original
    Tavily search results and analysis methodology.
    """
    
    opportunity_id: int = Field(description="ID of the opportunity")
    supporting_sources: List[TavilySourceMetadata] = Field(description="Sources supporting this opportunity")
    primary_source: Optional[TavilySourceMetadata] = Field(default=None, description="Primary/strongest supporting source")
    
    # Analysis methodology
    analysis_method: str = Field(description="How this opportunity was derived from sources")
    confidence_reasoning: str = Field(description="Reasoning for confidence level")
    key_evidence_points: List[str] = Field(description="Key evidence points from sources")
    
    # Source utilization
    sources_used_count: int = Field(description="Number of sources actually used in analysis")
    sources_available_count: int = Field(description="Total sources available for this competitor/topic")
    source_coverage_percentage: float = Field(description="Percentage of available sources utilized", ge=0, le=100)

class SourceCollectionAnalyzer:
    """
    Analyzer for collections of sources to generate aggregate insights.
    
    Provides methods for analyzing multiple sources together and generating
    comprehensive source analysis results for progressive disclosure.
    """
    
    @staticmethod
    def analyze_source_collection(sources: List[TavilySourceMetadata]) -> SourceAnalysisResult:
        """
        Analyze a collection of sources and generate comprehensive insights.
        
        Args:
            sources: List of source metadata objects
            
        Returns:
            SourceAnalysisResult: Comprehensive analysis of the source collection
        """
        if not sources:
            return SourceAnalysisResult(
                total_sources=0,
                unique_domains=0,
                search_queries_used=[],
                average_credibility=5.0,
                average_relevance=5.0,
                credibility_distribution={},
                source_type_distribution={},
                highest_credibility_sources=[],
                most_relevant_sources=[],
                key_domains=[],
                coverage_assessment="No sources available",
                reliability_assessment="Cannot assess - no sources",
                credibility_indicator="⚪",
                source_count_display="No sources",
                quality_summary="No source data available"
            )
        
        # Basic metrics
        total_sources = len(sources)
        unique_domains = len(set(source.domain for source in sources))
        search_queries = list(set(source.search_query for source in sources))
        
        # Quality metrics
        avg_credibility = sum(source.credibility_score for source in sources) / total_sources
        avg_relevance = sum(source.relevance_score for source in sources) / total_sources
        
        # Distributions
        credibility_dist = {}
        source_type_dist = {}
        
        for source in sources:
            cred_level = source.credibility_level.value
            credibility_dist[cred_level] = credibility_dist.get(cred_level, 0) + 1
            
            source_type = source.source_type.value
            source_type_dist[source_type] = source_type_dist.get(source_type, 0) + 1
        
        # Top sources
        highest_cred = sorted(sources, key=lambda x: x.credibility_score, reverse=True)[:3]
        most_relevant = sorted(sources, key=lambda x: x.relevance_score, reverse=True)[:3]
        
        # Key domains
        domain_counts = {}
        for source in sources:
            domain_counts[source.domain] = domain_counts.get(source.domain, 0) + 1
        key_domains = sorted(domain_counts.keys(), key=lambda x: domain_counts[x], reverse=True)[:5]
        
        # Assessments
        coverage_assessment = SourceCollectionAnalyzer._assess_coverage(sources, source_type_dist)
        reliability_assessment = SourceCollectionAnalyzer._assess_reliability(avg_credibility, credibility_dist)
        
        # Progressive disclosure helpers
        credibility_indicator = SourceCollectionAnalyzer._get_credibility_indicator(avg_credibility)
        source_count_display = SourceCollectionAnalyzer._get_source_count_display(total_sources)
        quality_summary = SourceCollectionAnalyzer._get_quality_summary(avg_credibility, total_sources)
        
        return SourceAnalysisResult(
            total_sources=total_sources,
            unique_domains=unique_domains,
            search_queries_used=search_queries,
            average_credibility=avg_credibility,
            average_relevance=avg_relevance,
            credibility_distribution=credibility_dist,
            source_type_distribution=source_type_dist,
            highest_credibility_sources=highest_cred,
            most_relevant_sources=most_relevant,
            key_domains=key_domains,
            coverage_assessment=coverage_assessment,
            reliability_assessment=reliability_assessment,
            credibility_indicator=credibility_indicator,
            source_count_display=source_count_display,
            quality_summary=quality_summary
        )
    
    @staticmethod
    def _assess_coverage(sources: List[TavilySourceMetadata], source_type_dist: Dict[str, int]) -> str:
        """Assess topic coverage based on source diversity."""
        if len(source_type_dist) >= 3:
            return "Comprehensive coverage across multiple source types"
        elif len(source_type_dist) == 2:
            return "Good coverage with moderate source diversity"
        else:
            return "Limited coverage - single source type"
    
    @staticmethod
    def _assess_reliability(avg_credibility: float, credibility_dist: Dict[str, int]) -> str:
        """Assess overall reliability based on credibility metrics."""
        high_cred_count = credibility_dist.get("high", 0)
        total_sources = sum(credibility_dist.values())
        
        if avg_credibility >= 8.0 and high_cred_count / total_sources >= 0.5:
            return "High reliability - predominantly high-credibility sources"
        elif avg_credibility >= 6.5:
            return "Good reliability - mix of credible sources"
        elif avg_credibility >= 5.0:
            return "Moderate reliability - verify key claims"
        else:
            return "Low reliability - use with caution"
    
    @staticmethod
    def _get_credibility_indicator(avg_credibility: float) -> str:
        """Get visual credibility indicator."""
        if avg_credibility >= 8.0:
            return "🟢"
        elif avg_credibility >= 6.0:
            return "🟡"
        else:
            return "🔴"
    
    @staticmethod
    def _get_source_count_display(total_sources: int) -> str:
        """Get human-readable source count display."""
        if total_sources == 0:
            return "No sources"
        elif total_sources == 1:
            return "1 source"
        elif total_sources <= 5:
            return f"{total_sources} sources"
        else:
            return f"{total_sources} sources (comprehensive)"
    
    @staticmethod
    def _get_quality_summary(avg_credibility: float, total_sources: int) -> str:
        """Get brief quality summary for display."""
        quality_level = "High" if avg_credibility >= 8.0 else "Good" if avg_credibility >= 6.0 else "Moderate"
        return f"{quality_level} quality • {total_sources} sources"

# Source Analysis Utilities
class SourceAnalyzer:
    """
    Utility class for analyzing and scoring sources from Tavily results.
    
    Provides methods for credibility assessment, relevance scoring,
    and metadata extraction from raw Tavily data.
    """
    
    @staticmethod
    def analyze_tavily_result(
        result: Dict[str, Any], 
        query: str, 
        competitor: str
    ) -> TavilySourceMetadata:
        """
        Convert raw Tavily result to enhanced source metadata.
        
        Args:
            result: Raw result from Tavily search
            query: Search query used
            competitor: Competitor being researched
            
        Returns:
            TavilySourceMetadata: Enhanced metadata object
        """
        url = result.get("url", "")
        title = result.get("title", "")
        content = result.get("content", "")
        tavily_score = result.get("score", 0.5)
        
        # Extract domain
        domain = SourceAnalyzer.extract_domain(url)
        
        # Assess source type and credibility
        source_type = SourceAnalyzer.classify_source_type(domain, title, content)
        credibility_level = SourceAnalyzer.assess_credibility_level(domain, source_type)
        credibility_score = SourceAnalyzer.calculate_credibility_score(domain, source_type, tavily_score)
        
        # Calculate relevance
        relevance_score = SourceAnalyzer.calculate_relevance_score(content, query, competitor)
        
        # Extract key topics
        key_topics = SourceAnalyzer.extract_key_topics(content, competitor)
        
        return TavilySourceMetadata(
            url=url,
            title=title,
            content=content,
            tavily_score=tavily_score,
            search_query=query,
            competitor=competitor,
            domain=domain,
            source_type=source_type,
            credibility_level=credibility_level,
            credibility_score=credibility_score,
            content_length=len(content),
            relevance_score=relevance_score,
            key_topics=key_topics
        )
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """Extract clean domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            return domain if domain else url
        except:
            return url
    
    @staticmethod
    def classify_source_type(domain: str, title: str, content: str) -> SourceType:
        """Classify source type based on domain and content."""
        domain_lower = domain.lower()
        title_lower = title.lower()
        content_lower = content.lower()
        
        # Academic sources
        academic_indicators = ['pubmed', 'ncbi', 'nature.com', 'science.org', 'nejm.org', 'thelancet.com', '.edu']
        if any(indicator in domain_lower for indicator in academic_indicators):
            return SourceType.ACADEMIC
        
        # Regulatory sources
        regulatory_indicators = ['fda.gov', 'who.int', 'ema.europa.eu', 'health.gov']
        if any(indicator in domain_lower for indicator in regulatory_indicators):
            return SourceType.REGULATORY
        
        # Industry reports
        industry_indicators = ['massdevice', 'medtechdive', 'devicetalks', 'medicaldevice', 'report', 'market research']
        if any(indicator in domain_lower for indicator in industry_indicators) or 'report' in title_lower:
            return SourceType.INDUSTRY_REPORT
        
        # News articles
        news_indicators = ['reuters', 'bloomberg', 'wsj', 'ft.com', 'cnn', 'bbc', 'news']
        if any(indicator in domain_lower for indicator in news_indicators) or 'news' in title_lower:
            return SourceType.NEWS_ARTICLE
        
        # Company websites
        company_indicators = ['.com', 'about', 'company', 'corporate']
        if any(indicator in domain_lower for indicator in company_indicators) and 'blog' not in domain_lower:
            return SourceType.COMPANY_WEBSITE
        
        # Blogs
        blog_indicators = ['blog', 'wordpress', 'medium.com', 'linkedin.com']
        if any(indicator in domain_lower for indicator in blog_indicators):
            return SourceType.BLOG
        
        return SourceType.UNKNOWN
    
    @staticmethod
    def assess_credibility_level(domain: str, source_type: SourceType) -> CredibilityLevel:
        """Assess credibility level based on domain and source type."""
        domain_lower = domain.lower()
        
        # High credibility domains
        high_credibility = {
            'pubmed.ncbi.nlm.nih.gov', 'ncbi.nlm.nih.gov', 'fda.gov', 'who.int',
            'reuters.com', 'bloomberg.com', 'wsj.com', 'ft.com',
            'nature.com', 'science.org', 'nejm.org', 'thelancet.com'
        }
        
        if domain_lower in high_credibility or source_type in [SourceType.ACADEMIC, SourceType.REGULATORY]:
            return CredibilityLevel.HIGH
        
        # Medium credibility
        if source_type in [SourceType.INDUSTRY_REPORT, SourceType.NEWS_ARTICLE]:
            return CredibilityLevel.MEDIUM
        
        # Low credibility
        if source_type == SourceType.BLOG:
            return CredibilityLevel.LOW
        
        return CredibilityLevel.UNKNOWN
    
    @staticmethod
    def calculate_credibility_score(domain: str, source_type: SourceType, tavily_score: float) -> float:
        """Calculate numerical credibility score."""
        base_scores = {
            SourceType.ACADEMIC: 9.0,
            SourceType.REGULATORY: 9.5,
            SourceType.INDUSTRY_REPORT: 7.0,
            SourceType.NEWS_ARTICLE: 6.5,
            SourceType.COMPANY_WEBSITE: 5.5,
            SourceType.BLOG: 3.0,
            SourceType.UNKNOWN: 5.0
        }
        
        base_score = base_scores.get(source_type, 5.0)
        
        # Adjust based on Tavily score
        tavily_adjustment = (tavily_score - 0.5) * 2  # Scale -1 to +1
        
        final_score = base_score + tavily_adjustment
        return max(1.0, min(10.0, final_score))
    
    @staticmethod
    def calculate_relevance_score(content: str, query: str, competitor: str) -> float:
        """Calculate relevance score based on content analysis."""
        content_lower = content.lower()
        query_lower = query.lower()
        competitor_lower = competitor.lower()
        
        score = 5.0  # Base score
        
        # Check for competitor mention
        if competitor_lower in content_lower:
            score += 2.0
        
        # Check for query terms
        query_terms = query_lower.split()
        matching_terms = sum(1 for term in query_terms if term in content_lower)
        score += (matching_terms / len(query_terms)) * 2.0
        
        # Check content length (longer content often more relevant)
        if len(content) > 200:
            score += 1.0
        
        return max(1.0, min(10.0, score))
    
    @staticmethod
    def extract_key_topics(content: str, competitor: str) -> List[str]:
        """Extract key topics from content."""
        # Simple keyword extraction - could be enhanced with NLP
        medical_keywords = [
            'clinical', 'trial', 'fda', 'approval', 'device', 'surgical', 
            'patient', 'treatment', 'therapy', 'innovation', 'technology',
            'market', 'revenue', 'growth', 'competition', 'strategy'
        ]
        
        content_lower = content.lower()
        found_topics = [keyword for keyword in medical_keywords if keyword in content_lower]
        
        # Add competitor name if mentioned
        if competitor.lower() in content_lower:
            found_topics.append(competitor)
        
        return found_topics[:5]  # Limit to top 5 topics

# Analysis Methodology Tracking Models
class LangGraphNodeExecution(BaseModel):
    """
    Tracks execution details for individual LangGraph nodes.
    
    Provides transparency into how each node processes data and contributes
    to the final analysis results.
    """
    
    node_name: str = Field(description="Name of the LangGraph node")
    execution_order: int = Field(description="Order in which this node was executed")
    started_at: datetime = Field(description="When node execution started")
    completed_at: Optional[datetime] = Field(default=None, description="When node execution completed")
    
    # Input/Output tracking
    input_data_summary: str = Field(description="Summary of input data received")
    output_data_summary: Optional[str] = Field(default=None, description="Summary of output data produced")
    data_transformations: List[str] = Field(default=[], description="List of data transformations performed")
    
    # Processing details
    queries_executed: List[str] = Field(default=[], description="Search queries or prompts executed")
    ai_prompts_used: List[str] = Field(default=[], description="AI prompts used in this node")
    processing_duration: Optional[float] = Field(default=None, description="Processing time in seconds")
    
    # Quality metrics
    success_indicators: List[str] = Field(default=[], description="Indicators of successful processing")
    quality_checks_performed: List[str] = Field(default=[], description="Quality checks performed")
    confidence_factors: List[str] = Field(default=[], description="Factors contributing to confidence")
    
    # Error handling
    warnings_generated: List[str] = Field(default=[], description="Warnings generated during execution")
    error_handling_applied: List[str] = Field(default=[], description="Error handling strategies applied")
    
    # Source tracking
    sources_consumed: List[str] = Field(default=[], description="Sources consumed by this node")
    sources_produced: List[str] = Field(default=[], description="Sources produced or enhanced by this node")
    
    @property
    def execution_duration(self) -> Optional[float]:
        """Calculate execution duration if both timestamps are available"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

class AnalysisMethodology(BaseModel):
    """
    Comprehensive analysis methodology documentation.
    
    Captures the complete methodology used for competitive intelligence analysis,
    including search strategies, data processing approaches, and reasoning chains.
    """
    
    # Analysis approach
    methodology_name: str = Field(description="Name/type of analysis methodology used")
    methodology_version: str = Field(default="1.0", description="Version of the methodology")
    analysis_framework: str = Field(description="Analytical framework applied (e.g., 'competitive_gap_analysis')")
    
    # Search strategy
    search_strategy: Dict[str, Any] = Field(description="Comprehensive search strategy details")
    query_generation_approach: str = Field(description="How search queries were generated")
    source_selection_criteria: List[str] = Field(description="Criteria for selecting and prioritizing sources")
    
    # Data processing
    data_processing_pipeline: List[str] = Field(description="Steps in the data processing pipeline")
    content_analysis_method: str = Field(description="Method used for analyzing content")
    gap_identification_approach: str = Field(description="Approach for identifying competitive gaps")
    
    # Opportunity generation
    opportunity_discovery_method: str = Field(description="Method for discovering opportunities")
    prioritization_algorithm: str = Field(description="Algorithm/criteria for prioritizing opportunities")
    scoring_methodology: str = Field(description="How opportunity scores were calculated")
    
    # Quality assurance
    validation_steps: List[str] = Field(description="Steps taken to validate findings")
    bias_mitigation_strategies: List[str] = Field(description="Strategies to mitigate analysis bias")
    confidence_assessment_method: str = Field(description="How confidence levels were assessed")
    
    # Limitations and assumptions
    known_limitations: List[str] = Field(default=[], description="Known limitations of the analysis")
    key_assumptions: List[str] = Field(default=[], description="Key assumptions made during analysis")
    uncertainty_factors: List[str] = Field(default=[], description="Factors contributing to uncertainty")

class ComprehensiveAnalysisMetadata(AnalysisMetadata):
    """
    Extended analysis metadata with comprehensive methodology tracking.
    
    Builds upon the base AnalysisMetadata to include detailed methodology
    documentation and node-by-node execution tracking.
    """
    
    # Methodology documentation
    methodology: AnalysisMethodology = Field(description="Detailed analysis methodology")
    node_executions: List[LangGraphNodeExecution] = Field(default=[], description="Execution details for each LangGraph node")
    
    # Enhanced search tracking
    total_searches_executed: int = Field(description="Total number of search queries executed")
    unique_competitors_researched: int = Field(description="Number of unique competitors researched")
    search_query_categories: Dict[str, int] = Field(description="Breakdown of query types used")
    
    # Source utilization analysis
    total_sources_analyzed: int = Field(description="Total number of sources analyzed")
    high_quality_sources_count: int = Field(description="Number of high-quality sources (credibility >= 8)")
    source_diversity_score: float = Field(description="Diversity score of source types (1-10)", ge=1, le=10)
    
    # Processing performance
    total_processing_time: float = Field(description="Total analysis processing time in seconds")
    ai_model_interactions: int = Field(description="Total number of AI model interactions")
    data_transformation_steps: int = Field(description="Number of data transformation steps")
    
    # Quality indicators
    analysis_completeness_indicators: List[str] = Field(description="Indicators of analysis completeness")
    cross_validation_results: List[str] = Field(default=[], description="Results of cross-validation checks")
    peer_review_notes: List[str] = Field(default=[], description="Peer review notes if applicable")
    
    # Traceability
    decision_audit_trail: List[Dict[str, Any]] = Field(default=[], description="Audit trail of key decisions")
    reasoning_chains: List[Dict[str, Any]] = Field(default=[], description="Documented reasoning chains")
    
    def add_node_execution(self, node_execution: LangGraphNodeExecution):
        """Add a node execution record"""
        self.node_executions.append(node_execution)
        
        # Update aggregate metrics
        if node_execution.execution_duration:
            self.total_processing_time += node_execution.execution_duration
        
        self.ai_model_interactions += len(node_execution.ai_prompts_used)
        self.data_transformation_steps += len(node_execution.data_transformations)
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get a summary of the execution process"""
        return {
            "total_nodes_executed": len(self.node_executions),
            "total_processing_time": self.total_processing_time,
            "average_node_duration": self.total_processing_time / len(self.node_executions) if self.node_executions else 0,
            "most_time_consuming_node": max(self.node_executions, key=lambda x: x.execution_duration or 0).node_name if self.node_executions else None,
            "total_queries_executed": sum(len(node.queries_executed) for node in self.node_executions),
            "total_ai_interactions": self.ai_model_interactions,
            "methodology_version": self.methodology.methodology_version,
            "analysis_framework": self.methodology.analysis_framework
        }
    
    def get_methodology_transparency_report(self) -> Dict[str, Any]:
        """Generate a transparency report for the analysis methodology"""
        return {
            "search_strategy": {
                "approach": self.methodology.query_generation_approach,
                "total_queries": self.total_searches_executed,
                "query_categories": self.search_query_categories,
                "source_selection": self.methodology.source_selection_criteria
            },
            "data_processing": {
                "pipeline_steps": self.methodology.data_processing_pipeline,
                "content_analysis": self.methodology.content_analysis_method,
                "transformations": self.data_transformation_steps
            },
            "opportunity_generation": {
                "discovery_method": self.methodology.opportunity_discovery_method,
                "scoring_method": self.methodology.scoring_methodology,
                "prioritization": self.methodology.prioritization_algorithm
            },
            "quality_assurance": {
                "validation_steps": self.methodology.validation_steps,
                "bias_mitigation": self.methodology.bias_mitigation_strategies,
                "confidence_assessment": self.methodology.confidence_assessment_method
            },
            "limitations": {
                "known_limitations": self.methodology.known_limitations,
                "key_assumptions": self.methodology.key_assumptions,
                "uncertainty_factors": self.methodology.uncertainty_factors
            }
        }

class MethodologyTracker:
    """
    Utility class for tracking analysis methodology throughout the LangGraph pipeline.
    
    Provides methods for recording node executions, capturing methodology details,
    and generating transparency reports.
    """
    
    def __init__(self, client_name: str, competitors: List[str], device_category: str):
        """Initialize methodology tracker"""
        self.metadata = ComprehensiveAnalysisMetadata(
            client_name=client_name,
            competitors_analyzed=competitors,
            device_category=device_category,
            analysis_timestamp=datetime.now(),
            total_searches_performed=0,
            unique_queries_used=[],
            search_strategy="Multi-layered competitive intelligence approach",
            langgraph_nodes_executed=[],
            processing_duration=0.0,
            ai_model_used="gpt-4",
            overall_confidence=7.5,
            source_quality_score=7.0,
            analysis_completeness=8.0,
            gap_analysis_method="AI-enhanced competitive gap analysis",
            opportunity_generation_method="Evidence-based opportunity synthesis",
            prioritization_criteria=["Market impact", "Implementation feasibility", "Competitive advantage"],
            methodology=AnalysisMethodology(
                methodology_name="Enhanced Competitive Intelligence Framework",
                analysis_framework="competitive_gap_opportunity_analysis",
                search_strategy={
                    "approach": "multi_dimensional",
                    "competitor_focus": True,
                    "opportunity_discovery": True,
                    "source_diversification": True
                },
                query_generation_approach="Category-aware dynamic query generation",
                source_selection_criteria=[
                    "Credibility assessment (domain authority, source type)",
                    "Relevance scoring (content-query alignment)",
                    "Recency weighting (publication date)",
                    "Source diversity (multiple perspectives)"
                ],
                data_processing_pipeline=[
                    "Raw data ingestion from Tavily",
                    "Source metadata enhancement",
                    "Content analysis and extraction",
                    "Competitive gap identification",
                    "Opportunity synthesis",
                    "Scoring and prioritization"
                ],
                content_analysis_method="AI-enhanced semantic analysis with human-defined frameworks",
                gap_identification_approach="Comparative analysis across multiple dimensions (clinical, market, product, brand)",
                opportunity_discovery_method="Gap-to-opportunity transformation with business impact assessment",
                prioritization_algorithm="Multi-factor scoring (impact × feasibility × confidence)",
                scoring_methodology="Weighted composite scoring with credibility and market factors",
                validation_steps=[
                    "Source credibility verification",
                    "Cross-reference validation",
                    "Logical consistency checks",
                    "Business feasibility assessment"
                ],
                bias_mitigation_strategies=[
                    "Multiple source validation",
                    "Diverse query perspectives",
                    "Structured analytical frameworks",
                    "Confidence uncertainty tracking"
                ],
                confidence_assessment_method="Multi-factor confidence scoring based on source quality, analysis depth, and validation results"
            ),
            total_searches_executed=0,
            unique_competitors_researched=len(competitors),
            search_query_categories={},
            total_sources_analyzed=0,
            high_quality_sources_count=0,
            source_diversity_score=7.0,
            total_processing_time=0.0,
            ai_model_interactions=0,
            data_transformation_steps=0,
            analysis_completeness_indicators=[],
            cross_validation_results=[],
            peer_review_notes=[],
            decision_audit_trail=[],
            reasoning_chains=[]
        )
        self.current_node_start_time = None
    
    def start_node_execution(self, node_name: str, input_summary: str) -> LangGraphNodeExecution:
        """Start tracking a node execution"""
        self.current_node_start_time = datetime.now()
        
        node_execution = LangGraphNodeExecution(
            node_name=node_name,
            execution_order=len(self.metadata.node_executions) + 1,
            started_at=self.current_node_start_time,
            input_data_summary=input_summary
        )
        
        return node_execution
    
    def complete_node_execution(
        self, 
        node_execution: LangGraphNodeExecution,
        output_summary: str,
        transformations: List[str] = None,
        queries: List[str] = None,
        ai_prompts: List[str] = None,
        sources_consumed: List[str] = None,
        success_indicators: List[str] = None,
        warnings: List[str] = None
    ):
        """Complete a node execution and add to metadata"""
        node_execution.completed_at = datetime.now()
        node_execution.output_data_summary = output_summary
        
        if transformations:
            node_execution.data_transformations.extend(transformations)
        if queries:
            node_execution.queries_executed.extend(queries)
            self.metadata.total_searches_executed += len(queries)
            self.metadata.unique_queries_used.extend(queries)
        if ai_prompts:
            node_execution.ai_prompts_used.extend(ai_prompts)
        if sources_consumed:
            node_execution.sources_consumed.extend(sources_consumed)
        if success_indicators:
            node_execution.success_indicators.extend(success_indicators)
        if warnings:
            node_execution.warnings_generated.extend(warnings)
        
        # Add to metadata
        self.metadata.add_node_execution(node_execution)
        
        # Update aggregate tracking
        self.metadata.langgraph_nodes_executed.append(node_execution.node_name)
    
    def record_decision(self, decision_point: str, reasoning: str, alternatives_considered: List[str]):
        """Record a key decision in the audit trail"""
        decision_record = {
            "timestamp": datetime.now().isoformat(),
            "decision_point": decision_point,
            "reasoning": reasoning,
            "alternatives_considered": alternatives_considered,
            "node_context": self.metadata.node_executions[-1].node_name if self.metadata.node_executions else "unknown"
        }
        self.metadata.decision_audit_trail.append(decision_record)
    
    def record_reasoning_chain(self, premise: str, reasoning_steps: List[str], conclusion: str):
        """Record a reasoning chain for transparency"""
        reasoning_record = {
            "timestamp": datetime.now().isoformat(),
            "premise": premise,
            "reasoning_steps": reasoning_steps,
            "conclusion": conclusion,
            "confidence_factors": [],
            "node_context": self.metadata.node_executions[-1].node_name if self.metadata.node_executions else "unknown"
        }
        self.metadata.reasoning_chains.append(reasoning_record)
    
    def update_source_metrics(self, sources_analyzed: int, high_quality_count: int, diversity_score: float):
        """Update source analysis metrics"""
        self.metadata.total_sources_analyzed += sources_analyzed
        self.metadata.high_quality_sources_count += high_quality_count
        self.metadata.source_diversity_score = diversity_score
    
    def finalize_analysis(self) -> ComprehensiveAnalysisMetadata:
        """Finalize the analysis and return complete metadata"""
        # Calculate final metrics
        if self.metadata.node_executions:
            self.metadata.processing_duration = sum(
                node.execution_duration or 0 for node in self.metadata.node_executions
            )
        
        # Remove duplicate queries
        self.metadata.unique_queries_used = list(set(self.metadata.unique_queries_used))
        
        # Set completeness indicators
        self.metadata.analysis_completeness_indicators = [
            f"Executed {len(self.metadata.node_executions)} LangGraph nodes",
            f"Analyzed {self.metadata.total_sources_analyzed} sources",
            f"Performed {self.metadata.total_searches_executed} searches",
            f"Generated {len(self.metadata.reasoning_chains)} reasoning chains",
            f"Recorded {len(self.metadata.decision_audit_trail)} key decisions"
        ]
        
        return self.metadata 

# Progressive Disclosure Base Models
class ProgressiveDisclosureModel(BaseModel):
    """
    Base model for progressive disclosure functionality.
    
    Provides common fields and methods for displaying information
    at different levels of detail (summary, detail, full).
    Enhanced with real source integration and methodology transparency.
    """
    
    # Core source integration
    source_collection: Optional["SourceCollection"] = Field(
        default=None, 
        description="Collection of supporting sources with credibility analysis"
    )
    
    # Analysis methodology integration  
    analysis_metadata: Optional["AnalysisMetadata"] = Field(
        default=None,
        description="Metadata about the analysis process for transparency"
    )
    
    # Progressive disclosure control
    detail_level: DetailLevel = Field(
        default=DetailLevel.SUMMARY,
        description="Current detail level for progressive disclosure"
    )
    
    # Quality indicators (computed from real data)
    overall_quality_score: float = Field(
        default=7.0, 
        description="Overall quality score based on sources and methodology (1-10)",
        ge=1, le=10
    )
    
    # Display helpers (computed from real analysis data)
    has_enhanced_data: bool = Field(
        default=False,
        description="Whether enhanced source and methodology data is available"
    )
    
    enhanced_data_types: List[str] = Field(
        default_factory=list,
        description="Types of enhanced data available (e.g., 'sources', 'methodology', 'traceability')"
    )
    
    @model_validator(mode='after')
    def set_progressive_disclosure_fields(self):
        """Set progressive disclosure fields based on available data"""
        
        # Check for enhanced data availability
        enhanced_types = []
        
        if self.source_collection and self.source_collection.sources:
            enhanced_types.append("sources")
            enhanced_types.append("source_analysis")
        
        if self.analysis_metadata:
            enhanced_types.append("methodology")
            if hasattr(self.analysis_metadata, 'langgraph_nodes_executed'):
                enhanced_types.append("execution_trace")
        
        self.enhanced_data_types = enhanced_types
        self.has_enhanced_data = len(enhanced_types) > 0
        
        # Calculate overall quality score from real data
        quality_factors = []
        
        # Source quality factor
        if self.source_collection and self.source_collection.sources:
            source_quality = self.source_collection.average_credibility or 5.0
            quality_factors.append(source_quality)
        
        # Methodology quality factor
        if self.analysis_metadata:
            methodology_quality = getattr(self.analysis_metadata, 'overall_confidence', 7.0)
            quality_factors.append(methodology_quality)
        
        # Calculate overall quality
        if quality_factors:
            self.overall_quality_score = sum(quality_factors) / len(quality_factors)
        else:
            self.overall_quality_score = 7.0  # Default for opportunities without enhanced data
        
        return self
    
    def get_quality_indicators(self) -> Dict[str, Any]:
        """Get quality indicators for display"""
        # Source quality
        source_quality = "⚪"
        source_count = 0
        if self.source_collection and self.source_collection.sources:
            avg_credibility = self.source_collection.average_credibility or 5.0
            source_count = len(self.source_collection.sources)
            
            if avg_credibility >= 8.0:
                source_quality = "🟢"
            elif avg_credibility >= 6.0:
                source_quality = "🟡"
            else:
                source_quality = "🔴"
        
        # Methodology quality
        methodology_confidence = 7.0
        if self.analysis_metadata:
            methodology_confidence = getattr(self.analysis_metadata, 'overall_confidence', 7.0)
        
        return {
            "overall_score": self.overall_quality_score,
            "source_quality_indicator": source_quality,
            "source_count": source_count,
            "methodology_confidence": methodology_confidence,
            "has_enhanced_data": self.has_enhanced_data,
            "enhanced_data_types": self.enhanced_data_types
        }
    
    def can_expand_to_level(self, target_level: DetailLevel) -> bool:
        """Check if expansion to target detail level is possible"""
        current_level_value = ["summary", "detail", "full"].index(self.detail_level.value)
        target_level_value = ["summary", "detail", "full"].index(target_level.value)
        
        # Can always go to same or lower level
        if target_level_value <= current_level_value:
            return True
        
        # Check if enhanced data is available for higher levels
        if target_level == DetailLevel.DETAIL:
            return "sources" in self.enhanced_data_types or "methodology" in self.enhanced_data_types
        elif target_level == DetailLevel.FULL:
            return "source_analysis" in self.enhanced_data_types and "execution_trace" in self.enhanced_data_types
        
        return False 