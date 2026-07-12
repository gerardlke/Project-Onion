import asyncio
import json
from typing import AsyncGenerator


class ProgressTracker:
    def __init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()

    async def update(self, message: str, percent: int = None):
        payload = {"message": message}
        if percent is not None:
            payload["percent"] = percent
        await self._queue.put(payload)

    async def complete(self, message: str = "Upload complete.", metadata: dict = None):
        payload = {"message": message, "percent": 100, "done": True}
        if metadata:
            payload["metadata"] = metadata
        await self._queue.put(payload)

    async def error(self, message: str):
        await self._queue.put({"message": message, "error": True, "done": True})

    async def stream(self) -> AsyncGenerator[str, None]:
        while True:
            payload = await self._queue.get()
            yield f"data: {json.dumps(payload)}\n\n"
            if payload.get("done"):
                break