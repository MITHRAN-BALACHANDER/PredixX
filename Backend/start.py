"""
Simple startup script for DPE Backend (No Docker Required)
Run with: python start.py
"""
import os
import sys
import uvicorn

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting Dynamic Pricing Engine Backend")
    print("=" * 60)
    print("\n📍 API will be available at: http://localhost:8000")
    print("📖 API Docs at: http://localhost:8000/docs")
    print("\n✓ Using SQLite database (no Docker needed)")
    print("✓ Background tasks enabled (no Redis/Celery needed)")
    print("\nPress CTRL+C to stop the server\n")
    print("=" * 60)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
