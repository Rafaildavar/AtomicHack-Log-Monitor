import sys
import os
from pathlib import Path

# Add parent directory to path so we can import api module
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from api.main import app
except Exception as e:
    print(f"Error importing app: {e}")
    # Fallback: create a simple app
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/health")
    def health():
        return {"status": "error", "message": str(e)}

# Export for Vercel
handler = app
