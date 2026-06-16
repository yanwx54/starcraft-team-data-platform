"""Vercel Serverless Function 入口 — 将 FastAPI 适配为 Vercel Python Runtime。"""

import sys
from pathlib import Path

# 将项目根目录加入 Python 路径
project_root = Path(__file__).resolve().parent.parent
backend_dir = project_root / "backend"
for path in [str(project_root), str(backend_dir)]:
    if path not in sys.path:
        sys.path.insert(0, path)

from app.main import app  # noqa: E402
