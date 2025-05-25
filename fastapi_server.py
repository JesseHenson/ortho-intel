# fastapi_server.py
"""
FastAPI server for orthopedic competitive intelligence API
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from typing import Dict, Any
import logging
import os

from data_models import CompetitorAnalysisRequest, CompetitorAnalysisResponse
from main_langgraph import intelligence_graph

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