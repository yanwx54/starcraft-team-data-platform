"""Vercel Serverless Function 入口 — 将 FastAPI 适配为 Vercel Python Runtime。"""

import sys
from pathlib import Path

# 将 backend 目录加入 Python 路径
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app  # noqa: E402

# Vercel Python Runtime 使用 ASGI 接口
# 框架会自动检测名为 `app` 的 ASGI 实例
