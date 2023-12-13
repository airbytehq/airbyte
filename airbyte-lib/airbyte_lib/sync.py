from .source import Source
from .cache import InMemoryCache

def sync(connector: Source, store: InMemoryCache):
    store.write(connector.read())