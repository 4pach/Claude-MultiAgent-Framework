#!/usr/bin/env python3
"""
FastAPI Web Service example using Claude MultiAgent Framework
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from claude_framework import Framework, track_mcp_call
import uvicorn

# Initialize framework
framework = Framework()
app = FastAPI(
    title="Claude MultiAgent API",
    description="AI-powered API with automatic monitoring",
    version="1.0.0"
)

class ProcessRequest(BaseModel):
    text: str
    options: dict = {}

class ProcessResponse(BaseModel):
    result: str
    processing_time: float
    agent_used: str

@app.on_event("startup")
async def startup_event():
    """Initialize framework on startup"""
    await framework.start()
    print("🚀 Claude MultiAgent Framework API started")

@app.on_event("shutdown") 
async def shutdown_event():
    """Cleanup on shutdown"""
    await framework.stop()

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Claude MultiAgent Framework API",
        "version": "1.0.0",
        "endpoints": ["/process", "/health", "/metrics"]
    }

@app.post("/process", response_model=ProcessResponse)
@track_mcp_call("web_api", "process_data")
async def process_data(request: ProcessRequest):
    """Process data using framework agents"""
    
    try:
        # Use architect agent for processing
        architect = framework.get_agent('architect')
        if not architect:
            raise HTTPException(status_code=503, detail="Architect agent not available")
        
        task = {
            'type': 'data_processing',
            'text': request.text,
            'options': request.options
        }
        
        import time
        start_time = time.time()
        
        result = await architect.process(task)
        
        processing_time = time.time() - start_time
        
        return ProcessResponse(
            result=result.get('processed_text', 'Data processed successfully'),
            processing_time=processing_time,
            agent_used='architect'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "framework_running": framework.is_running,
        "agents": list(framework.agents.keys())
    }

@app.get("/metrics")
@track_mcp_call("web_api", "get_metrics")
async def get_metrics():
    """Get monitoring metrics"""
    
    if framework.monitoring:
        stats = framework.monitoring.get_stats()
        return {
            "mcp_calls": stats,
            "framework_status": "running" if framework.is_running else "stopped"
        }
    
    return {"message": "Monitoring not available"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
