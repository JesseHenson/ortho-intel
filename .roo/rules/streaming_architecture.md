---
description: 
globs: 
alwaysApply: false
---
# Streaming Architecture Rules

## **Core Principles**

### **Communication Patterns**
- **Use Server-Sent Events (SSE)** for one-way streaming from server to client
- **Implement WebSockets** only when bidirectional communication is required
- **Design for graceful degradation** when streaming is unavailable
- **Maintain backward compatibility** with non-streaming endpoints

### **Message Format Standards**
```python
# ✅ DO: Consistent streaming message format
{
    "type": "progress_update",
    "timestamp": "2024-01-01T12:00:00Z",
    "data": {
        "stage": "research_competitor",
        "competitor": "Stryker Spine",
        "progress": 0.3,
        "message": "Analyzing competitor product portfolio..."
    },
    "metadata": {
        "session_id": "uuid",
        "request_id": "uuid"
    }
}
```

## **Backend Streaming Implementation**

### **LangGraph Streaming Nodes**
```python
# ✅ DO: Implement streaming-aware nodes
async def streaming_research_competitor(state: GraphState) -> Command:
    """Research competitor with streaming updates"""
    
    # Emit start event
    await emit_stream_event({
        "type": "stage_started",
        "data": {"stage": "research_competitor", "competitor": state["current_competitor"]}
    })
    
    try:
        # Perform research with progress updates
        for i, query in enumerate(search_queries):
            await emit_stream_event({
                "type": "search_started",
                "data": {"query": query, "progress": i / len(search_queries)}
            })
            
            results = await tavily_tool.ainvoke({"query": query})
            
            await emit_stream_event({
                "type": "sources_found",
                "data": {"count": len(results), "sources": results[:3]}  # Preview
            })
        
        return Command(update={"research_results": results}, goto="next_node")
        
    except Exception as e:
        await emit_stream_event({
            "type": "error",
            "data": {"error": str(e), "stage": "research_competitor"}
        })
        raise
```

### **FastAPI Streaming Endpoints**
```python
# ✅ DO: Proper streaming endpoint structure
@app.get("/api/analysis/stream")
async def stream_analysis(
    competitors: List[str] = Query(...),
    focus_area: str = Query(...),
    request: Request = None
):
    async def generate_stream():
        try:
            session_id = str(uuid.uuid4())
            
            # Initialize streaming context
            streaming_context = StreamingContext(session_id, request)
            
            # Run analysis with streaming
            async for event in opportunity_graph.astream_analysis(
                competitors, focus_area, streaming_context
            ):
                # Format and yield event
                yield f"data: {json.dumps(event)}\n\n"
                
                # Check for client disconnect
                if await request.is_disconnected():
                    break
                    
        except Exception as e:
            error_event = {
                "type": "error",
                "data": {"error": str(e)},
                "timestamp": datetime.utcnow().isoformat()
            }
            yield f"data: {json.dumps(error_event)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )
```

## **Frontend Streaming Implementation**

### **Streamlit Streaming Components**
```python
# ✅ DO: Streamlit streaming with session state
def create_streaming_analysis_view():
    """Create streaming analysis interface"""
    
    # Initialize session state
    if "streaming_active" not in st.session_state:
        st.session_state.streaming_active = False
        st.session_state.stream_events = []
        st.session_state.current_stage = None
    
    # Streaming container
    stream_container = st.container()
    
    if st.session_state.streaming_active:
        with stream_container:
            display_streaming_progress()
            display_live_sources()
            display_key_insights()
    
    # Start streaming button
    if st.button("🚀 Start Analysis", disabled=st.session_state.streaming_active):
        start_streaming_analysis()

def start_streaming_analysis():
    """Initialize streaming analysis"""
    st.session_state.streaming_active = True
    
    # Create placeholder for updates
    progress_placeholder = st.empty()
    sources_placeholder = st.empty()
    insights_placeholder = st.empty()
    
    # Start streaming in background
    stream_url = f"{API_BASE_URL}/api/analysis/stream"
    
    # Use threading for non-blocking streaming
    import threading
    thread = threading.Thread(
        target=handle_stream_events,
        args=(stream_url, progress_placeholder, sources_placeholder, insights_placeholder)
    )
    thread.start()
```

### **Event Handling Patterns**
```python
# ✅ DO: Robust event handling
def handle_stream_events(stream_url, *placeholders):
    """Handle incoming stream events"""
    
    try:
        with requests.get(stream_url, stream=True) as response:
            for line in response.iter_lines():
                if line:
                    try:
                        # Parse SSE format
                        if line.startswith(b'data: '):
                            event_data = json.loads(line[6:])
                            process_stream_event(event_data, placeholders)
                            
                    except json.JSONDecodeError:
                        continue
                        
    except requests.exceptions.RequestException as e:
        handle_streaming_error(e)
    finally:
        st.session_state.streaming_active = False
        st.rerun()

def process_stream_event(event, placeholders):
    """Process individual stream events"""
    event_type = event.get("type")
    
    if event_type == "stage_started":
        update_progress_display(event["data"], placeholders[0])
    elif event_type == "sources_found":
        update_sources_display(event["data"], placeholders[1])
    elif event_type == "insight_generated":
        update_insights_display(event["data"], placeholders[2])
    elif event_type == "error":
        handle_streaming_error(event["data"])
    
    # Trigger Streamlit rerun
    st.rerun()
```

## **Error Handling and Recovery**

### **Connection Management**
```python
# ✅ DO: Robust connection handling
class StreamingContext:
    def __init__(self, session_id: str, request: Request):
        self.session_id = session_id
        self.request = request
        self.start_time = datetime.utcnow()
        self.last_heartbeat = datetime.utcnow()
        self.is_active = True
    
    async def check_connection(self):
        """Check if client is still connected"""
        if self.request and await self.request.is_disconnected():
            self.is_active = False
            return False
        
        # Check for timeout
        if (datetime.utcnow() - self.last_heartbeat).seconds > 30:
            self.is_active = False
            return False
            
        return True
    
    async def emit_heartbeat(self):
        """Send heartbeat to maintain connection"""
        self.last_heartbeat = datetime.utcnow()
        return {
            "type": "heartbeat",
            "timestamp": self.last_heartbeat.isoformat()
        }
```

### **Graceful Degradation**
```python
# ✅ DO: Fallback to non-streaming
async def run_analysis_with_fallback(competitors, focus_area):
    """Run analysis with streaming fallback"""
    
    try:
        # Attempt streaming analysis
        if streaming_available():
            return await stream_analysis(competitors, focus_area)
    except StreamingException as e:
        logger.warning(f"Streaming failed: {e}, falling back to batch mode")
    
    # Fallback to traditional analysis
    return await batch_analysis(competitors, focus_area)
```

## **Performance and Security**

### **Rate Limiting**
```python
# ✅ DO: Implement streaming rate limits
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/analysis/stream")
@limiter.limit("5/minute")  # Limit streaming requests
async def stream_analysis(request: Request, ...):
    # Implementation
```

### **Resource Management**
```python
# ✅ DO: Monitor streaming resources
class StreamingMonitor:
    def __init__(self):
        self.active_streams = {}
        self.max_concurrent_streams = 10
    
    async def register_stream(self, session_id: str, context: StreamingContext):
        if len(self.active_streams) >= self.max_concurrent_streams:
            raise TooManyStreamsException("Maximum concurrent streams reached")
        
        self.active_streams[session_id] = context
    
    async def cleanup_inactive_streams(self):
        """Remove inactive or timed-out streams"""
        inactive = [
            sid for sid, ctx in self.active_streams.items()
            if not ctx.is_active or (datetime.utcnow() - ctx.start_time).seconds > 300
        ]
        
        for sid in inactive:
            del self.active_streams[sid]
```

## **Testing Streaming Features**

### **Unit Tests**
```python
# ✅ DO: Test streaming components
@pytest.mark.asyncio
async def test_streaming_node():
    """Test streaming LangGraph node"""
    
    events = []
    
    async def mock_emit(event):
        events.append(event)
    
    # Mock streaming context
    context = MockStreamingContext(emit_func=mock_emit)
    
    # Run streaming node
    result = await streaming_research_competitor(test_state, context)
    
    # Verify events were emitted
    assert len(events) > 0
    assert events[0]["type"] == "stage_started"
    assert result.goto == "next_node"
```

### **Integration Tests**
```python
# ✅ DO: Test end-to-end streaming
def test_streaming_endpoint():
    """Test streaming API endpoint"""
    
    with TestClient(app) as client:
        with client.stream("GET", "/api/analysis/stream?competitors=Test") as response:
            events = []
            
            for line in response.iter_lines():
                if line.startswith("data: "):
                    event = json.loads(line[6:])
                    events.append(event)
            
            # Verify streaming behavior
            assert len(events) > 0
            assert any(e["type"] == "stage_started" for e in events)
            assert any(e["type"] == "sources_found" for e in events)
```

## **Common Anti-Patterns**

### **❌ DON'T: Block the Event Loop**
```python
# ❌ DON'T: Synchronous operations in streaming
def streaming_node(state):
    time.sleep(5)  # Blocks entire event loop
    return result

# ✅ DO: Use async operations
async def streaming_node(state):
    await asyncio.sleep(5)  # Non-blocking
    return result
```

### **❌ DON'T: Ignore Connection State**
```python
# ❌ DON'T: Continue streaming to disconnected clients
async def generate_stream():
    for i in range(1000):
        yield f"data: {i}\n\n"  # No disconnect check

# ✅ DO: Check connection state
async def generate_stream():
    for i in range(1000):
        if await request.is_disconnected():
            break
        yield f"data: {i}\n\n"
```

## **Monitoring and Observability**

### **Metrics Collection**
- **Track active stream count** and duration
- **Monitor event emission rates** and types
- **Measure client disconnect rates** and reasons
- **Log streaming errors** and recovery attempts

### **Health Checks**
- **Verify streaming endpoint availability**
- **Test WebSocket connection establishment**
- **Monitor backend processing latency**
- **Check frontend event handling performance**
