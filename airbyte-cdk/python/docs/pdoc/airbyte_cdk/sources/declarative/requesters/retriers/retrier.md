Module airbyte_cdk.sources.declarative.requesters.retriers.retrier
==================================================================

Classes
-------

`Retrier()`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * airbyte_cdk.sources.declarative.requesters.retriers.default_retrier.DefaultRetrier

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