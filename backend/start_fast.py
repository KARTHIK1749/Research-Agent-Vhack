#!/usr/bin/env python3
"""
Fast startup script with performance optimizations.
"""
import os
os.environ["OMP_NUM_THREADS"] = "4"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["PYTHONOPTIMIZE"] = "1"

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting MARIS in FAST MODE...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1,
        log_level="info"
    )
