from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
import uvicorn
from app import app
from graph import parse_graph_data
import json
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import asyncio
import threading
import traceback
import logging
import os

api = FastAPI(title="Graph Execution API")


class GraphData(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    route_edges: List[Dict[str, Any]]


@api.post("/api/execute-graph")
async def execute_graph(graph_data: GraphData):
    try:
        graph = parse_graph_data(json.dumps(graph_data.model_dump()))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    app.execute_graph(graph)
    return {"status": "success"}


@api.post("/api/execute-graph-with-progress")
async def execute_graph_with_progress(graph_data: GraphData):
    try:
        graph = parse_graph_data(json.dumps(graph_data.model_dump()))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    async def event_generator():
        # 创建一个队列用于存储进度消息
        queue = asyncio.Queue()

        def progress_callback(progress_data):
            # 将进度数据放入队列
            queue.put_nowait(progress_data)

        def execute():
            try:
                app.execute_graph(graph, progress_callback)
            except Exception as e:
                queue.put_nowait(e)
            finally:
                queue.put_nowait(None)

        # 在后台线程中执行图
        thread = threading.Thread(target=execute)
        thread.start()

        try:
            while True:
                data = await queue.get()
                if data is None:
                    break
                if isinstance(data, Exception):
                    raise data
                if isinstance(data, dict):
                    data = json.dumps(data)
                    yield f"data: {data}\n\n"
        except Exception as e:
            logging.error(
                "Execute graph with progress exception:\n%s", traceback.format_exc()
            )
            yield f"data: {json.dumps({'error': repr(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@api.get("/api/node-metas")
async def get_node_metas():
    """获取所有可用节点的元数据"""
    node_metas = {}
    for node_type, (_, node_meta) in app.node_defs.items():
        node_metas[node_type] = node_meta
    return {"status": "success", "data": node_metas}


STATIC_DIR = "static"
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

api.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name=STATIC_DIR)


def start_api_service(dev_mode=False):
    # 如果是开发环境，启用CORS
    if dev_mode:
        # 添加CORS中间件
        api.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # 允许所有来源
            allow_credentials=True,
            allow_methods=["*"],  # 允许所有方法
            allow_headers=["*"],  # 允许所有头
        )
        logging.info("Development mode enabled, CORS configured to allow all origins")

    uvicorn.run("api_service:api", host="0.0.0.0", port=8000)
