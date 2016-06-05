# streamis

**Work in progress**

Subscribe to Redis pubsub channels via HTTP and EventSource. Powered by
[asyncio][], [Tornado][], and [aioredis][].

[asyncio]: https://docs.python.org/3/library/asyncio.html
[Tornado]: http://www.tornadoweb.org/en/stable/
[aioredis]: http://aioredis.readthedocs.io/en/latest/

## Why?

Server sent events are useful and the complexity of websockets is often
not necessary. By adding a proxy between Redis and the browser, server
pushes can easily supplement the more traditional request-response
nature of WSGI frameworks such as [Django][] and [Flask][].

[Django]: https://www.djangoproject.com/
[Flask]: http://flask.pocoo.org/

## See also

Related (and almost certainly better) projects:

* [Webdis](http://webd.is/)
* [websocketd](http://websocketd.com/)
