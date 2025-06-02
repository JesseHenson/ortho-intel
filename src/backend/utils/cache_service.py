"""
Cache Service for Competitive Intelligence Analysis

This service provides a clean, type-safe interface for caching competitive intelligence
analysis results. Designed for AI assistant comprehension with clear patterns and
comprehensive error handling.

Key Features:
- Automatic cache key generation and validation
- Intelligent cache expiry and cleanup
- Simulated streaming for cached results
- Comprehensive logging for debugging
- Cost tracking for API usage optimization

Usage:
    # Initialize service
    cache_service = CacheService()
    
    # Check for cached results
    cached = await cache_service.get_cached_analysis(['Stryker'], 'spine_fusion')
    if cached:
        return cached
    
    # Store new results
    await cache_service.store_analysis(['Stryker'], 'spine_fusion', results, state, time)
"""

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import List, Dict, Any, Optional, Tuple, AsyncGenerator, Union
import os
import logging
import asyncio
import json
from datetime import datetime, timedelta

from src.backend.core.cache_models import Base, AnalysisCache, CachedSearchResult, CacheConfig, DEFAULT_CACHE_SETTINGS

logger = logging.getLogger(__name__)

class CacheService:
    """
    High-level cache service for competitive intelligence analysis.
    
    This service abstracts database operations and provides intelligent caching
    behavior including cache validation, cleanup, and streaming simulation.
    
    Attributes:
        engine: SQLAlchemy database engine
        SessionLocal: SQLAlchemy session factory
        db_path: Path to SQLite database file
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize cache service with database connection.
        
        Args:
            db_path: Optional path to SQLite database file.
                    Defaults to 'cache/analysis_cache.db' in project root.
        """
        # Set up database path
        if db_path is None:
            # Default to cache directory in project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            cache_dir = os.path.join(project_root, "cache")
            os.makedirs(cache_dir, exist_ok=True)
            db_path = os.path.join(cache_dir, "analysis_cache.db")
        
        self.db_path = db_path
        
        # Create SQLite engine with connection pooling
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            poolclass=StaticPool,
            connect_args={
                "check_same_thread": False,
                "timeout": 30
            },
            echo=False  # Set to True for SQL debugging
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Initialize database
        self._initialize_database()
        
        logger.info(f"Cache service initialized with database: {db_path}")
    
    def _initialize_database(self) -> None:
        """Create database tables and initialize default configuration."""
        try:
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            
            # Initialize default configuration settings
            with self.SessionLocal() as session:
                for setting_name, (value, description) in DEFAULT_CACHE_SETTINGS.items():
                    CacheConfig.set_setting(session, setting_name, value, description)
                session.commit()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get database session for manual operations."""
        return self.SessionLocal()
    
    async def get_cached_analysis(self, competitors: List[str], focus_area: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached analysis results if available and valid.
        
        Args:
            competitors: List of competitor names
            focus_area: Analysis focus area (e.g., 'spine_fusion')
            
        Returns:
            Cached analysis results dictionary, or None if no valid cache exists
            
        Example:
            results = await cache_service.get_cached_analysis(['Stryker'], 'spine_fusion')
            if results:
                print(f"Cache hit! Found {len(results['clinical_gaps'])} gaps")
        """
        cache_key = AnalysisCache.generate_cache_key(competitors, focus_area)
        
        try:
            with self.SessionLocal() as session:
                # Find valid cache entry
                cache_entry = session.query(AnalysisCache).filter(
                    and_(
                        AnalysisCache.cache_key == cache_key,
                        AnalysisCache.status == "complete",
                        AnalysisCache.expires_at > datetime.utcnow()
                    )
                ).first()
                
                if cache_entry and cache_entry.is_valid():
                    # Update access metadata
                    cache_entry.mark_accessed()
                    session.commit()
                    
                    logger.info(f"Cache HIT for {competitors} + {focus_area} "
                              f"(hit #{cache_entry.hit_count}, saved ${self._get_cost_savings():.2f})")
                    
                    return cache_entry.get_results()
                else:
                    logger.info(f"Cache MISS for {competitors} + {focus_area}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving cached analysis: {e}")
            return None
    
    async def store_analysis(self, competitors: List[str], focus_area: str, 
                           results: Dict[str, Any], langgraph_state: Dict[str, Any],
                           processing_time: float) -> bool:
        """
        Store analysis results in cache for future retrieval.
        
        Args:
            competitors: List of competitor names
            focus_area: Analysis focus area
            results: Transformed analysis results ready for frontend
            langgraph_state: Raw LangGraph final state for debugging
            processing_time: Original processing time in seconds
            
        Returns:
            True if stored successfully, False otherwise
            
        Example:
            success = await cache_service.store_analysis(
                ['Stryker'], 'spine_fusion', results, state, 15.2
            )
        """
        try:
            with self.SessionLocal() as session:
                # Check if cache entry already exists
                cache_key = AnalysisCache.generate_cache_key(competitors, focus_area)
                existing = session.query(AnalysisCache).filter_by(cache_key=cache_key).first()
                
                if existing:
                    # Update existing entry
                    existing.store_results(results, langgraph_state, processing_time)
                    cache_entry = existing
                else:
                    # Create new cache entry
                    expiry_days = self._get_setting(session, "cache_expiry_days", 7)
                    cache_entry = AnalysisCache.create_from_params(
                        competitors, focus_area, expiry_days
                    )
                    cache_entry.store_results(results, langgraph_state, processing_time)
                    session.add(cache_entry)
                
                # Store search results if available
                await self._store_search_results(session, cache_entry, langgraph_state)
                
                session.commit()
                
                logger.info(f"Analysis cached successfully for {competitors} + {focus_area} "
                          f"(processing time: {processing_time:.1f}s)")
                
                # Cleanup old entries if needed
                await self._cleanup_expired_entries()
                
                return True
                
        except Exception as e:
            logger.error(f"Error storing analysis in cache: {e}")
            return False
    
    async def _store_search_results(self, session: Session, cache_entry: AnalysisCache, 
                                  langgraph_state: Dict[str, Any]) -> None:
        """Store individual search results for granular caching."""
        try:
            # Extract search results from LangGraph state
            raw_results = langgraph_state.get('raw_research_results', [])
            search_queries = langgraph_state.get('search_queries', [])
            
            for i, result in enumerate(raw_results):
                if isinstance(result, dict):
                    search_result = CachedSearchResult(
                        cache_id=cache_entry.id,
                        query=result.get('query', search_queries[i] if i < len(search_queries) else ''),
                        competitor=result.get('competitor', ''),
                        search_iteration=result.get('iteration', i),
                        url=result.get('url', ''),
                        title=result.get('title', ''),
                        content=result.get('content', ''),
                        score=result.get('score', 0.0),
                        credibility_score=result.get('credibility_score'),
                        domain=result.get('domain'),
                        source_type=result.get('source_type')
                    )
                    session.add(search_result)
                    
        except Exception as e:
            logger.warning(f"Could not store search results: {e}")
    
    async def simulate_cached_streaming(self, cached_results: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """
        Simulate live streaming for cached results to maintain user experience.
        
        This method breaks down cached results into chunks and yields them with
        realistic delays to simulate the original analysis process.
        
        Args:
            cached_results: Complete cached analysis results
            
        Yields:
            JSON strings containing streaming events
            
        Example:
            async for chunk in cache_service.simulate_cached_streaming(results):
                await send_to_frontend(chunk)
        """
        try:
            # Get streaming configuration
            with self.SessionLocal() as session:
                chunk_delay = self._get_setting(session, "streaming_chunk_delay", 1.5)
                simulate_enabled = self._get_setting(session, "simulate_streaming", True)
            
            if not simulate_enabled:
                # Send everything at once
                yield json.dumps({
                    "type": "complete_analysis",
                    "data": cached_results,
                    "metadata": {"cached": True, "streaming_simulated": False}
                })
                return
            
            # Simulate progressive analysis streaming
            streaming_events = [
                ("analysis_started", {"competitors": cached_results.get("competitors", []), "cached": True}),
                ("research_phase", {"total_queries": len(cached_results.get("search_queries", []))}),
                ("gaps_identified", {"count": len(cached_results.get("clinical_gaps", []))}),
                ("opportunities_generated", {"count": len(cached_results.get("top_opportunities", []))}),
                ("analysis_complete", cached_results)
            ]
            
            logger.info("Starting simulated streaming for cached results")
            
            for event_type, data in streaming_events:
                event = {
                    "type": event_type,
                    "data": data,
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {"cached": True, "streaming_simulated": True}
                }
                
                yield json.dumps(event)
                
                # Wait between chunks (except for the last one)
                if event_type != "analysis_complete":
                    await asyncio.sleep(chunk_delay)
            
            logger.info("Simulated streaming completed")
            
        except Exception as e:
            logger.error(f"Error in simulated streaming: {e}")
            # Fallback: send complete results
            yield json.dumps({
                "type": "error",
                "message": "Streaming simulation failed, sending complete results",
                "data": cached_results,
                "metadata": {"cached": True, "error": True}
            })
    
    async def cleanup_expired_entries(self) -> int:
        """
        Remove expired cache entries and associated data.
        
        Returns:
            Number of entries cleaned up
        """
        try:
            with self.SessionLocal() as session:
                # Find expired entries
                expired_entries = session.query(AnalysisCache).filter(
                    AnalysisCache.expires_at < datetime.utcnow()
                ).all()
                
                count = len(expired_entries)
                
                # Delete expired entries (cascade will handle search results)
                for entry in expired_entries:
                    session.delete(entry)
                
                session.commit()
                
                if count > 0:
                    logger.info(f"Cleaned up {count} expired cache entries")
                
                return count
                
        except Exception as e:
            logger.error(f"Error cleaning up expired entries: {e}")
            return 0
    
    async def _cleanup_expired_entries(self) -> None:
        """Internal cleanup that runs after storing new entries."""
        await self.cleanup_expired_entries()
    
    def _get_setting(self, session: Session, name: str, default: Any = None) -> Any:
        """Get configuration setting from database."""
        return CacheConfig.get_setting(session, name, default)
    
    def _get_cost_savings(self) -> float:
        """Get estimated cost savings per cache hit."""
        with self.SessionLocal() as session:
            return self._get_setting(session, "cache_hit_cost_savings", 2.50)
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache statistics for monitoring and optimization.
        
        Returns:
            Dictionary containing cache performance metrics
        """
        try:
            with self.SessionLocal() as session:
                # Basic stats
                total_entries = session.query(AnalysisCache).count()
                valid_entries = session.query(AnalysisCache).filter(
                    and_(
                        AnalysisCache.status == "complete",
                        AnalysisCache.expires_at > datetime.utcnow()
                    )
                ).count()
                
                # Performance stats
                total_hits = session.query(AnalysisCache).filter(
                    AnalysisCache.hit_count > 0
                ).count()
                
                avg_processing_time = session.query(AnalysisCache).filter(
                    AnalysisCache.original_processing_time.isnot(None)
                ).with_entities(AnalysisCache.original_processing_time).all()
                
                avg_time = sum(t[0] for t in avg_processing_time) / len(avg_processing_time) if avg_processing_time else 0
                
                # Cost savings
                cost_per_hit = self._get_cost_savings()
                total_cost_saved = total_hits * cost_per_hit
                
                return {
                    "total_cache_entries": total_entries,
                    "valid_entries": valid_entries,
                    "cache_hits": total_hits,
                    "hit_rate": (total_hits / total_entries * 100) if total_entries > 0 else 0,
                    "avg_processing_time": round(avg_time, 2),
                    "estimated_cost_saved": round(total_cost_saved, 2),
                    "database_path": self.db_path,
                    "database_size_mb": os.path.getsize(self.db_path) / 1024 / 1024 if os.path.exists(self.db_path) else 0
                }
                
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}


# Global cache service instance for easy importing
cache_service = CacheService()

# Convenience functions for common operations
async def get_cached_analysis(competitors: List[str], focus_area: str) -> Optional[Dict[str, Any]]:
    """Convenience function to get cached analysis results."""
    return await cache_service.get_cached_analysis(competitors, focus_area)

async def store_analysis(competitors: List[str], focus_area: str, 
                        results: Dict[str, Any], langgraph_state: Dict[str, Any],
                        processing_time: float) -> bool:
    """Convenience function to store analysis results."""
    return await cache_service.store_analysis(competitors, focus_area, results, langgraph_state, processing_time)

async def simulate_streaming(cached_results: Dict[str, Any]) -> AsyncGenerator[str, None]:
    """Convenience function to simulate streaming for cached results."""
    async for chunk in cache_service.simulate_cached_streaming(cached_results):
        yield chunk 