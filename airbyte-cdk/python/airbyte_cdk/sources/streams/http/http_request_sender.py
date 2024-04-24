

# _create_prepared_request
# _send_request(all parameters)
# request_kwargs
# _send(request)

import logging
import urllib
from typing import Any, Mapping, Optional, Union, Tuple
import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from .exceptions import DefaultBackoffException, RequestBodyException, UserDefinedBackoffException
from .rate_limiting import default_backoff_handler, user_defined_backoff_handler
from .http_error_handler import HttpErrorHandler

BODY_REQUEST_METHODS = ("GET", "POST", "PUT", "PATCH")

class HttpRequestSender():

    error_mapping: Mapping[int, str] = {
        400: FailureType.config_error, # <= straightforward failure for 400s
        401: FailureType.config_error,
        403: FailureType.config_error,
        404: FailureType.system_error,
        429: FailureType.transient_error, # <= should retry before failing, therefore indicates need for addtl interface
        500: FailureType.transient_error,
        502: FailureType.transient_error,
        503: FailureType.transient_error,
    }

    def __init__(
            self,
            session: requests.Session,
            logger: logging.Logger,
            http_response_handler: HttpErrorHandler = HttpErrorHandler()
        ):
        self._session = session
        self._logger = logger
        self._http_response_handler = http_response_handler

    def _dedupe_query_params(self, url: str, params: Mapping[str, str]) -> Mapping[str, str]:
        """
        Remove query parameters from params mapping if they are already encoded in the URL.
        :param url: URL with
        :param params:
        :return:
        """
        if params is None:
            params = {}
        query_string = urllib.parse.urlparse(url).query
        query_dict = {k: v[0] for k, v in urllib.parse.parse_qs(query_string).items()}

        duplicate_keys_with_same_value = {k for k in query_dict.keys() if str(params.get(k)) == str(query_dict[k])}
        return {k: v for k, v in params.items() if k not in duplicate_keys_with_same_value}

    def _create_prepared_request(
            self,
            http_method: str,
            url: str,
            dedupe_query_params: bool,
            headers: Optional[Mapping[str, str]] = None,
            params: Optional[Mapping[str, str]] = None,
            json: Optional[Mapping[str, Any]] = None,
            data: Optional[Union[str, Mapping[str, Any]]] = None,
        ):
        # creates and returns a prepared request

        # Public method from HttpStream --> should it be re-implemented here? No guarantee that it's not overridden in existing connectors
        if dedupe_query_params:
            query_params = self._dedupe_query_params(url, params)
        else:
            query_params = params or {}
        args = {"method": http_method, "url": url, "headers": headers, "params": query_params}
        if http_method.upper() in BODY_REQUEST_METHODS:
            if json and data:
                raise RequestBodyException(
                    "At the same time only one of the 'request_body_data' and 'request_body_json' functions can return data"
                )
            elif json:
                args["json"] = json
            elif data:
                args["data"] = data
        prepared_request: requests.PreparedRequest = self._session.prepare_request(requests.Request(**args))

        return prepared_request

    def _send_with_retry(
            self,
            retry_factor: float,
            max_tries: Optional[int],
            max_time: Optional[int],
            request: requests.PreparedRequest,
            request_kwargs: Optional[Mapping[str, Any]] = None
    ) -> requests.Response:
        """
        Backoff package has max_tries parameter that means total number of
        tries before giving up, so if this number is 0 no calls expected to be done.
        But for this class we call it max_REtries assuming there would be at
        least one attempt and some retry attempts, to comply this logic we add
        1 to expected retries attempts.
        """
        if max_tries is not None:
            max_tries = max(0, max_tries) + 1

        user_backoff_handler = user_defined_backoff_handler(max_tries=max_tries, max_time=max_time)(self._send)
        backoff_handler = default_backoff_handler(max_tries=max_tries, max_time=max_time, factor=retry_factor)
        # backoff handlers wrap _send, so it will always return a response
        response = backoff_handler(user_backoff_handler)(request, request_kwargs)

        return response


    def _send(
            self,
            request: requests.PreparedRequest,
            request_kwargs: Optional[Mapping[str, Any]] = None
        ) -> requests.Response:
        # sends prepared request, returns response, invokes error handling on response

        self._logger.debug(
            "Making outbound API request",
            extra={"headers": request.headers, "url": request.url, "request_body": request.body}
        )

        response: requests.Response = self._session.send(request, **request_kwargs)

        # Evaluation of response.text can be heavy, for example, if streaming a large response
        # Do it only in debug mode
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(
                "Receiving response", extra={"headers": response.headers, "status": response.status_code, "body": response.text}
            )


        response = self._http_response_handler.validate_response(response)



        # !!! need to maintain backwards compatiblity with existing connectors, specifically  HttpStream public methods: should_retry, backoff_time, error_message, raise_on_http_errors


        # if self.should_retry(response):
        #     custom_backoff_time = self.backoff_time(response)
        #     error_message = self.error_message(response)
        #     if custom_backoff_time:
        #         raise UserDefinedBackoffException(
        #             backoff=custom_backoff_time, request=request, response=response, error_message=error_message
        #         )
        #     else:
        #         raise DefaultBackoffException(request=request, response=response, error_message=error_message)
        # elif self.raise_on_http_errors:
        #     # Raise any HTTP exceptions that happened in case there were unexpected ones
        #     try:
        #         response.raise_for_status()
        #     except requests.HTTPError as exc:
        #         self._logger.error(response.text)
        #         raise exc

        return response

    def send_request(
            self,
            http_method: str,
            url: str,
            retry_factor: float,
            headers: Optional[Mapping[str, str]] = None,
            params: Optional[Mapping[str, str]] = None,
            json: Optional[Mapping[str, Any]] = None,
            data: Optional[Union[str, Mapping[str, Any]]] = None,
            max_tries: Optional[int] = None,
            max_time: Optional[int] = None,
            dedupe_query_params: bool = False,
            request_kwargs: Optional[Mapping[str, Any]] = None,
        ) -> Tuple[requests.PreparedRequest, requests.Response]:
        """
        Public method that should be called from within HttpStream's feth_next_page method.
        Should prepare request, send it and return request and response objects.
        """

        request: requests.PreparedRequest = self._create_prepared_request(
            http_method=http_method,
            url=url,
            dedupe_query_params=dedupe_query_params,
            headers=headers,
            params=params,
            json=json,
            data=data
        )

        response: requests.Response = self._send_with_retry(
            retry_factor=retry_factor,
            max_tries=max_tries,
            max_time=max_time,
            request=request,
            request_kwargs=request_kwargs
        )

        return request, response
