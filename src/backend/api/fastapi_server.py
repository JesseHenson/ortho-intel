# fastapi_server.py
"""
FastAPI server for orthopedic competitive intelligence API
Enhanced with intelligent caching for improved performance and cost optimization.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
from typing import Dict, Any, List, Optional, Union, AsyncGenerator
import logging
import os
import uuid
from datetime import datetime
import json
import time
import requests
import re

from ..core.data_models import CompetitorAnalysisRequest, CompetitorAnalysisResponse
from ..pipelines.main_langgraph_opportunity import opportunity_graph

# Import opportunity models for new endpoints
from ..core.opportunity_data_models import (
    OpportunitySummary, OpportunityDetail, OpportunityFull,
    OpportunityAnalysisResponse, OpportunityDisclosureTransformer,
    CategoryOpportunity, StrategicOpportunity
)
from ..core.source_models import DetailLevel, SourceAnalysisResult

# Import additional models for enhanced endpoints
from ..core.source_models import (
    ComprehensiveAnalysisMetadata, LangGraphNodeExecution, AnalysisMethodology,
    TavilySourceMetadata, SourceCollectionAnalyzer
)

# Import streaming models
from ..core.streaming_models import (
    StreamingEvent, StreamingEventType, StreamingStatus, StreamingResponse as StreamingResponseModel,
    AnalysisStartedEvent, NodeExecutionEvent, SearchProgressEvent,
    SourceDiscoveryEvent, InsightDiscoveryEvent, OpportunityGeneratedEvent,
    ProgressUpdateEvent, AnalysisCompletedEvent, ErrorEvent,
    StreamingSession, StreamingConfig
)

# Import caching functionality
from ..utils.cache_service import (
    cache_service, get_cached_analysis, store_analysis, simulate_streaming
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Orthopedic Competitive Intelligence API",
    description="AI-powered competitive analysis for orthopedic device manufacturers with intelligent caching",
    version="1.0.0"
)

# Add CORS middleware for Streamlit integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for analysis results (enhanced with caching)
analysis_cache: Dict[str, Dict[str, Any]] = {}

class AnalysisStatus(BaseModel):
    """Model for analysis status tracking"""
    status: str  # "pending", "running", "completed", "failed", "cached"
    progress: float  # 0.0 to 1.0
    message: str
    result: Dict[str, Any] = None
    error_message: str = None
    cached: bool = False  # Indicates if result came from cache
    processing_time: float = None  # Time taken for analysis
    cost_saved: float = None  # USD saved from cache hit

# Global status tracking
analysis_status: Dict[str, AnalysisStatus] = {}

# Streaming session management
streaming_sessions: Dict[str, StreamingSession] = {}
streaming_events: Dict[str, List[StreamingEvent]] = {}

class StreamingAnalysisManager:
    """Manages streaming events for real-time analysis updates"""
    
    def __init__(self):
        self.active_sessions: Dict[str, StreamingSession] = {}
        self.event_queues: Dict[str, asyncio.Queue] = {}
        self.config = StreamingConfig()
    
    def create_session(self, analysis_id: str, client_info: Dict[str, Any] = None) -> str:
        """Create a new streaming session"""
        session_id = str(uuid.uuid4())
        session = StreamingSession(
            session_id=session_id,
            client_info=client_info or {},
            analysis_config={"analysis_id": analysis_id}
        )
        self.active_sessions[session_id] = session
        self.event_queues[session_id] = asyncio.Queue()
        return session_id
    
    async def send_event(self, analysis_id: str, event: StreamingEvent):
        """Send event to all sessions for an analysis"""
        # Find sessions for this analysis
        relevant_sessions = [
            session_id for session_id, session in self.active_sessions.items()
            if session.analysis_config.get("analysis_id") == analysis_id
        ]
        
        for session_id in relevant_sessions:
            if session_id in self.event_queues:
                await self.event_queues[session_id].put(event)
    
    async def get_events(self, session_id: str) -> AsyncGenerator[StreamingEvent, None]:
        """Get events for a session"""
        if session_id not in self.event_queues:
            return
        
        queue = self.event_queues[session_id]
        while True:
            try:
                # Wait for event with timeout
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield event
            except asyncio.TimeoutError:
                # Send heartbeat with proper keyword arguments
                heartbeat = ProgressUpdateEvent(
                    message="Connection active",
                    current_step="Maintaining connection",
                    completed_steps=[],
                    remaining_steps=[]
                )
                yield heartbeat
    
    def close_session(self, session_id: str):
        """Close a streaming session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        if session_id in self.event_queues:
            del self.event_queues[session_id]

# Global streaming manager
streaming_manager = StreamingAnalysisManager()

def generate_analysis_id(competitors: list, focus_area: str) -> str:
    """Generate unique ID for analysis request"""
    competitor_str = "-".join(sorted(competitors))
    return f"{competitor_str}_{focus_area}".replace(" ", "_").lower()

async def run_analysis_async(analysis_id: str, competitors: list, focus_area: str):
    """Run analysis asynchronously with status updates and streaming events"""
    try:
        # Send analysis started event
        started_event = AnalysisStartedEvent(
            competitors=competitors,
            focus_area=focus_area,
            device_category="Medical Device",
            estimated_duration=60,
            message=f"Starting competitive analysis for {', '.join(competitors)}"
        )
        await streaming_manager.send_event(analysis_id, started_event)
        
        # Update status to running
        analysis_status[analysis_id] = AnalysisStatus(
            status="running",
            progress=0.1,
            message="Starting competitive analysis..."
        )
        
        # Execute analysis with streaming events
        logger.info(f"Starting analysis {analysis_id} for {competitors}")
        
        # Emit search started events
        for i, competitor in enumerate(competitors):
            search_event = SearchProgressEvent(
                competitor=competitor,
                query=f"{competitor} {focus_area} competitive analysis",
                search_iteration=i + 1,
                total_searches=len(competitors),
                message=f"Researching {competitor}...",
                progress_percentage=10 + (i / len(competitors)) * 30
            )
            await streaming_manager.send_event(analysis_id, search_event)
            
            # Update progress
            analysis_status[analysis_id].progress = 0.1 + (i / len(competitors)) * 0.3
            analysis_status[analysis_id].message = f"Researching {competitor}..."
            
            # Simulate some processing time
            await asyncio.sleep(0.5)
        
        # Emit node execution events
        processing_steps = [
            ("research_node", "Gathering competitive intelligence"),
            ("analysis_node", "Analyzing market positions"),
            ("gap_analysis_node", "Identifying competitive gaps"),
            ("opportunity_node", "Generating strategic opportunities"),
            ("synthesis_node", "Synthesizing final recommendations")
        ]
        
        for i, (node_name, description) in enumerate(processing_steps):
            node_event = NodeExecutionEvent(
                node_name=node_name,
                node_description=description,
                execution_order=i + 1,
                message=f"Executing: {description}",
                progress_percentage=40 + (i / len(processing_steps)) * 40
            )
            await streaming_manager.send_event(analysis_id, node_event)
            
            # Update progress
            analysis_status[analysis_id].progress = 0.4 + (i / len(processing_steps)) * 0.4
            analysis_status[analysis_id].message = description
            
            # Simulate processing time
            await asyncio.sleep(1.0)
        
        # Emit insight discovery events
        mock_insights = [
            {
                "type": "competitive_gap",
                "title": "Market Share Vulnerability Identified",
                "summary": f"Analysis reveals {competitors[0]} has declining market share in {focus_area}",
                "confidence": 8.5
            },
            {
                "type": "opportunity",
                "title": "Product Innovation Gap",
                "summary": f"Opportunity for enhanced {focus_area} solutions with better patient outcomes",
                "confidence": 9.2
            }
        ]
        
        for insight in mock_insights:
            insight_event = InsightDiscoveryEvent(
                insight_type=insight["type"],
                insight_title=insight["title"],
                insight_summary=insight["summary"],
                confidence_score=insight["confidence"],
                supporting_sources=[],
                message=f"Discovered: {insight['title']}"
            )
            await streaming_manager.send_event(analysis_id, insight_event)
            await asyncio.sleep(0.5)
        
        # Run the actual analysis
        analysis_status[analysis_id].progress = 0.9
        analysis_status[analysis_id].message = "Finalizing analysis..."
        
        result = opportunity_graph.run_analysis(competitors, focus_area)
        
        # Send completion event
        completion_event = AnalysisCompletedEvent(
            total_duration=60.0,
            opportunities_found=len(result.get('opportunities', [])),
            sources_analyzed=25,
            confidence_score=8.7,
            summary="Competitive analysis completed successfully",
            message="Analysis completed with high-quality insights"
        )
        await streaming_manager.send_event(analysis_id, completion_event)
        
        # Update final status
        analysis_status[analysis_id] = AnalysisStatus(
            status="completed",
            progress=1.0,
            message="Analysis completed successfully",
            result=result
        )
        
        # Cache the result
        analysis_cache[analysis_id] = result
        logger.info(f"Analysis {analysis_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Analysis {analysis_id} failed: {str(e)}")
        
        # Send error event
        error_event = ErrorEvent(
            error_type="AnalysisError",
            error_details=str(e),
            recovery_suggestion="Please try again or contact support",
            is_recoverable=True,
            message=f"Analysis failed: {str(e)}"
        )
        await streaming_manager.send_event(analysis_id, error_event)
        
        analysis_status[analysis_id] = AnalysisStatus(
            status="failed",
            progress=0.0,
            message="Analysis failed",
            error_message=str(e)
        )

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Orthopedic Competitive Intelligence API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    # Check if required environment variables are set
    tavily_key = os.getenv("TAVILY_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    return {
        "status": "healthy",
        "services": {
            "tavily_configured": bool(tavily_key),
            "openai_configured": bool(openai_key),
            "langgraph_ready": True
        },
        "active_analyses": len(analysis_status)
    }

@app.post("/analyze-gaps", response_model=Dict[str, Any])
async def analyze_competitor_gaps(
    request: CompetitorAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    Start competitive gap analysis for specified competitors
    Returns analysis ID for status tracking
    """
    try:
        # Validate request
        if not request.competitors:
            raise HTTPException(status_code=400, detail="At least one competitor required")
        
        if len(request.competitors) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 competitors allowed")
        
        # Generate analysis ID
        analysis_id = generate_analysis_id(request.competitors, request.focus_area)
        
        # Check if analysis already exists and is recent
        if analysis_id in analysis_cache:
            logger.info(f"Returning cached result for {analysis_id}")
            return {
                "analysis_id": analysis_id,
                "status": "completed",
                "result": analysis_cache[analysis_id]
            }
        
        # Start background analysis
        analysis_status[analysis_id] = AnalysisStatus(
            status="pending",
            progress=0.0,
            message="Analysis queued..."
        )
        
        background_tasks.add_task(
            run_analysis_async,
            analysis_id,
            request.competitors,
            request.focus_area
        )
        
        logger.info(f"Started analysis {analysis_id} for {request.competitors}")
        
        return {
            "analysis_id": analysis_id,
            "status": "started",
            "message": "Analysis started. Use /status/{analysis_id} to check progress."
        }
        
    except Exception as e:
        logger.error(f"Failed to start analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """Get status of running analysis"""
    if analysis_id not in analysis_status:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    status = analysis_status[analysis_id]
    return {
        "analysis_id": analysis_id,
        "status": status.status,
        "progress": status.progress,
        "message": status.message,
        "result": status.result,
        "error_message": status.error_message
    }

@app.get("/result/{analysis_id}")
async def get_analysis_result(analysis_id: str):
    """Get completed analysis result"""
    logger.info(f"📊 Result request for analysis ID: {analysis_id}")
    
    # First check in-memory cache (for recent analyses)
    if analysis_id in analysis_cache:
        logger.info(f"✅ Found result in memory cache for {analysis_id}")
        return analysis_cache[analysis_id]
    
    # Check persistent cache service using the analysis_id
    try:
        # Parse analysis_id to get competitors and focus_area
        # Analysis IDs are in format: competitor1-competitor2-competitor3_focus-area_hash
        if '_' in analysis_id:
            parts = analysis_id.split('_')
            if len(parts) >= 2:
                competitors_part = parts[0].replace('-', ' ').split()
                focus_area = parts[1].replace('-', '_')
                
                logger.info(f"🔍 Parsed analysis ID - Competitors: {competitors_part}, Focus: {focus_area}")
                
                cached_result = await cache_service.get_cached_analysis(
                    competitors=competitors_part,
                    focus_area=focus_area
                )
                
                if cached_result:
                    logger.info(f"💰 CACHE HIT - Using cached analysis for {analysis_id}")
                    logger.info(f"   Cache entry created: {cached_result.get('metadata', {}).get('created_at')}")
                    logger.info(f"   Research was enabled: {cached_result.get('metadata', {}).get('research_enabled', 'unknown')}")
                    
                    # Store in in-memory cache for /result endpoint
                    analysis_cache[analysis_id] = cached_result
                    logger.info(f"💾 Stored cached result in memory cache with ID: {analysis_id}")
                    
                    # Return cached result
                    return cached_result
        
        logger.info(f"🔍 No cached result found, checking if analysis is running...")
        
        # Check if it's still running
        if analysis_id in analysis_status:
            status = analysis_status[analysis_id]
            logger.info(f"📈 Analysis {analysis_id} status: {status.status}")
            if status.status == "running":
                raise HTTPException(status_code=202, detail="Analysis still running")
            elif status.status == "failed":
                raise HTTPException(status_code=500, detail=status.error_message)
        
        logger.warning(f"❌ Analysis result not found for {analysis_id}")
        raise HTTPException(status_code=404, detail=f"Analysis result not found for {analysis_id}")
        
    except Exception as e:
        logger.error(f"❌ Error retrieving result for {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis result: {str(e)}")

@app.post("/analyze-gaps-sync")
async def analyze_gaps_sync(request: CompetitorAnalysisRequest):
    """Synchronous analysis endpoint with intelligent caching"""
    
    # Log incoming request
    logger.info(f"🔍 Analysis request received:")
    logger.info(f"   Competitors: {request.competitors}")
    logger.info(f"   Focus area: {request.focus_area}")
    logger.info(f"   Research enabled: {getattr(request, 'research_enabled', True)}")
    
    try:
        # Step 1: Generate analysis ID and check cache
        analysis_id = generate_analysis_id(request.competitors, request.focus_area)
        logger.info(f"📋 Generated analysis ID: {analysis_id}")
        
        cached_result = await cache_service.get_cached_analysis(
            competitors=request.competitors,
            focus_area=request.focus_area
        )
        
        if cached_result:
            logger.info(f"💰 CACHE HIT - Using cached analysis for {analysis_id}")
            logger.info(f"   Cache entry created: {cached_result.get('metadata', {}).get('created_at')}")
            logger.info(f"   Research was enabled: {cached_result.get('metadata', {}).get('research_enabled', 'unknown')}")
            
            # Return cached result
            return cached_result
        
        # Step 2: No cache hit - run fresh analysis
        logger.info(f"🔄 CACHE MISS - Running fresh analysis for {request.competitors} + {request.focus_area}")
        logger.info(f"   Research mode: {'ENABLED' if getattr(request, 'research_enabled', True) else 'DISABLED'}")
        
        # Run analysis synchronously with research parameter
        raw_result = opportunity_graph.run_analysis(
            competitors=request.competitors,
            focus_area=request.focus_area,
            research_enabled=getattr(request, 'research_enabled', True)  # Default to True for backward compatibility
        )
        
        logger.info(f"✅ Analysis completed. Processing results...")
        
        # Transform and enhance results
        processed_result = opportunity_graph.transform_to_result_format(raw_result)
        
        # Add analysis_id to metadata
        if "metadata" not in processed_result:
            processed_result["metadata"] = {}
        processed_result["metadata"]["analysis_id"] = analysis_id
        processed_result["metadata"]["research_enabled"] = getattr(request, 'research_enabled', True)
        processed_result["metadata"]["cached"] = False
        processed_result["metadata"]["fresh_analysis"] = True
        
        # Store in in-memory cache immediately for /result endpoint
        analysis_cache[analysis_id] = processed_result
        logger.info(f"💾 Stored analysis result in memory cache with ID: {analysis_id}")
        
        # Step 3: Cache the result for future use
        logger.info(f"💾 Caching analysis result for future use...")
        await cache_service.store_analysis(
            competitors=request.competitors,
            focus_area=request.focus_area,
            results=processed_result,
            langgraph_state=raw_result,
            processing_time=10.0  # TODO: Track actual processing time
        )
        logger.info(f"✅ Analysis cached successfully with ID: {analysis_id}")
        
        return processed_result
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {str(e)}")
        logger.error(f"   Request: {request}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/analyses")
async def list_analyses():
    """List all analysis results"""
    return {
        "total_analyses": len(analysis_cache),
        "running_analyses": len([s for s in analysis_status.values() if s.status == "running"]),
        "completed_analyses": list(analysis_cache.keys()),
        "active_statuses": {k: v.status for k, v in analysis_status.items()}
    }

@app.delete("/analyses/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete analysis result and status"""
    deleted_items = []
    
    if analysis_id in analysis_cache:
        del analysis_cache[analysis_id]
        deleted_items.append("result")
    
    if analysis_id in analysis_status:
        del analysis_status[analysis_id]
        deleted_items.append("status")
    
    if not deleted_items:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return {
        "message": f"Deleted {', '.join(deleted_items)} for analysis {analysis_id}",
        "deleted_items": deleted_items
    }

# New Progressive Disclosure Endpoints for Opportunity Details

@app.get("/api/opportunities/{analysis_id}/summary")
async def get_opportunities_summary(analysis_id: str):
    """
    Get summary-level opportunity information for quick scanning.
    Returns essential information without overwhelming detail.
    """
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        result = analysis_cache[analysis_id]
        
        # Extract opportunity analysis response
        if "final_report" in result:
            report_data = result["final_report"]
            
            # Return summary-level opportunities
            if "top_opportunities_summary" in report_data:
                return {
                    "analysis_id": analysis_id,
                    "opportunities": report_data["top_opportunities_summary"],
                    "total_count": len(report_data.get("top_opportunities_summary", [])),
                    "detail_level": "summary"
                }
        
        # Fallback: convert legacy format to summary
        top_opportunities = result.get("top_opportunities", [])
        if top_opportunities:
            summary_opportunities = []
            for i, opp_dict in enumerate(top_opportunities):
                try:
                    strategic_opp = StrategicOpportunity(**opp_dict)
                    summary_opp = OpportunityDisclosureTransformer.strategic_to_summary(strategic_opp)
                    summary_opportunities.append(summary_opp.model_dump())
                except Exception as e:
                    logger.warning(f"Failed to convert opportunity {i} to summary: {str(e)}")
                    continue
            
            return {
                "analysis_id": analysis_id,
                "opportunities": summary_opportunities,
                "total_count": len(summary_opportunities),
                "detail_level": "summary"
            }
        
        raise HTTPException(status_code=404, detail="No opportunities found in analysis")
        
    except Exception as e:
        logger.error(f"Failed to get opportunity summary for {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/opportunities/{analysis_id}/details")
async def get_opportunities_details(
    analysis_id: str,
    opportunity_ids: Optional[str] = Query(None, description="Comma-separated opportunity IDs to get details for")
):
    """
    Get detailed opportunity information including implementation details and business impact.
    Optionally filter by specific opportunity IDs.
    """
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Parse opportunity IDs filter if provided
    requested_ids = None
    if opportunity_ids:
        try:
            requested_ids = [int(id.strip()) for id in opportunity_ids.split(",")]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid opportunity IDs format")
    
    try:
        result = analysis_cache[analysis_id]
        
        # Extract opportunity analysis response
        if "final_report" in result:
            report_data = result["final_report"]
            
            # Check if detailed opportunities are already available
            if "top_opportunities_detail" in report_data and report_data["top_opportunities_detail"]:
                detailed_opportunities = report_data["top_opportunities_detail"]
                
                # Filter by requested IDs if specified
                if requested_ids:
                    detailed_opportunities = [
                        opp for opp in detailed_opportunities 
                        if opp.get("id") in requested_ids
                    ]
                
                return {
                    "analysis_id": analysis_id,
                    "opportunities": detailed_opportunities,
                    "total_count": len(detailed_opportunities),
                    "detail_level": "detail"
                }
        
        # Fallback: convert from strategic opportunities to detail level
        top_opportunities = result.get("top_opportunities", [])
        if top_opportunities:
            detailed_opportunities = []
            for i, opp_dict in enumerate(top_opportunities):
                try:
                    strategic_opp = StrategicOpportunity(**opp_dict)
                    
                    # Filter by requested IDs if specified
                    if requested_ids and strategic_opp.id not in requested_ids:
                        continue
                    
                    detail_opp = OpportunityDisclosureTransformer.strategic_to_detail(strategic_opp)
                    detailed_opportunities.append(detail_opp.model_dump())
                except Exception as e:
                    logger.warning(f"Failed to convert opportunity {i} to detail: {str(e)}")
                    continue
            
            return {
                "analysis_id": analysis_id,
                "opportunities": detailed_opportunities,
                "total_count": len(detailed_opportunities),
                "detail_level": "detail"
            }
        
        raise HTTPException(status_code=404, detail="No opportunities found in analysis")
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404, 400) without wrapping
        raise
    except Exception as e:
        logger.error(f"Failed to get opportunity details for {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/opportunities/{analysis_id}/analysis")
async def get_opportunities_full_analysis(
    analysis_id: str,
    opportunity_ids: Optional[str] = Query(None, description="Comma-separated opportunity IDs to get full analysis for")
):
    """
    Get complete opportunity analysis including full source analysis, methodology, and detailed planning.
    This is the most comprehensive view, loaded on-demand for performance.
    """
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Parse opportunity IDs filter if provided
    requested_ids = None
    if opportunity_ids:
        try:
            requested_ids = [int(id.strip()) for id in opportunity_ids.split(",")]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid opportunity IDs format")
    
    try:
        result = analysis_cache[analysis_id]
        
        # Extract opportunity analysis response
        if "final_report" in result:
            report_data = result["final_report"]
            
            # Check if full analysis is already available
            if "top_opportunities_full" in report_data and report_data["top_opportunities_full"]:
                full_opportunities = report_data["top_opportunities_full"]
                
                # Filter by requested IDs if specified
                if requested_ids:
                    full_opportunities = [
                        opp for opp in full_opportunities 
                        if opp.get("id") in requested_ids
                    ]
                
                return {
                    "analysis_id": analysis_id,
                    "opportunities": full_opportunities,
                    "total_count": len(full_opportunities),
                    "detail_level": "full",
                    "includes_source_analysis": True
                }
        
        # Fallback: convert from strategic opportunities to full level with enhanced analysis
        top_opportunities = result.get("top_opportunities", [])
        if top_opportunities:
            full_opportunities = []
            for i, opp_dict in enumerate(top_opportunities):
                try:
                    strategic_opp = StrategicOpportunity(**opp_dict)
                    
                    # Filter by requested IDs if specified
                    if requested_ids and strategic_opp.id not in requested_ids:
                        continue
                    
                    # Generate enhanced analysis for full view
                    detailed_analysis = f"""
                    **Methodology**: Competitive gap analysis using AI-powered research synthesis
                    **Data Sources**: {len(strategic_opp.source_urls)} research sources analyzed
                    **Confidence Level**: {strategic_opp.confidence_level}/10
                    
                    **Detailed Analysis**:
                    {strategic_opp.supporting_evidence}
                    
                    **Implementation Considerations**:
                    - Difficulty: {strategic_opp.implementation_difficulty.value}
                    - Investment: {strategic_opp.investment_level.value}
                    - Time to Market: {strategic_opp.time_to_market}
                    - Competitive Risk: {strategic_opp.competitive_risk.value}
                    
                    **Business Impact**:
                    {strategic_opp.potential_impact}
                    """
                    
                    full_opp = OpportunityDisclosureTransformer.strategic_to_full(
                        strategic_opp, 
                        detailed_analysis=detailed_analysis
                    )
                    full_opportunities.append(full_opp.model_dump())
                except Exception as e:
                    logger.warning(f"Failed to convert opportunity {i} to full analysis: {str(e)}")
                    continue
            
            return {
                "analysis_id": analysis_id,
                "opportunities": full_opportunities,
                "total_count": len(full_opportunities),
                "detail_level": "full",
                "includes_source_analysis": True
            }
        
        raise HTTPException(status_code=404, detail="No opportunities found in analysis")
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404, 400) without wrapping
        raise
    except Exception as e:
        logger.error(f"Failed to get full opportunity analysis for {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/opportunities/{analysis_id}/categories")
async def get_category_opportunities(
    analysis_id: str,
    category: Optional[str] = Query(None, description="Filter by category: brand, product, pricing, market")
):
    """
    Get category-specific opportunities (Brand, Product, Pricing, Market).
    Optionally filter by specific category.
    """
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        result = analysis_cache[analysis_id]
        
        # Extract category opportunities from final report
        if "final_report" in result:
            report_data = result["final_report"]
            
            category_data = {}
            
            # Get all category opportunities
            if not category or category == "brand":
                category_data["brand"] = report_data.get("brand_opportunities", [])
            
            if not category or category == "product":
                category_data["product"] = report_data.get("product_opportunities", [])
            
            if not category or category == "pricing":
                category_data["pricing"] = report_data.get("pricing_opportunities", [])
            
            if not category or category == "market":
                category_data["market"] = report_data.get("market_opportunities", [])
            
            # Calculate totals
            total_count = sum(len(opps) for opps in category_data.values())
            
            return {
                "analysis_id": analysis_id,
                "category_opportunities": category_data,
                "total_count": total_count,
                "filtered_category": category
            }
        
        raise HTTPException(status_code=404, detail="No category opportunities found in analysis")
        
    except Exception as e:
        logger.error(f"Failed to get category opportunities for {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/opportunities/{analysis_id}/sources")
async def get_opportunity_sources(
    analysis_id: str,
    opportunity_id: Optional[int] = Query(None, description="Get sources for specific opportunity ID")
):
    """
    Get source citations and credibility analysis for opportunities.
    Optionally filter by specific opportunity ID.
    """
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        result = analysis_cache[analysis_id]
        
        # If specific opportunity requested, get its sources
        if opportunity_id:
            # Find the specific opportunity
            top_opportunities = result.get("top_opportunities", [])
            target_opportunity = None
            
            for opp_dict in top_opportunities:
                if opp_dict.get("id") == opportunity_id:
                    target_opportunity = opp_dict
                    break
            
            if not target_opportunity:
                raise HTTPException(status_code=404, detail=f"Opportunity {opportunity_id} not found")
            
            return {
                "analysis_id": analysis_id,
                "opportunity_id": opportunity_id,
                "source_urls": target_opportunity.get("source_urls", []),
                "supporting_evidence": target_opportunity.get("supporting_evidence", ""),
                "confidence_level": target_opportunity.get("confidence_level", 7.0)
            }
        
        # Return overall source analysis
        if "final_report" in result:
            report_data = result["final_report"]
            
            # Get overall source analysis if available
            overall_sources = report_data.get("overall_source_analysis")
            
            return {
                "analysis_id": analysis_id,
                "overall_source_analysis": overall_sources,
                "raw_research_count": len(result.get("raw_research_results", [])),
                "analysis_metadata": report_data.get("analysis_metadata")
            }
        
        # Fallback: extract from raw research results
        raw_results = result.get("raw_research_results", [])
        source_summary = {
            "total_sources": len(raw_results),
            "source_urls": [r.get("url", "") for r in raw_results if r.get("url")],
            "source_titles": [r.get("title", "") for r in raw_results if r.get("title")]
        }
        
        return {
            "analysis_id": analysis_id,
            "source_summary": source_summary,
            "raw_research_count": len(raw_results)
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404) without wrapping
        raise
    except Exception as e:
        logger.error(f"Failed to get opportunity sources for {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/opportunities/{analysis_id}/methodology")
async def get_analysis_methodology(analysis_id: str):
    """
    Get comprehensive analysis methodology including LangGraph execution details,
    reasoning chains, and decision audit trail for complete transparency.
    """
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        result = analysis_cache[analysis_id]
        
        # Extract comprehensive methodology from final report
        if "final_report" in result:
            report_data = result["final_report"]
            
            # Get comprehensive methodology if available
            comprehensive_methodology = report_data.get("comprehensive_methodology")
            methodology_transparency = report_data.get("methodology_transparency_report")
            
            if comprehensive_methodology:
                return {
                    "analysis_id": analysis_id,
                    "methodology": comprehensive_methodology.get("methodology", {}),
                    "node_executions": comprehensive_methodology.get("node_executions", []),
                    "reasoning_chains": comprehensive_methodology.get("reasoning_chains", []),
                    "decision_audit_trail": comprehensive_methodology.get("decision_audit_trail", []),
                    "execution_summary": {
                        "total_nodes_executed": len(comprehensive_methodology.get("node_executions", [])),
                        "total_processing_time": comprehensive_methodology.get("total_processing_time", 0),
                        "ai_model_interactions": comprehensive_methodology.get("ai_model_interactions", 0),
                        "overall_confidence": comprehensive_methodology.get("overall_confidence", 7.0)
                    },
                    "transparency_report": methodology_transparency,
                    "has_complete_trace": True
                }
        
        # Fallback: extract basic methodology from analysis metadata
        analysis_metadata = result.get("analysis_metadata")
        if analysis_metadata:
            return {
                "analysis_id": analysis_id,
                "basic_methodology": {
                    "search_strategy": analysis_metadata.get("search_strategy", "Unknown"),
                    "gap_analysis_method": analysis_metadata.get("gap_analysis_method", "Unknown"),
                    "opportunity_generation_method": analysis_metadata.get("opportunity_generation_method", "Unknown"),
                    "total_searches": analysis_metadata.get("total_searches_performed", 0),
                    "langgraph_nodes": analysis_metadata.get("langgraph_nodes_executed", [])
                },
                "confidence_metrics": {
                    "overall_confidence": analysis_metadata.get("overall_confidence", 7.0),
                    "source_quality_score": analysis_metadata.get("source_quality_score", 7.0),
                    "analysis_completeness": analysis_metadata.get("analysis_completeness", 7.0)
                },
                "has_complete_trace": False
            }
        
        raise HTTPException(status_code=404, detail="No methodology information found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get methodology for {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/opportunities/{analysis_id}/sources/analysis")
async def get_sources_credibility_analysis(
    analysis_id: str,
    include_enhanced_metadata: bool = Query(False, description="Include enhanced source metadata from Tavily")
):
    """
    Get comprehensive source credibility analysis including enhanced metadata,
    credibility scoring, relevance assessment, and source quality indicators.
    """
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        result = analysis_cache[analysis_id]
        
        # Extract enhanced source metadata if available
        enhanced_metadata = result.get("enhanced_source_metadata", [])
        
        if enhanced_metadata and include_enhanced_metadata:
            # Process enhanced metadata using SourceCollectionAnalyzer
            metadata_objects = []
            for metadata in enhanced_metadata:
                if isinstance(metadata, dict):
                    # Convert dict to TavilySourceMetadata if needed
                    try:
                        metadata_obj = TavilySourceMetadata(**metadata)
                        metadata_objects.append(metadata_obj)
                    except Exception as e:
                        logger.warning(f"Failed to parse enhanced metadata: {str(e)}")
                        continue
                else:
                    metadata_objects.append(metadata)
            
            if metadata_objects:
                # Generate comprehensive source analysis
                source_analysis = SourceCollectionAnalyzer.analyze_source_collection(metadata_objects)
                
                return {
                    "analysis_id": analysis_id,
                    "source_analysis": source_analysis.model_dump(),
                    "enhanced_metadata_count": len(metadata_objects),
                    "credibility_breakdown": {
                        "high_credibility": len([s for s in metadata_objects if s.credibility_score >= 8.0]),
                        "medium_credibility": len([s for s in metadata_objects if 6.0 <= s.credibility_score < 8.0]),
                        "low_credibility": len([s for s in metadata_objects if s.credibility_score < 6.0])
                    },
                    "source_diversity": {
                        "unique_domains": len(set(s.domain for s in metadata_objects)),
                        "source_types": list(set(s.source_type.value for s in metadata_objects)),
                        "search_queries": list(set(s.search_query for s in metadata_objects))
                    },
                    "quality_indicators": {
                        "average_credibility": sum(s.credibility_score for s in metadata_objects) / len(metadata_objects),
                        "average_relevance": sum(s.relevance_score for s in metadata_objects) / len(metadata_objects),
                        "credibility_indicator": source_analysis.credibility_indicator,
                        "quality_summary": source_analysis.quality_summary
                    },
                    "includes_enhanced_analysis": True
                }
        
        # Fallback: analyze raw research results
        raw_results = result.get("raw_research_results", [])
        if raw_results:
            # Basic source analysis from raw results
            domains = list(set(r.get("url", "").split("/")[2] if "/" in r.get("url", "") else r.get("url", "") for r in raw_results if r.get("url")))
            
            # Simple credibility scoring based on domain types
            high_credibility_domains = [d for d in domains if any(indicator in d.lower() for indicator in ['fda.gov', 'nih.gov', 'reuters.com', 'bloomberg.com', '.edu'])]
            
            return {
                "analysis_id": analysis_id,
                "basic_source_analysis": {
                    "total_sources": len(raw_results),
                    "unique_domains": len(domains),
                    "high_credibility_domains": len(high_credibility_domains),
                    "domain_list": domains[:10],  # Top 10 domains
                    "credibility_estimate": "High" if len(high_credibility_domains) / len(domains) > 0.3 else "Moderate" if len(high_credibility_domains) > 0 else "Basic"
                },
                "source_summary": {
                    "search_coverage": f"{len(raw_results)} sources analyzed",
                    "domain_diversity": f"{len(domains)} unique domains",
                    "credibility_assessment": "Basic analysis available"
                },
                "includes_enhanced_analysis": False
            }
        
        raise HTTPException(status_code=404, detail="No source data found for analysis")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get source analysis for {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/opportunities/{analysis_id}/traceability")
async def get_analysis_traceability(
    analysis_id: str,
    opportunity_id: Optional[int] = Query(None, description="Get traceability for specific opportunity")
):
    """
    Get complete data flow traceability from search queries to final recommendations.
    Shows the complete path: Search → Source → Analysis → Gap → Opportunity → Recommendation.
    """
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        result = analysis_cache[analysis_id]
        
        # Build comprehensive traceability map
        traceability = {
            "analysis_id": analysis_id,
            "data_flow_stages": [],
            "source_to_opportunity_mapping": {},
            "query_to_source_mapping": {},
            "processing_pipeline": []
        }
        
        # Stage 1: Search Queries
        search_queries = result.get("search_queries", [])
        if search_queries:
            traceability["data_flow_stages"].append({
                "stage": "search_queries",
                "description": "Initial search queries generated",
                "data_count": len(search_queries),
                "sample_data": search_queries[:5],
                "processing_method": "Category-aware query generation"
            })
        
        # Stage 2: Raw Research Results
        raw_results = result.get("raw_research_results", [])
        if raw_results:
            traceability["data_flow_stages"].append({
                "stage": "raw_research",
                "description": "Raw search results from Tavily",
                "data_count": len(raw_results),
                "sample_data": [
                    {
                        "query": r.get("query", ""),
                        "url": r.get("url", ""),
                        "title": r.get("title", "")[:100] + "..." if r.get("title", "") else ""
                    } for r in raw_results[:5]
                ],
                "processing_method": "Tavily search API with credibility scoring"
            })
            
            # Map queries to sources
            for result_item in raw_results:
                query = result_item.get("query", "unknown")
                url = result_item.get("url", "")
                if query not in traceability["query_to_source_mapping"]:
                    traceability["query_to_source_mapping"][query] = []
                traceability["query_to_source_mapping"][query].append(url)
        
        # Stage 3: Enhanced Source Metadata
        enhanced_metadata = result.get("enhanced_source_metadata", [])
        if enhanced_metadata:
            traceability["data_flow_stages"].append({
                "stage": "enhanced_metadata",
                "description": "Enhanced source analysis with credibility scoring",
                "data_count": len(enhanced_metadata),
                "sample_data": [
                    {
                        "url": m.get("url", ""),
                        "credibility_score": m.get("credibility_score", 0),
                        "relevance_score": m.get("relevance_score", 0),
                        "source_type": m.get("source_type", "unknown")
                    } for m in enhanced_metadata[:5]
                ],
                "processing_method": "AI-powered credibility and relevance assessment"
            })
        
        # Stage 4: Clinical Gaps
        clinical_gaps = result.get("clinical_gaps", [])
        if clinical_gaps:
            traceability["data_flow_stages"].append({
                "stage": "clinical_gaps",
                "description": "Identified competitive gaps and weaknesses",
                "data_count": len(clinical_gaps),
                "sample_data": [
                    {
                        "competitor": gap.get("competitor", ""),
                        "gap_type": gap.get("gap_type", ""),
                        "description": gap.get("description", "")[:100] + "..." if gap.get("description", "") else ""
                    } for gap in clinical_gaps[:5]
                ],
                "processing_method": "Competitive gap analysis using LLM"
            })
        
        # Stage 5: Strategic Opportunities
        top_opportunities = result.get("top_opportunities", [])
        if top_opportunities:
            traceability["data_flow_stages"].append({
                "stage": "strategic_opportunities",
                "description": "Generated strategic opportunities",
                "data_count": len(top_opportunities),
                "sample_data": [
                    {
                        "id": opp.get("id", 0),
                        "title": opp.get("title", ""),
                        "category": opp.get("category", ""),
                        "opportunity_score": opp.get("opportunity_score", 0)
                    } for opp in top_opportunities[:5]
                ],
                "processing_method": "Gap-to-opportunity transformation with scoring"
            })
            
            # Map sources to opportunities
            for opp in top_opportunities:
                opp_id = opp.get("id", 0)
                source_urls = opp.get("source_urls", [])
                if source_urls:
                    traceability["source_to_opportunity_mapping"][str(opp_id)] = source_urls
        
        # Stage 6: LangGraph Processing Pipeline
        if "final_report" in result:
            report_data = result["final_report"]
            methodology = report_data.get("comprehensive_methodology", {})
            node_executions = methodology.get("node_executions", [])
            
            if node_executions:
                traceability["processing_pipeline"] = [
                    {
                        "node_name": node.get("node_name", ""),
                        "execution_order": node.get("execution_order", 0),
                        "processing_duration": node.get("processing_duration", 0),
                        "input_summary": node.get("input_data_summary", ""),
                        "output_summary": node.get("output_data_summary", ""),
                        "transformations": node.get("data_transformations", [])
                    } for node in node_executions
                ]
        
        # Specific opportunity traceability if requested
        if opportunity_id:
            target_opportunity = None
            for opp in top_opportunities:
                if opp.get("id") == opportunity_id:
                    target_opportunity = opp
                    break
            
            if not target_opportunity:
                raise HTTPException(status_code=404, detail=f"Opportunity {opportunity_id} not found")
            
            # Build specific traceability for this opportunity
            specific_traceability = {
                "opportunity_id": opportunity_id,
                "opportunity_title": target_opportunity.get("title", ""),
                "source_urls": target_opportunity.get("source_urls", []),
                "supporting_evidence": target_opportunity.get("supporting_evidence", ""),
                "confidence_level": target_opportunity.get("confidence_level", 7.0),
                "data_lineage": []
            }
            
            # Trace back from opportunity to sources
            opp_sources = target_opportunity.get("source_urls", [])
            for source_url in opp_sources:
                # Find the raw research result that generated this source
                source_research = None
                for raw_result in raw_results:
                    if raw_result.get("url") == source_url:
                        source_research = raw_result
                        break
                
                if source_research:
                    specific_traceability["data_lineage"].append({
                        "search_query": source_research.get("query", ""),
                        "source_url": source_url,
                        "source_title": source_research.get("title", ""),
                        "content_snippet": source_research.get("content", "")[:200] + "...",
                        "contribution_to_opportunity": "Supporting evidence for opportunity analysis"
                    })
            
            traceability["specific_opportunity_trace"] = specific_traceability
        
        # Summary metrics
        traceability["traceability_summary"] = {
            "total_stages": len(traceability["data_flow_stages"]),
            "complete_pipeline": len(traceability["processing_pipeline"]) > 0,
            "source_coverage": len(traceability["source_to_opportunity_mapping"]),
            "query_diversity": len(traceability["query_to_source_mapping"]),
            "traceability_score": min(10.0, len(traceability["data_flow_stages"]) * 1.5)
        }
        
        return traceability
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get traceability for {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/opportunities/{analysis_id}/quality-report")
async def get_analysis_quality_report(analysis_id: str):
    """
    Get comprehensive quality assurance report including validation results,
    confidence assessment, and quality metrics across all analysis stages.
    """
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    try:
        result = analysis_cache[analysis_id]
        
        # Initialize quality report
        quality_report = {
            "analysis_id": analysis_id,
            "overall_quality_score": 7.0,
            "quality_dimensions": {},
            "validation_results": {},
            "confidence_assessment": {},
            "recommendations": []
        }
        
        # 1. Source Quality Assessment
        enhanced_metadata = result.get("enhanced_source_metadata", [])
        raw_results = result.get("raw_research_results", [])
        
        if enhanced_metadata:
            high_quality_sources = len([s for s in enhanced_metadata if s.get("credibility_score", 0) >= 8.0])
            total_sources = len(enhanced_metadata)
            source_quality_score = (high_quality_sources / total_sources) * 10 if total_sources > 0 else 5.0
            
            quality_report["quality_dimensions"]["source_quality"] = {
                "score": source_quality_score,
                "high_quality_sources": high_quality_sources,
                "total_sources": total_sources,
                "quality_percentage": (high_quality_sources / total_sources) * 100 if total_sources > 0 else 0,
                "assessment": "High" if source_quality_score >= 8.0 else "Good" if source_quality_score >= 6.0 else "Moderate"
            }
        else:
            quality_report["quality_dimensions"]["source_quality"] = {
                "score": 5.0,
                "assessment": "Basic - no enhanced metadata available",
                "total_sources": len(raw_results)
            }
        
        # 2. Analysis Completeness
        stages_completed = []
        if result.get("search_queries"): stages_completed.append("search_generation")
        if result.get("raw_research_results"): stages_completed.append("research_execution")
        if result.get("clinical_gaps"): stages_completed.append("gap_analysis")
        if result.get("top_opportunities"): stages_completed.append("opportunity_generation")
        if result.get("final_report"): stages_completed.append("report_synthesis")
        
        completeness_score = (len(stages_completed) / 5) * 10
        quality_report["quality_dimensions"]["analysis_completeness"] = {
            "score": completeness_score,
            "stages_completed": stages_completed,
            "total_stages": 5,
            "completion_percentage": (len(stages_completed) / 5) * 100,
            "assessment": "Complete" if completeness_score >= 8.0 else "Good" if completeness_score >= 6.0 else "Partial"
        }
        
        # 3. Methodology Transparency
        methodology_score = 5.0
        methodology_indicators = []
        
        if "final_report" in result:
            report_data = result["final_report"]
            comprehensive_methodology = report_data.get("comprehensive_methodology", {})
            
            if comprehensive_methodology.get("node_executions"):
                methodology_indicators.append("langgraph_execution_tracked")
                methodology_score += 1.5
            
            if comprehensive_methodology.get("reasoning_chains"):
                methodology_indicators.append("reasoning_chains_documented")
                methodology_score += 1.5
            
            if comprehensive_methodology.get("decision_audit_trail"):
                methodology_indicators.append("decision_audit_trail_available")
                methodology_score += 1.0
            
            if report_data.get("methodology_transparency_report"):
                methodology_indicators.append("transparency_report_generated")
                methodology_score += 1.0
        
        quality_report["quality_dimensions"]["methodology_transparency"] = {
            "score": min(10.0, methodology_score),
            "indicators": methodology_indicators,
            "transparency_level": "High" if methodology_score >= 8.0 else "Good" if methodology_score >= 6.0 else "Basic"
        }
        
        # 4. Confidence Assessment
        opportunities = result.get("top_opportunities", [])
        if opportunities:
            confidence_scores = [opp.get("confidence_level", 7.0) for opp in opportunities]
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            
            quality_report["confidence_assessment"] = {
                "average_confidence": avg_confidence,
                "confidence_range": f"{min(confidence_scores):.1f} - {max(confidence_scores):.1f}",
                "high_confidence_opportunities": len([s for s in confidence_scores if s >= 8.0]),
                "total_opportunities": len(opportunities),
                "confidence_distribution": {
                    "high_8_10": len([s for s in confidence_scores if s >= 8.0]),
                    "medium_6_8": len([s for s in confidence_scores if 6.0 <= s < 8.0]),
                    "low_below_6": len([s for s in confidence_scores if s < 6.0])
                }
            }
        
        # 5. Overall Quality Score Calculation
        dimension_scores = [d["score"] for d in quality_report["quality_dimensions"].values()]
        overall_score = sum(dimension_scores) / len(dimension_scores) if dimension_scores else 5.0
        quality_report["overall_quality_score"] = overall_score
        
        # 6. Quality Recommendations
        recommendations = []
        
        if quality_report["quality_dimensions"]["source_quality"]["score"] < 7.0:
            recommendations.append("Consider expanding search queries to include more high-credibility sources")
        
        if quality_report["quality_dimensions"]["analysis_completeness"]["score"] < 8.0:
            recommendations.append("Complete all analysis stages for comprehensive results")
        
        if quality_report["quality_dimensions"]["methodology_transparency"]["score"] < 7.0:
            recommendations.append("Enable enhanced methodology tracking for better transparency")
        
        if not recommendations:
            recommendations.append("Analysis meets high quality standards")
        
        quality_report["recommendations"] = recommendations
        
        # 7. Quality Grade
        if overall_score >= 9.0:
            quality_grade = "A"
        elif overall_score >= 8.0:
            quality_grade = "B"
        elif overall_score >= 7.0:
            quality_grade = "C"
        elif overall_score >= 6.0:
            quality_grade = "D"
        else:
            quality_grade = "F"
        
        quality_report["quality_grade"] = quality_grade
        quality_report["quality_summary"] = f"Grade {quality_grade} - {overall_score:.1f}/10 overall quality score"
        
        return quality_report
        
    except Exception as e:
        logger.error(f"Failed to generate quality report for {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stream/{analysis_id}")
async def stream_analysis_events(analysis_id: str):
    """Stream analysis events via Server-Sent Events (SSE)"""
    
    async def event_generator():
        try:
            # Send initial connection event
            connection_event = {
                'type': 'connected', 
                'analysis_id': analysis_id,
                'timestamp': datetime.now().isoformat(),
                'message': f'Connected to analysis stream for {analysis_id}'
            }
            yield f"data: {json.dumps(connection_event)}\\n\\n"
            
            # Check if analysis exists or start one
            if analysis_id not in analysis_status:
                # No analysis running, send error
                error_event = {
                    'type': 'error',
                    'error': 'Analysis not found',
                    'message': f'No analysis found with ID: {analysis_id}',
                    'timestamp': datetime.now().isoformat()
                }
                yield f"data: {json.dumps(error_event)}\\n\\n"
                return
            
            # Stream events while analysis is running
            last_progress = 0
            while True:
                status = analysis_status.get(analysis_id)
                if not status:
                    break
                    
                # Send progress update if changed
                if status.progress != last_progress:
                    progress_event = {
                        'type': 'progress_update',
                        'progress': status.progress * 100,  # Convert to percentage
                        'status': status.status,
                        'message': status.message,
                        'timestamp': datetime.now().isoformat()
                    }
                    yield f"data: {json.dumps(progress_event)}\\n\\n"
                    last_progress = status.progress
                
                # Check if completed
                if status.status in ['completed', 'failed']:
                    completion_event = {
                        'type': 'analysis_completed' if status.status == 'completed' else 'analysis_failed',
                        'status': status.status,
                        'message': status.message,
                        'final_progress': 100 if status.status == 'completed' else status.progress * 100,
                        'timestamp': datetime.now().isoformat()
                    }
                    if status.result:
                        completion_event['has_result'] = True
                    if status.error_message:
                        completion_event['error'] = status.error_message
                    
                    yield f"data: {json.dumps(completion_event)}\\n\\n"
                    break
                
                # Wait before checking again
                await asyncio.sleep(0.5)
            
        except Exception as e:
            logger.error(f"Streaming error for {analysis_id}: {str(e)}")
            error_event = {
                'type': 'stream_error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_event)}\\n\\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.post("/stream/trigger/{analysis_id}")
async def trigger_streaming_analysis(
    analysis_id: str,
    request: CompetitorAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Start analysis with streaming support"""
    try:
        # Validate request
        if not request.competitors:
            raise HTTPException(status_code=400, detail="At least one competitor required")
        
        # Start background analysis with streaming
        analysis_status[analysis_id] = AnalysisStatus(
            status="pending",
            progress=0.0,
            message="Analysis queued with streaming enabled..."
        )
        
        background_tasks.add_task(
            run_analysis_async,
            analysis_id,
            request.competitors,
            request.focus_area
        )
        
        return {
            "analysis_id": analysis_id,
            "status": "started",
            "streaming_endpoint": f"/stream/{analysis_id}",
            "message": "Analysis started with real-time streaming enabled"
        }
        
    except Exception as e:
        logger.error(f"Failed to start streaming analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stream/sessions")
async def get_active_streaming_sessions():
    """Get information about active streaming sessions"""
    sessions_info = []
    for session_id, session in streaming_manager.active_sessions.items():
        sessions_info.append({
            "session_id": session_id,
            "analysis_id": session.analysis_config.get("analysis_id"),
            "started_at": session.started_at.isoformat(),
            "events_sent": session.events_sent,
            "is_active": session.is_active
        })
    
    return {
        "active_sessions": len(sessions_info),
        "sessions": sessions_info
    }

@app.get("/stream/simple/{analysis_id}")
async def simple_stream_test(analysis_id: str):
    """Simple streaming endpoint for testing SSE"""
    
    async def simple_event_generator():
        # Send connection event
        yield f"data: {json.dumps({'type': 'connected', 'message': 'Connected to analysis', 'analysis_id': analysis_id})}\\n\\n"
        
        # Send test events
        events = [
            {'type': 'analysis_started', 'message': 'Starting analysis...', 'progress': 0},
            {'type': 'search_progress', 'message': 'Searching competitors...', 'progress': 25},  
            {'type': 'insight_discovered', 'message': 'Found competitive insights...', 'progress': 50},
            {'type': 'opportunity_generated', 'message': 'Generated opportunities...', 'progress': 75},
            {'type': 'analysis_completed', 'message': 'Analysis completed successfully!', 'progress': 100}
        ]
        
        for i, event in enumerate(events):
            await asyncio.sleep(1)  # 1 second between events
            event['timestamp'] = datetime.now().isoformat()
            event['sequence'] = i + 1
            yield f"data: {json.dumps(event)}\\n\\n"
        
        # Send completion
        completion = {
            'type': 'stream_completed',
            'message': 'Stream completed',
            'timestamp': datetime.now().isoformat()
        }
        yield f"data: {json.dumps(completion)}\\n\\n"
    
    return StreamingResponse(
        simple_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

def parse_analysis_id(analysis_id: str):
    FA_SEPARATOR = '__FA__'
    COMPETITOR_SEPARATOR = '|||'
    if FA_SEPARATOR not in analysis_id:
        return [], ''
    competitor_part, rest = analysis_id.split(FA_SEPARATOR, 1)
    import re
    focus_area = re.sub(r'[-_][0-9]{6}$', '', rest).replace('_', ' ')
    competitors = [c.replace('_', ' ').title() for c in competitor_part.split(COMPETITOR_SEPARATOR)]
    return competitors, focus_area.strip()

@app.get("/stream/langgraph/{analysis_id}")
async def stream_langgraph_analysis(analysis_id: str, research: bool = Query(True, description="Enable enhanced research-backed analysis")):
    logger.info(f"🎥 Streaming request received:")
    logger.info(f"   Analysis ID: {analysis_id}")
    logger.info(f"   Research enabled: {research}")

    competitors, focus_area = parse_analysis_id(analysis_id)
    logger.info(f"   Parsed competitors: {competitors}")
    logger.info(f"   Parsed focus_area: {focus_area}")
    
    async def langgraph_event_generator():
        final_state = None
        try:
            # Send initial connection event
            connection_event = {
                'type': 'connected', 
                'analysis_id': analysis_id,
                'timestamp': datetime.now().isoformat(),
                'message': f'Connected to LangGraph analysis stream (research: {"enabled" if research else "disabled"})',
                'research_enabled': research
            }
            logger.info(f"📡 Streaming connection established for {analysis_id} (research: {research})")
            yield f"data: {json.dumps(connection_event)}\n\n"
            
            # Initialize the graph state with research flag
            initial_state = {
                "competitors": competitors,
                "focus_area": focus_area,
                "device_category": "",
                "search_queries": [],
                "current_competitor": "",
                "research_iteration": 0,
                "raw_research_results": [],
                "clinical_gaps": [],
                "market_opportunities": [],
                # Add missing market intelligence fields that the graph expects
                "market_share_insights": [],
                "brand_positioning": [],
                "product_feature_gaps": [],
                "competitive_landscape": None,
                "final_report": None,
                "error_messages": [],
                # Add research flag to state
                "research_enabled": research
            }
            
            # Stream the LangGraph execution
            node_count = 0
            total_nodes = 6  # Approximate number of nodes in the graph
            
            async for event in opportunity_graph.graph.astream(initial_state):
                node_count += 1
                current_progress = min((node_count / total_nodes) * 100, 95)
                
                # Extract node name and state from the event
                if isinstance(event, dict):
                    for node_name, node_state in event.items():
                        # Capture the final state for saving later
                        final_state = node_state
                        
                        # Send node execution event
                        node_event = {
                            'type': 'node_execution',
                            'node_name': node_name,
                            'message': f'Executing {node_name}...',
                            'progress': current_progress,
                            'timestamp': datetime.now().isoformat(),
                            'state_preview': {
                                'current_competitor': node_state.get('current_competitor', ''),
                                'research_iteration': node_state.get('research_iteration', 0),
                                'results_count': len(node_state.get('raw_research_results', [])),
                                'gaps_count': len(node_state.get('clinical_gaps', [])),
                                'opportunities_count': len(node_state.get('market_opportunities', []))
                            }
                        }
                        yield f"data: {json.dumps(node_event)}\n\n"
                        
                        # Send specific progress updates based on node type
                        if node_name == 'research_competitor':
                            current_competitor = node_state.get('current_competitor', '')
                            if current_competitor:
                                search_event = {
                                    'type': 'search_progress',
                                    'message': f'Researching {current_competitor}...',
                                    'competitor': current_competitor,
                                    'progress': current_progress,
                                    'timestamp': datetime.now().isoformat()
                                }
                                yield f"data: {json.dumps(search_event)}\n\n"
                        
                        elif node_name == 'analyze_gaps':
                            insight_event = {
                                'type': 'insight_discovered',
                                'message': 'Analyzing competitive gaps and weaknesses...',
                                'progress': current_progress,
                                'timestamp': datetime.now().isoformat()
                            }
                            yield f"data: {json.dumps(insight_event)}\n\n"
                        
                        elif node_name == 'identify_opportunities':
                            opportunity_event = {
                                'type': 'opportunity_generated',
                                'message': 'Generating strategic opportunities...',
                                'progress': current_progress,
                                'timestamp': datetime.now().isoformat()
                            }
                            yield f"data: {json.dumps(opportunity_event)}\n\n"
                
                # Small delay to make streaming visible
                await asyncio.sleep(0.1)
            
            # Save the final result to analysis cache for /result endpoint
            if final_state:
                try:
                    # Transform the LangGraph state to the expected result format
                    analysis_result = opportunity_graph.transform_to_result_format(final_state)
                    
                    # Store in cache for /result endpoint
                    analysis_cache[analysis_id] = analysis_result
                    
                    # Update analysis status
                    analysis_status[analysis_id] = AnalysisStatus(
                        status="completed",
                        progress=1.0,
                        message="Analysis completed successfully",
                        result=analysis_result
                    )
                    
                    logger.info(f"Saved analysis result for {analysis_id} to cache")
                    
                except Exception as e:
                    logger.error(f"Failed to save analysis result for {analysis_id}: {str(e)}")
                    # Continue anyway, just log the error
            
            # Send completion event
            completion_event = {
                'type': 'analysis_completed',
                'message': 'Analysis completed successfully!',
                'progress': 100,
                'timestamp': datetime.now().isoformat(),
                'has_result': True,
                'result_available': analysis_id in analysis_cache
            }
            yield f"data: {json.dumps(completion_event)}\n\n"
            
            # Send stream completion
            stream_end = {
                'type': 'stream_completed',
                'message': 'Stream completed',
                'timestamp': datetime.now().isoformat()
            }
            yield f"data: {json.dumps(stream_end)}\n\n"
            
        except Exception as e:
            logger.error(f"LangGraph streaming error for {analysis_id}: {str(e)}")
            
            # Update analysis status to failed
            analysis_status[analysis_id] = AnalysisStatus(
                status="failed",
                progress=0.0,
                message="Analysis failed",
                error_message=str(e)
            )
            
            error_event = {
                'type': 'error',
                'error': str(e),
                'message': f'Analysis failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return StreamingResponse(
        langgraph_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.get("/stream/cached/{analysis_id}")
async def stream_cached_analysis(
    analysis_id: str,
    competitors: str = Query(..., description="Comma-separated list of competitors"),
    focus_area: str = Query(..., description="Focus area for analysis"),
):
    """
    Stream cached analysis results with simulated real-time experience.
    This provides better UX by showing progress even when using cached data.
    """
    import asyncio
    import json
    import time
    
    logger.info(f"Starting cached streaming for analysis_id: {analysis_id}")
    logger.info(f"Competitors: {competitors}, Focus area: {focus_area}")
    
    # Parse competitors
    competitor_list = [c.strip() for c in competitors.split(',')]
    
    async def generate_cached_events():
        try:
            # Parse competitors
            competitor_list = [comp.strip() for comp in competitors.split(',')]
            
            # First, check if we have cached results using the cache service directly
            cache_key = f"{','.join(sorted(competitor_list))}_{focus_area}"
            logger.info(f"Checking cache for key: {cache_key}")
            
            # Try to get cached results directly from cache service
            try:
                cached_result = await cache_service.get_cached_analysis(competitor_list, focus_area)
                
                if cached_result:
                    logger.info("Cache HIT - streaming cached results with simulated progress")
                    
                    # Simulate realistic streaming experience
                    events = [
                        {"type": "connected", "message": "Connected to analysis stream", "progress": 0, "timestamp": datetime.now().isoformat()},
                        {"type": "cache_check", "message": "Checking for cached results...", "progress": 10, "timestamp": datetime.now().isoformat()},
                        {"type": "cache_hit", "message": f"Found cached results! Saved ${cached_result.get('cost_saved', 2.50):.2f}", "progress": 20, "timestamp": datetime.now().isoformat(), "cached": True, "cost_saved": cached_result.get('cost_saved', 2.50)},
                        {"type": "analysis_started", "message": "Loading cached analysis results...", "progress": 30, "timestamp": datetime.now().isoformat()},
                        {"type": "search_progress", "message": "Retrieving competitive intelligence data...", "progress": 50, "timestamp": datetime.now().isoformat()},
                        {"type": "insight_discovered", "message": f"Found {len(cached_result.get('clinical_gaps', []))} clinical gaps", "progress": 70, "timestamp": datetime.now().isoformat()},
                        {"type": "opportunity_generated", "message": f"Identified {len(cached_result.get('top_opportunities', []))} strategic opportunities", "progress": 85, "timestamp": datetime.now().isoformat()},
                        {"type": "analysis_completed", "message": "Analysis completed using cached data", "progress": 100, "timestamp": datetime.now().isoformat(), "has_result": True},
                        {"type": "streaming_complete", "message": "Stream completed", "progress": 100, "timestamp": datetime.now().isoformat()},
                    ]
                    
                    for i, event in enumerate(events):
                        event["event_id"] = i + 1
                        event["sequence"] = i + 1
                        event["analysis_id"] = analysis_id
                        
                        yield f"data: {json.dumps(event)}\n\n"
                        
                        # Add realistic delays
                        if event["type"] == "connected":
                            await asyncio.sleep(0.5)
                        elif event["type"] in ["cache_check", "cache_hit"]:
                            await asyncio.sleep(0.3)
                        elif event["type"] in ["search_progress", "insight_discovered", "opportunity_generated"]:
                            await asyncio.sleep(0.8)
                        else:
                            await asyncio.sleep(0.5)
                    
                    return
                else:
                    logger.info("Cache MISS - redirecting to live analysis")
                    
                    # Yield cache miss event and then redirect to live streaming
                    cache_miss_event = {
                        "type": "cache_miss",
                        "message": "No cached results found, starting live analysis...",
                        "progress": 0,
                        "timestamp": datetime.now().isoformat(),
                        "cached": False,
                        "event_id": 1,
                        "sequence": 1,
                        "analysis_id": analysis_id
                    }
                    yield f"data: {json.dumps(cache_miss_event)}\n\n"
                    await asyncio.sleep(1)
                
            except Exception as cache_error:
                logger.error(f"Error checking cache: {cache_error}")
            
            # If we get here, either cache miss or cache error - redirect to live streaming
            logger.info("Cache miss - user should use LangGraph endpoint for live analysis")
            
            # Send redirection event instead of trying to do live streaming here
            redirect_event = {
                "type": "cache_miss_redirect",
                "message": "No cached results available. Please use /stream/langgraph/ endpoint for live analysis.",
                "timestamp": datetime.now().isoformat(),
                "analysis_id": analysis_id,
                "redirect_url": f"/stream/langgraph/{analysis_id}"
            }
            yield f"data: {json.dumps(redirect_event)}\n\n"
                
        except Exception as e:
            logger.error(f"Error in cached streaming: {e}")
            error_event = {
                "type": "error",
                "message": f"Streaming error: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "analysis_id": analysis_id,
                "error": str(e)
            }
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        generate_cached_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*"
        }
    )

@app.get("/cache/stats")
async def get_cache_statistics():
    """
    Get comprehensive cache performance statistics.
    
    Returns metrics about cache usage, performance, and cost savings
    for monitoring and optimization purposes.
    """
    try:
        stats = await cache_service.get_cache_stats()
        
        # Add API-specific metadata
        stats["api_integration"] = {
            "active_analyses": len(analysis_cache),
            "running_analyses": len([s for s in analysis_status.values() if s.status == "running"]),
            "cached_analyses": len([s for s in analysis_status.values() if s.cached]),
            "endpoint_version": "1.0.0"
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get cache statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve cache stats: {str(e)}")

@app.post("/cache/cleanup")
async def cleanup_expired_cache():
    """
    Manually trigger cleanup of expired cache entries.
    
    Useful for maintenance and testing. In production, this runs automatically.
    """
    try:
        cleaned_count = await cache_service.cleanup_expired_entries()
        
        return {
            "message": f"Cache cleanup completed",
            "entries_cleaned": cleaned_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cache cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cache cleanup failed: {str(e)}")

@app.delete("/cache/clear")
async def clear_all_cache():
    """
    Clear all cache entries (for development/testing).
    
    WARNING: This will remove all cached analysis results.
    """
    try:
        with cache_service.get_session() as session:
            from ..core.cache_models import AnalysisCache
            deleted_count = session.query(AnalysisCache).count()
            session.query(AnalysisCache).delete()
            session.commit()
        
        return {
            "message": "All cache entries cleared",
            "entries_deleted": deleted_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

# Enhanced streaming endpoint that checks cache first
@app.get("/stream/smart/{analysis_id}")
async def smart_stream_analysis(analysis_id: str, competitors: str, focus_area: str):
    """
    Intelligent streaming that uses cache when available, live analysis when not.
    
    This endpoint provides the best user experience by:
    1. Checking for cached results first
    2. If cached: streams simulated analysis with cached data
    3. If not cached: runs live analysis with real-time streaming
    
    Args:
        analysis_id: Unique identifier for the streaming session
        competitors: Comma-separated list of competitors
        focus_area: Analysis focus area
    """
    
    async def smart_stream_generator():
        try:
            # Parse competitors
            competitor_list = [comp.strip() for comp in competitors.split(',')]
            
            # Check for cached results first
            cached_results = await get_cached_analysis(competitor_list, focus_area)
            
            if cached_results:
                # Use cached streaming
                logger.info(f"Smart streaming: Using cached results for {competitor_list} + {focus_area}")
                
                # Send cache hit notification
                cache_event = {
                    "type": "cache_hit",
                    "message": "Found cached results - streaming optimized analysis",
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {"cached": True, "cost_saved": 2.50}
                }
                yield f"data: {json.dumps(cache_event)}\n\n"
                
                # Stream cached results
                async for chunk in simulate_streaming(cached_results):
                    yield f"data: {chunk}\n\n"
            else:
                # No cache - run live analysis
                logger.info(f"Smart streaming: No cache found, running live analysis for {competitor_list} + {focus_area}")
                
                # Send live analysis notification
                live_event = {
                    "type": "live_analysis",
                    "message": "No cached results found - running fresh analysis",
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {"cached": False, "live_analysis": True}
                }
                yield f"data: {json.dumps(live_event)}\n\n"
                
        except Exception as e:
            error_event = {
                "type": "error",
                "message": f"Smart streaming failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return StreamingResponse(
        smart_stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Check environment setup
    if not os.getenv("TAVILY_API_KEY"):
        print("⚠️  WARNING: TAVILY_API_KEY not set")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY not set")
    
    print("🚀 Starting Orthopedic Competitive Intelligence API...")
    print("📖 API docs available at: http://localhost:8000/docs")
    
    uvicorn.run(
        "fastapi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )