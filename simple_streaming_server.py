#!/usr/bin/env python3
"""
Simple standalone streaming server for testing SSE functionality
"""

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from datetime import datetime
import uvicorn

app = FastAPI(title="Simple Streaming Test Server")

# Enhanced CORS configuration for SSE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],  # Explicit frontend origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*", "Cache-Control", "Content-Type", "Authorization"],
)

@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle OPTIONS preflight requests"""
    return {
        "message": "OK",
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Cache-Control, Content-Type, Authorization"
        }
    }

@app.get("/")
async def root():
    return {"message": "Simple Streaming Test Server", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/stream/{analysis_id}")
async def stream_events(analysis_id: str):
    """Simple streaming endpoint with enhanced CORS and SSE headers"""
    
    async def event_generator():
        try:
            # Send connection event
            connection_event = {
                'type': 'connected',
                'analysis_id': analysis_id,
                'timestamp': datetime.now().isoformat()
            }
            yield f"data: {json.dumps(connection_event)}\\n\\n"
            
            # Send some test events
            events = [
                {'type': 'analysis_started', 'message': 'Starting analysis...', 'progress': 0},
                {'type': 'search_progress', 'message': 'Searching for competitors...', 'progress': 25},
                {'type': 'insight_discovered', 'message': 'Found competitive gap...', 'progress': 50},
                {'type': 'opportunity_generated', 'message': 'Generated opportunity...', 'progress': 75},
                {'type': 'analysis_completed', 'message': 'Analysis complete!', 'progress': 100}
            ]
            
            for i, event_data in enumerate(events):
                await asyncio.sleep(2)  # Wait 2 seconds between events
                
                event = {
                    **event_data,
                    'timestamp': datetime.now().isoformat(),
                    'event_id': i + 1,
                    'analysis_id': analysis_id
                }
                
                yield f"data: {json.dumps(event)}\\n\\n"
                
                # If this is the last event, break
                if i == len(events) - 1:
                    break
            
            # Send completion event
            completion_event = {
                'type': 'stream_complete',
                'message': 'Stream completed successfully',
                'analysis_id': analysis_id,
                'timestamp': datetime.now().isoformat()
            }
            yield f"data: {json.dumps(completion_event)}\\n\\n"
            
        except Exception as e:
            error_event = {
                'type': 'error',
                'message': f'Streaming error: {str(e)}',
                'analysis_id': analysis_id,
                'timestamp': datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_event)}\\n\\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            # SSE Headers
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
            # CORS Headers (explicit for SSE)
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Cache-Control, Content-Type, Last-Event-ID",
            "Access-Control-Expose-Headers": "Content-Type, Cache-Control"
        }
    )

@app.post("/trigger/{analysis_id}")
async def trigger_analysis(analysis_id: str, request: dict):
    """Simple trigger endpoint"""
    return {
        "analysis_id": analysis_id,
        "status": "started",
        "message": "Analysis triggered - check /stream/{analysis_id} for updates",
        "streaming_endpoint": f"/stream/{analysis_id}"
    }

@app.post("/stream/trigger/{analysis_id}")
async def trigger_streaming_analysis(analysis_id: str, request: dict):
    """Trigger endpoint that immediately starts streaming"""
    return {
        "analysis_id": analysis_id,
        "status": "started",
        "message": "Analysis triggered - streaming will begin immediately",
        "streaming_endpoint": f"/stream/{analysis_id}"
    }

if __name__ == "__main__":
    print("🚀 Starting Simple Streaming Test Server...")
    print("📖 Test at: http://localhost:8001/stream/test-123")
    
    uvicorn.run(
        "simple_streaming_server:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    ) 