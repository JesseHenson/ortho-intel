"""
Cache Models for Competitive Intelligence Analysis

This module defines SQLAlchemy models for caching analysis results to reduce API costs
and improve response times. Designed for easy extension and AI assistant comprehension.

Key Design Principles:
- Clear separation between raw data and processed results
- Extensible schema for future enhancements
- Self-documenting field names and relationships
- Optimized for both storage efficiency and query performance
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import hashlib
import json

Base = declarative_base()

class AnalysisCache(Base):
    """
    Primary cache table for competitive intelligence analysis results.
    
    This table stores complete analysis results with metadata for efficient retrieval.
    Cache keys are MD5 hashes of sorted competitors + focus area for consistent lookup.
    
    Usage:
        # Create cache entry
        cache_entry = AnalysisCache.create_from_params(['Stryker', 'Zimmer'], 'spine_fusion')
        
        # Check if cache is valid
        if cache_entry.is_valid():
            return cache_entry.get_results()
    """
    __tablename__ = "analysis_cache"
    
    # Primary identification
    id = Column(Integer, primary_key=True, autoincrement=True)
    cache_key = Column(String(32), unique=True, nullable=False, index=True)  # MD5 hash
    
    # Analysis parameters (for human readability and debugging)
    competitors = Column(JSON, nullable=False)  # ["Stryker Spine", "Zimmer Biomet"]
    focus_area = Column(String(100), nullable=False)  # "spine_fusion"
    
    # Cache metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    last_accessed = Column(DateTime, default=datetime.utcnow, nullable=False)
    hit_count = Column(Integer, default=0, nullable=False)
    
    # Analysis status and results
    status = Column(String(20), default="pending", nullable=False)  # pending, complete, failed, expired
    analysis_results = Column(JSON, nullable=True)  # Complete transformed results for frontend
    raw_langgraph_state = Column(JSON, nullable=True)  # Raw LangGraph final state for debugging
    
    # Performance metadata
    original_processing_time = Column(Float, nullable=True)  # Seconds
    total_api_cost_saved = Column(Float, default=0.0, nullable=False)  # Estimated USD saved
    
    # Relationships
    search_results = relationship("CachedSearchResult", back_populates="cache_entry", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_cache_lookup', 'cache_key', 'status', 'expires_at'),
        Index('idx_competitors_focus', 'focus_area'),
    )
    
    @classmethod
    def generate_cache_key(cls, competitors: List[str], focus_area: str) -> str:
        """
        Generate consistent cache key from analysis parameters.
        
        Args:
            competitors: List of competitor names
            focus_area: Focus area string (e.g., 'spine_fusion')
            
        Returns:
            32-character MD5 hash for cache lookup
            
        Example:
            key = AnalysisCache.generate_cache_key(['Stryker', 'Zimmer'], 'spine_fusion')
            # Returns: "a1b2c3d4e5f6..."
        """
        # Sort competitors for consistent hashing regardless of input order
        sorted_competitors = sorted([comp.strip().lower() for comp in competitors])
        normalized_focus = focus_area.strip().lower()
        
        # Create consistent string representation
        cache_string = f"{','.join(sorted_competitors)}||{normalized_focus}"
        
        # Generate MD5 hash
        return hashlib.md5(cache_string.encode('utf-8')).hexdigest()
    
    @classmethod
    def create_from_params(cls, competitors: List[str], focus_area: str, 
                          expiry_days: int = 7) -> 'AnalysisCache':
        """
        Create new cache entry from analysis parameters.
        
        Args:
            competitors: List of competitor names
            focus_area: Analysis focus area
            expiry_days: Days until cache expires (default: 7)
            
        Returns:
            New AnalysisCache instance (not yet saved to database)
        """
        cache_key = cls.generate_cache_key(competitors, focus_area)
        expires_at = datetime.utcnow() + timedelta(days=expiry_days)
        
        return cls(
            cache_key=cache_key,
            competitors=competitors,
            focus_area=focus_area,
            expires_at=expires_at,
            status="pending"
        )
    
    def is_valid(self) -> bool:
        """Check if cache entry is valid and not expired."""
        return (
            self.status == "complete" and 
            self.expires_at > datetime.utcnow() and
            self.analysis_results is not None
        )
    
    def mark_accessed(self) -> None:
        """Update access metadata when cache is used."""
        self.last_accessed = datetime.utcnow()
        self.hit_count += 1
    
    def get_results(self) -> Dict[str, Any]:
        """
        Get cached analysis results.
        
        Returns:
            Dictionary containing complete analysis results in frontend format
            
        Raises:
            ValueError: If cache is invalid or results are None
        """
        if not self.is_valid():
            raise ValueError(f"Cache entry {self.cache_key} is invalid or expired")
        
        return self.analysis_results
    
    def store_results(self, results: Dict[str, Any], langgraph_state: Dict[str, Any],
                     processing_time: float) -> None:
        """
        Store analysis results in cache entry.
        
        Args:
            results: Transformed results ready for frontend
            langgraph_state: Raw LangGraph state for debugging
            processing_time: Original processing time in seconds
        """
        import json
        from datetime import datetime
        
        # Custom JSON encoder for datetime objects
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        # Serialize with custom encoder
        try:
            self.analysis_results = json.loads(json.dumps(results, default=json_serializer))
            self.raw_langgraph_state = json.loads(json.dumps(langgraph_state, default=json_serializer))
        except Exception as e:
            # If serialization fails, convert to strings manually
            self.analysis_results = self._deep_convert_datetime(results)
            self.raw_langgraph_state = self._deep_convert_datetime(langgraph_state)
        
        self.original_processing_time = processing_time
        self.status = "complete"
    
    def _deep_convert_datetime(self, obj: Any) -> Any:
        """Recursively convert datetime objects to ISO strings."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {key: self._deep_convert_datetime(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_convert_datetime(item) for item in obj]
        else:
            return obj


class CachedSearchResult(Base):
    """
    Individual Tavily search results for granular caching and analysis.
    
    This table stores raw search results to enable partial cache hits and
    detailed analysis of search patterns. Useful for debugging and optimization.
    """
    __tablename__ = "cached_search_results"
    
    # Primary identification
    id = Column(Integer, primary_key=True, autoincrement=True)
    cache_id = Column(Integer, ForeignKey('analysis_cache.id'), nullable=False)
    
    # Search parameters
    query = Column(Text, nullable=False)
    competitor = Column(String(200), nullable=True)  # Which competitor this search was for
    search_iteration = Column(Integer, nullable=False)  # Which iteration in the research cycle
    
    # Search results
    url = Column(Text, nullable=True)
    title = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    score = Column(Float, nullable=True)
    
    # Enhanced metadata
    credibility_score = Column(Float, nullable=True)
    domain = Column(String(200), nullable=True)
    source_type = Column(String(50), nullable=True)  # academic, commercial, news, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    cache_entry = relationship("AnalysisCache", back_populates="search_results")
    
    # Indexes
    __table_args__ = (
        Index('idx_search_cache', 'cache_id', 'competitor'),
        Index('idx_search_query', 'query'),
    )


class CacheConfig(Base):
    """
    Configuration settings for cache behavior.
    
    This table stores cache configuration to make the system easily configurable
    without code changes. Useful for A/B testing and production tuning.
    """
    __tablename__ = "cache_config"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    setting_name = Column(String(100), unique=True, nullable=False)
    setting_value = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_setting(cls, session, name: str, default: Any = None) -> Any:
        """Get configuration setting with fallback to default."""
        setting = session.query(cls).filter_by(setting_name=name).first()
        if setting:
            # Try to parse as JSON first, then return as string
            try:
                return json.loads(setting.setting_value)
            except json.JSONDecodeError:
                return setting.setting_value
        return default
    
    @classmethod
    def set_setting(cls, session, name: str, value: Any, description: str = None) -> None:
        """Set configuration setting, creating or updating as needed."""
        setting = session.query(cls).filter_by(setting_name=name).first()
        
        # Convert value to JSON string if it's not already a string
        if isinstance(value, (dict, list, bool, int, float)):
            value_str = json.dumps(value)
        else:
            value_str = str(value)
        
        if setting:
            setting.setting_value = value_str
            setting.description = description
            setting.updated_at = datetime.utcnow()
        else:
            setting = cls(
                setting_name=name,
                setting_value=value_str,
                description=description
            )
            session.add(setting)


# Default configuration settings to initialize
DEFAULT_CACHE_SETTINGS = {
    "cache_expiry_days": (7, "Default cache expiry in days"),
    "max_cache_entries": (1000, "Maximum number of cache entries before cleanup"),
    "simulate_streaming": (True, "Whether to simulate live streaming for cached results"),
    "streaming_chunk_delay": (1.5, "Delay between streaming chunks in seconds"),
    "cache_hit_cost_savings": (2.50, "Estimated USD saved per cache hit"),
    "enable_partial_caching": (False, "Enable caching of intermediate LangGraph states"),
} 