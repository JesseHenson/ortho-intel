#!/usr/bin/env python3
"""
Main entry point for Orthopedic Intelligence API Server
Imports from restructured backend API components
"""

# Import and expose the FastAPI app from the restructured backend
from src.backend.api.fastapi_server import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 