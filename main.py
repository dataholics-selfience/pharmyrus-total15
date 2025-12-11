"""Main entry point for Pharmyrus v4.0"""
import uvicorn
import os

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "src.api_service:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
