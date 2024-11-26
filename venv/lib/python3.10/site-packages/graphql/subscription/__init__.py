"""GraphQL Subscription

The :mod:`graphql.subscription` package is responsible for subscribing to updates
on specific data.

.. deprecated:: 3.2
   This package has been deprecated with its exported functions integrated into the
   :mod:`graphql.execution` package, to better conform with the terminology of the
   GraphQL specification. For backwards compatibility, the :mod:`graphql.subscription`
   package currently re-exports the moved functions from the :mod:`graphql.execution`
   package. In v3.3, the :mod:`graphql.subscription` package will be dropped entirely.
"""

from ..execution import subscribe, create_source_event_stream, MapAsyncIterator

__all__ = ["subscribe", "create_source_event_stream", "MapAsyncIterator"]
