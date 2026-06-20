"""Vercel Serverless Function — FastAPI with database integration."""

import os
import sys

# Add project root and backend to path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, "backend")
if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi import FastAPI

app = FastAPI()

@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}
