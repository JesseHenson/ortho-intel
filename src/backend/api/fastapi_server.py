# fastapi_server.py
"""
FastAPI server for orthopedic competitive intelligence API
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from typing import Dict, Any, List, Optional, Union
import logging
import os

from ..core.data_models import CompetitorAnalysisRequest, CompetitorAnalysisResponse
from ..pipelines.main_langgraph import intelligence_graph

# Import opportunity models for new endpoints
from ..core.opportunity_data_models import (
    OpportunitySummary, OpportunityDetail, OpportunityFull,
    OpportunityAnalysisResponse, OpportunityDisclosureTransformer,
    CategoryOpportunity, StrategicOpportunity
)
from ..core.source_models import DetailLevel, SourceAnalysisResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Orthopedic Competitive Intelligence API",
    description="AI-powered competitive analysis for orthopedic device manufacturers",
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

# In-memory storage for analysis results (in production, use proper database)
analysis_cache: Dict[str, Dict[str, Any]] = {}

class AnalysisStatus(BaseModel):
    """Model for analysis status tracking"""
    status: str  # "pending", "running", "completed", "failed"
    progress: float  # 0.0 to 1.0
    message: str
    result: Dict[str, Any] = None
    error_message: str = None

# Global status tracking
analysis_status: Dict[str, AnalysisStatus] = {}

def generate_analysis_id(competitors: list, focus_area: str) -> str:
    """Generate unique ID for analysis request"""
    competitor_str = "-".join(sorted(competitors))
    return f"{competitor_str}_{focus_area}".replace(" ", "_").lower()

async def run_analysis_async(analysis_id: str, competitors: list, focus_area: str):
    """Run analysis asynchronously with status updates"""
    try:
        # Update status to running
        analysis_status[analysis_id] = AnalysisStatus(
            status="running",
            progress=0.1,
            message="Starting competitive analysis..."
        )
        
        # Execute analysis (this will take time)
        logger.info(f"Starting analysis {analysis_id} for {competitors}")
        
        # Update progress
        analysis_status[analysis_id].progress = 0.3
        analysis_status[analysis_id].message = "Researching competitors..."
        
        # Run the actual analysis
        result = intelligence_graph.run_analysis(competitors, focus_area)
        
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
    if analysis_id not in analysis_cache:
        # Check if it's still running
        if analysis_id in analysis_status:
            status = analysis_status[analysis_id]
            if status.status == "running":
                raise HTTPException(status_code=202, detail="Analysis still running")
            elif status.status == "failed":
                raise HTTPException(status_code=500, detail=status.error_message)
        
        raise HTTPException(status_code=404, detail="Analysis result not found")
    
    return analysis_cache[analysis_id]

@app.post("/analyze-gaps-sync", response_model=Dict[str, Any])
async def analyze_competitor_gaps_sync(request: CompetitorAnalysisRequest):
    """
    Synchronous competitor analysis (for testing/development)
    WARNING: This will block until analysis is complete
    """
    try:
        logger.info(f"Starting synchronous analysis for {request.competitors}")
        
        # Run analysis synchronously
        result = intelligence_graph.run_analysis(
            competitors=request.competitors,
            focus_area=request.focus_area
        )
        
        logger.info("Synchronous analysis completed")
        return result
        
    except Exception as e:
        logger.error(f"Synchronous analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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