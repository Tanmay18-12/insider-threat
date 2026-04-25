import os
import json
import redis
import asyncio
from datetime import datetime

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

class AlertService:
    def __init__(self):
        self.local_queue = asyncio.Queue()
        try:
            self.redis_client = redis.Redis.from_url(REDIS_URL)
            self.redis_client.ping()
        except Exception:
            self.redis_client = None
            print("Warning: Redis not available. Falling back to local asyncio.Queue.")

    async def publish_alert_async(self, alert_data: dict):
        for key, value in alert_data.items():
            if isinstance(value, datetime):
                alert_data[key] = value.isoformat()
            elif hasattr(value, '__str__') and not isinstance(value, (int, float, str, bool, type(None))):
                alert_data[key] = str(value)

        msg = json.dumps(alert_data)
        if self.redis_client:
            try:
                self.redis_client.publish("alerts", msg)
            except Exception as e:
                print(f"Error publishing to Redis: {e}")
        else:
            await self.local_queue.put(msg)
            
    def publish_alert(self, alert_data: dict):
        # Sync wrapper
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.publish_alert_async(alert_data))
        except RuntimeError:
            asyncio.run(self.publish_alert_async(alert_data))

alert_service = AlertService()
