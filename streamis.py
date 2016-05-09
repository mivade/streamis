from aiohttp import web
import aioredis

DEFAULT_CONFIG = {
    'redis': {
        'host': 'localhost',
        'port': 6379,
        'db': 0
    }
}


def make_app(config=DEFAULT_CONFIG):
    """Factory function for creating the aiohttp application."""
    # Helper to manage connecting to the database
    class Connection:
        _redis = None

        @classmethod
        async def redis(cls, force_reconnect=False):
            if cls._redis is None or force_reconnect:
                cls._redis = await aioredis.create_redis(
                    (config['redis']['host'], config['redis']['port']))
            return cls._redis

    # see https://gist.github.com/gdamjan/3ed70de225c05d267511
    async def sse_handler(request):
        """EventSource handler."""
        channel = request.match_info['channel']
        # if request.headers.get('accept') != 'text/event-stream':
        #     return web.Response(status=406)
        stream = web.StreamResponse()
        stream.content_type = 'text/event-stream'
        # stream.headers['Cache-Control'] = 'no-cache'
        # stream.header['Connection'] = 'keep-alive'
        await stream.prepare(request)

        redis = await Connection.redis()
        channel, = await redis.subscribe(channel)
        while True:
            msg = await channel.get(encoding='utf-8')
            if msg is None:
                break  # TODO: more graceful
            else:
                stream.write(b'data: %s\r\n\r\n' % msg.encode())

        await stream.write_eof()
        return stream

    app = web.Application()
    app.router.add_route('GET', '/{channel}', sse_handler)

    return app


if __name__ == "__main__":
    app = make_app()
    web.run_app(app)
