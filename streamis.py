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
    redis = None

    async def redis_connect():
        global redis
        if redis is None:
            redis = await aioredis.create_connection(
                (config['redis']['host'], config['redis']['port']))
        return redis

    # see https://gist.github.com/gdamjan/3ed70de225c05d267511
    async def sse_handler(request):
        """EventSource handler."""
        if request.headers.get('accept') != 'text/event-stream':
            return web.Response(status=406)
        stream = web.StreamResponse()
        stream.headers['Content-Type'] = 'text/event-stream'
        stream.headers['Cache-Control'] = 'no-cache'
        stream.header['Connection'] = 'keep-alive'
        stream.enable_chunked_encoding()
        await stream.prepare(request)

        # get messages from redis here

        await stream.write_eof()
        return stream

    app = web.Application()
    app.router.add_route('GET', '/{channel}', sse_handler)

    return app
