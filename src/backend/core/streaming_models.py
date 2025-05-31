#!/usr/bin/env python3
"""
Streaming data models for real-time competitive intelligence analysis.

Provides event-based models for real-time updates, progress tracking,
and error handling during LangGraph pipeline execution.

Following backend organization guidelines in src/backend/core/streaming_models.py
"""

from typing import List, Dict, Any, Optional, Union, Annotated, Literal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, Discriminator

from .source_models import TavilySourceMetadata, SourceCitation

class StreamingEventType(str, Enum):
    """Types of streaming events during analysis"""
    
    # Pipeline lifecycle events
    ANALYSIS_STARTED = "analysis_started"
    ANALYSIS_COMPLETED = "analysis_completed"
    ANALYSIS_ERROR = "analysis_error"
    
    # Node execution events
    NODE_STARTED = "node_started"
    NODE_COMPLETED = "node_completed"
    NODE_ERROR = "node_error"
    
    # Research progress events
    SEARCH_STARTED = "search_started"
    SOURCE_FOUND = "source_found"
    SOURCE_ANALYZED = "source_analyzed"
    SEARCH_COMPLETED = "search_completed"
    
    # Analysis progress events
    GAP_IDENTIFIED = "gap_identified"
    OPPORTUNITY_GENERATED = "opportunity_generated"
    INSIGHT_DISCOVERED = "insight_discovered"
    
    # Progress tracking events
    PROGRESS_UPDATE = "progress_update"
    STATUS_UPDATE = "status_update"

class StreamingStatus(str, Enum):
    """Status levels for streaming updates"""
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    PROGRESS = "progress"

class BaseStreamingEvent(BaseModel):
    """Base streaming event model"""
    
    timestamp: datetime = Field(default_factory=datetime.now, description="Event timestamp")
    status: StreamingStatus = Field(default=StreamingStatus.INFO, description="Event status level")
    message: str = Field(description="Human-readable event message")
    progress_percentage: Optional[float] = Field(default=None, description="Overall progress percentage (0-100)")
    
class AnalysisStartedEvent(BaseStreamingEvent):
    """Event when analysis begins"""
    
    event_type: Literal[StreamingEventType.ANALYSIS_STARTED] = Field(default=StreamingEventType.ANALYSIS_STARTED)
    competitors: List[str] = Field(description="List of competitors being analyzed")
    focus_area: str = Field(description="Analysis focus area")
    device_category: str = Field(description="Detected device category")
    estimated_duration: Optional[int] = Field(default=None, description="Estimated duration in seconds")

class NodeExecutionEvent(BaseStreamingEvent):
    """Event for LangGraph node execution"""
    
    event_type: Literal[StreamingEventType.NODE_STARTED] = Field(default=StreamingEventType.NODE_STARTED)
    node_name: str = Field(description="Name of the executing LangGraph node")
    node_description: str = Field(description="Human-readable description of node purpose")
    execution_order: int = Field(description="Order of execution in the pipeline")
    input_summary: Optional[str] = Field(default=None, description="Summary of input data")

class SearchProgressEvent(BaseStreamingEvent):
    """Event for search and research progress"""
    
    event_type: Literal[StreamingEventType.SEARCH_STARTED] = Field(default=StreamingEventType.SEARCH_STARTED)
    competitor: str = Field(description="Competitor being researched")
    query: str = Field(description="Search query being executed")
    search_iteration: int = Field(description="Current search iteration")
    total_searches: int = Field(description="Total planned searches")

class SourceDiscoveryEvent(BaseStreamingEvent):
    """Event when a source is found and analyzed"""
    
    event_type: Literal[StreamingEventType.SOURCE_FOUND] = Field(default=StreamingEventType.SOURCE_FOUND)
    source_url: str = Field(description="URL of discovered source")
    source_title: str = Field(description="Title of the source")
    source_domain: str = Field(description="Domain of the source")
    credibility_score: float = Field(description="Assessed credibility score (1-10)")
    relevance_score: float = Field(description="Relevance to query (1-10)")
    content_snippet: str = Field(description="Brief content snippet")

class InsightDiscoveryEvent(BaseStreamingEvent):
    """Event when analysis insights are discovered"""
    
    event_type: Literal[StreamingEventType.INSIGHT_DISCOVERED] = Field(default=StreamingEventType.INSIGHT_DISCOVERED)
    insight_type: str = Field(description="Type of insight (gap, opportunity, market_position)")
    insight_title: str = Field(description="Brief title of the insight")
    insight_summary: str = Field(description="Summary of the insight")
    confidence_score: float = Field(description="Confidence in the insight (1-10)")
    supporting_sources: List[str] = Field(default_factory=list, description="URLs of supporting sources")

class OpportunityGeneratedEvent(BaseStreamingEvent):
    """Event when strategic opportunities are generated"""
    
    event_type: Literal[StreamingEventType.OPPORTUNITY_GENERATED] = Field(default=StreamingEventType.OPPORTUNITY_GENERATED)
    opportunity_title: str = Field(description="Title of the generated opportunity")
    opportunity_category: str = Field(description="Category (Brand, Product, Pricing, Market)")
    opportunity_score: float = Field(description="Opportunity score (1-10)")
    implementation_difficulty: str = Field(description="Implementation difficulty level")
    time_to_market: str = Field(description="Estimated time to market")

class ProgressUpdateEvent(BaseStreamingEvent):
    """General progress update event"""
    
    event_type: Literal[StreamingEventType.PROGRESS_UPDATE] = Field(default=StreamingEventType.PROGRESS_UPDATE)
    current_step: str = Field(description="Current step description")
    completed_steps: List[str] = Field(description="List of completed steps")
    remaining_steps: List[str] = Field(description="List of remaining steps")
    estimated_completion: Optional[datetime] = Field(default=None, description="Estimated completion time")

class AnalysisCompletedEvent(BaseStreamingEvent):
    """Event when analysis is completed"""
    
    event_type: Literal[StreamingEventType.ANALYSIS_COMPLETED] = Field(default=StreamingEventType.ANALYSIS_COMPLETED)
    total_duration: float = Field(description="Total analysis duration in seconds")
    opportunities_found: int = Field(description="Number of opportunities identified")
    sources_analyzed: int = Field(description="Number of sources analyzed")
    confidence_score: float = Field(description="Overall confidence score")
    summary: str = Field(description="Executive summary of findings")

class ErrorEvent(BaseStreamingEvent):
    """Event for errors during analysis"""
    
    event_type: Literal[StreamingEventType.ANALYSIS_ERROR] = Field(default=StreamingEventType.ANALYSIS_ERROR)
    status: StreamingStatus = Field(default=StreamingStatus.ERROR)
    error_type: str = Field(description="Type of error")
    error_details: str = Field(description="Detailed error information")
    recovery_suggestion: Optional[str] = Field(default=None, description="Suggested recovery action")
    is_recoverable: bool = Field(default=False, description="Whether the error is recoverable")

# Discriminated Union type for all streaming events  
StreamingEvent = Annotated[Union[
    AnalysisStartedEvent,
    NodeExecutionEvent,
    SearchProgressEvent,
    SourceDiscoveryEvent,
    InsightDiscoveryEvent,
    OpportunityGeneratedEvent,
    ProgressUpdateEvent,
    AnalysisCompletedEvent,
    ErrorEvent
], Field(discriminator='event_type')]

class StreamingResponse(BaseModel):
    """Container for streaming response data"""
    
    event: StreamingEvent = Field(description="The streaming event")
    session_id: str = Field(description="Unique session identifier")
    sequence_number: int = Field(description="Sequential event number")
    
class StreamingSession(BaseModel):
    """Model for managing streaming sessions"""
    
    session_id: str = Field(description="Unique session identifier")
    started_at: datetime = Field(default_factory=datetime.now)
    client_info: Dict[str, Any] = Field(default_factory=dict, description="Client connection information")
    analysis_config: Dict[str, Any] = Field(description="Analysis configuration")
    last_activity: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True)
    events_sent: int = Field(default=0)

class StreamingMetrics(BaseModel):
    """Metrics for streaming performance monitoring"""
    
    session_id: str = Field(description="Session identifier")
    events_sent: int = Field(description="Total events sent")
    events_per_second: float = Field(description="Events per second rate")
    connection_duration: float = Field(description="Connection duration in seconds")
    bytes_sent: int = Field(description="Total bytes transmitted")
    client_disconnections: int = Field(default=0, description="Number of client disconnections")
    errors_encountered: int = Field(default=0, description="Number of errors")

class StreamingConfig(BaseModel):
    """Configuration for streaming behavior"""
    
    max_events_per_second: int = Field(default=10, description="Rate limiting: max events per second")
    batch_events: bool = Field(default=False, description="Whether to batch multiple events")
    batch_size: int = Field(default=5, description="Number of events per batch")
    heartbeat_interval: int = Field(default=30, description="Heartbeat interval in seconds")
    max_session_duration: int = Field(default=3600, description="Max session duration in seconds")
    buffer_size: int = Field(default=100, description="Event buffer size") 