from app.core.config import settings


class RedisBus:
    def __init__(self):
        self.url = settings.redis_url

    async def publish(self, stream: str, payload: dict) -> None:
        return None


redis_bus = RedisBus()
