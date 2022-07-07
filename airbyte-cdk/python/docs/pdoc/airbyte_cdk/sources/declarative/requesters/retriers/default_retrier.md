Module airbyte_cdk.sources.declarative.requesters.retriers.default_retrier
==========================================================================

Classes
-------

`DefaultRetrier(max_retries: Optional[int] = 5, retry_factor: float = 5)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.declarative.requesters.retriers.retrier.Retrier
    * abc.ABC

    ### Instance variables

    `max_retries: Optional[int]`
    :

    `retry_factor: float`
    :

    ### Methods

    `backoff_time(self, response: requests.models.Response) ‑> Optional[float]`
    :

    `should_retry(self, response: requests.models.Response) ‑> bool`
    :