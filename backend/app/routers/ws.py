from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json
from app.services.alert_service import alert_service

router = APIRouter(prefix="/ws", tags=["websocket"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@router.websocket("/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    # Start a background task to listen to redis
    async def listen_redis():
        if not alert_service.redis_client:
            while True:
                msg = await alert_service.local_queue.get()
                await manager.broadcast(msg)
                alert_service.local_queue.task_done()
                
        pubsub = alert_service.redis_client.pubsub()
        pubsub.subscribe("alerts")
        
        while True:
            try:
                message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and message['type'] == 'message':
                    data = message['data'].decode('utf-8')
                    await manager.broadcast(data)
            except Exception as e:
                print(f"Redis listen error: {e}")
                await asyncio.sleep(2)
            await asyncio.sleep(0.1)

    listen_task = asyncio.create_task(listen_redis())

    try:
        while True:
            # Just keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        listen_task.cancel()
