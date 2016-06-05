import logging
import asyncio
from tornado.platform.asyncio import AsyncIOMainLoop
from tornado import web, log
import aioredis

AsyncIOMainLoop().install()

log.enable_pretty_logging()
logger = logging.getLogger('streamis')

DEFAULT_CONFIG = {
    'redis': {
        'host': 'localhost',
        'port': 6379,
        'db': 0
    }
}


class Connection:
    _redis = None

    @classmethod
    async def redis(cls, config: dict, force_reconnect=False):
        if cls._redis is None or force_reconnect:
            cls._redis = await aioredis.create_redis(
                (config['redis']['host'], config['redis']['port']))
        return cls._redis


class Subscription:
    """Handles subscriptions to Redis PUB/SUB channels."""
    def __init__(self, redis, channel: str):
        self._redis = redis
        self.name = channel

    async def subscribe(self):
        self.channel, = await self._redis.subscribe(self.name)

    def __str__(self):
        return self.name

    async def get(self):
        """Return the next message as it comes in."""
        msg = await self.channel.get(encoding='utf-8')
        return msg


class SubscriptionManager:
    """Manages all subscriptions."""
    def __init__(self, redis_config=DEFAULT_CONFIG):
        self.redis = None
        self.redis_config = redis_config
        self.subscriptions = dict()

    async def connect(self):
        self.redis = await Connection.redis(self.redis_config)

    async def subscribe(self, channel: str):
        """Subscribe to a new channel."""
        if channel in self.subscriptions:
            return self.subscriptions[channel]
        subscription = Subscription(self.redis, channel)
        await subscription.subscribe()
        self.subscriptions[channel] = subscription
        return subscription

    def unsubscribe(self, channel: str):
        """Unsubscribe from a channel."""
        if channel not in self.subscriptions:
            logger.warning("Not subscribed to channel '%s'" % channel)
            return
        sub = self.subscriptions.pop(channel)
        del sub


class SSEHandler(web.RequestHandler):
    def initialize(self, manager: SubscriptionManager):
        self.manager = manager

    async def get(self, channel: str):
        subscription = await self.manager.subscribe(channel)
        message = await subscription.get()
        self.write(message)


if __name__ == "__main__":
    port = 8989
    loop = asyncio.get_event_loop()

    manager = SubscriptionManager()
    loop.run_until_complete(manager.connect())

    app = web.Application(
        [(r'/(.*)', SSEHandler, dict(manager=manager))],
        debug=True
    )
    app.listen(port)
    logger.info('Listening on port %d' % port)
    loop.run_forever()
