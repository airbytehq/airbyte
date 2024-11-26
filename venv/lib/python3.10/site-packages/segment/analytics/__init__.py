
from segment.analytics.version import VERSION
from segment.analytics.client import Client

__version__ = VERSION

"""Settings."""
write_key = Client.DefaultConfig.write_key
host = Client.DefaultConfig.host
on_error = Client.DefaultConfig.on_error
debug = Client.DefaultConfig.debug
send = Client.DefaultConfig.send
sync_mode = Client.DefaultConfig.sync_mode
max_queue_size = Client.DefaultConfig.max_queue_size
gzip = Client.DefaultConfig.gzip
timeout = Client.DefaultConfig.timeout
max_retries = Client.DefaultConfig.max_retries

default_client = None


def track(*args, **kwargs):
    """Send a track call."""
    return _proxy('track', *args, **kwargs)


def identify(*args, **kwargs):
    """Send a identify call."""
    return _proxy('identify', *args, **kwargs)


def group(*args, **kwargs):
    """Send a group call."""
    return _proxy('group', *args, **kwargs)


def alias(*args, **kwargs):
    """Send a alias call."""
    return _proxy('alias', *args, **kwargs)


def page(*args, **kwargs):
    """Send a page call."""
    return _proxy('page', *args, **kwargs)


def screen(*args, **kwargs):
    """Send a screen call."""
    return _proxy('screen', *args, **kwargs)


def flush():
    """Tell the client to flush."""
    _proxy('flush')


def join():
    """Block program until the client clears the queue"""
    _proxy('join')


def shutdown():
    """Flush all messages and cleanly shutdown the client"""
    _proxy('flush')
    _proxy('join')


def _proxy(method, *args, **kwargs):
    """Create an analytics client if one doesn't exist and send to it."""
    global default_client
    if not default_client:
        default_client = Client(write_key, host=host, debug=debug,
                                max_queue_size=max_queue_size,
                                send=send, on_error=on_error,
                                gzip=gzip, max_retries=max_retries,
                                sync_mode=sync_mode, timeout=timeout)

    fn = getattr(default_client, method)
    return fn(*args, **kwargs)
