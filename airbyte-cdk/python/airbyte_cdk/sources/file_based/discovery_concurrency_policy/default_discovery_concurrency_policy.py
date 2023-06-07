from airbyte_cdk.sources.file_based.discovery_concurrency_policy.abstract_discovery_concurrency_policy import AbstractDiscoveryConcurrencyPolicy


class DefaultDiscoveryConcurrencyPolicy(AbstractDiscoveryConcurrencyPolicy):
    """
    Default number of concurrent requests to send to the source.
    """
    n_concurrent_requests = 10
