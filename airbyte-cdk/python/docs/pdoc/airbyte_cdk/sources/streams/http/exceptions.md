Module airbyte_cdk.sources.streams.http.exceptions
==================================================

Classes
-------

`BaseBackoffException(request: requests.models.PreparedRequest, response: requests.models.Response)`
:   An HTTP error occurred.
    
    Initialize RequestException with `request` and `response` objects.

    ### Ancestors (in MRO)

    * requests.exceptions.HTTPError
    * requests.exceptions.RequestException
    * builtins.OSError
    * builtins.Exception
    * builtins.BaseException

    ### Descendants

    * airbyte_cdk.sources.streams.http.exceptions.DefaultBackoffException
    * airbyte_cdk.sources.streams.http.exceptions.UserDefinedBackoffException

`DefaultBackoffException(request: requests.models.PreparedRequest, response: requests.models.Response)`
:   An HTTP error occurred.
    
    Initialize RequestException with `request` and `response` objects.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.streams.http.exceptions.BaseBackoffException
    * requests.exceptions.HTTPError
    * requests.exceptions.RequestException
    * builtins.OSError
    * builtins.Exception
    * builtins.BaseException

`RequestBodyException(*args, **kwargs)`
:   Raised when there are issues in configuring a request body

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

`UserDefinedBackoffException(backoff: Union[int, float], request: requests.models.PreparedRequest, response: requests.models.Response)`
:   An exception that exposes how long it attempted to backoff
    
    :param backoff: how long to backoff in seconds
    :param request: the request that triggered this backoff exception
    :param response: the response that triggered the backoff exception

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.streams.http.exceptions.BaseBackoffException
    * requests.exceptions.HTTPError
    * requests.exceptions.RequestException
    * builtins.OSError
    * builtins.Exception
    * builtins.BaseException