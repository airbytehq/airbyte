#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import urllib
from typing import Any, Mapping, Optional, Union, Tuple
import requests
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from .exceptions import DefaultBackoffException, RequestBodyException, UserDefinedBackoffException
from .rate_limiting import default_backoff_handler, user_defined_backoff_handler
from .error_handler.http_status_error_handler import HttpStatusErrorHandler
from .error_handler.error_handler import ErrorHandler
from .error_handler.default_retry_strategy import DefaultRetryStrategy
from .error_handler.retry_strategy import RetryStrategy
from .error_handler.response_action import ResponseAction

BODY_REQUEST_METHODS = ("GET", "POST", "PUT", "PATCH")

class HttpClient:

    def __init__(
            self,
            session: requests.Session,
            logger: logging.Logger = logging.getLogger("airbyte"),
            http_error_handler: Optional[ErrorHandler] = HttpStatusErrorHandler(),
            retry_strategy: Optional[RetryStrategy] = DefaultRetryStrategy()
        ):
        self._session = session
        self._logger = logger
        self._http_error_handler = http_error_handler
        self._retry_strategy = retry_strategy

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
        if self._retry_strategy.max_retries is not None:
            max_tries = max(0, self._retry_strategy.max_retries) + 1

        user_backoff_handler = user_defined_backoff_handler(max_tries=max_tries, max_time=self._retry_strategy.max_time)(self._send)
        backoff_handler = default_backoff_handler(max_tries=max_tries, max_time=self._retry_strategy.max_time, factor=self._retry_strategy.retry_factor)
        # backoff handlers wrap _send, so it will always return a response
        response = backoff_handler(user_backoff_handler)(request, request_kwargs)

        return response


    def _send(
            self,
            request: requests.PreparedRequest,
            request_kwargs: Optional[Mapping[str, Any]] = None
        ) -> requests.Response:


        self._logger.debug(
            "Making outbound API request",
            extra={"headers": request.headers, "url": request.url, "request_body": request.body}
        )

        try:
            response: requests.Response = self._session.send(request, **request_kwargs)
        except requests.RequestException as e:
            self._logger.error(f"Failed to return response: {e}")

        # Evaluation of response.text can be heavy, for example, if streaming a large response
        # Do it only in debug mode
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(
                "Receiving response", extra={"headers": response.headers, "status": response.status_code, "body": response.text}
            )

        response_action, failure_type, error_message = self._http_error_handler.interpret_response(response)

        if response_action:
            if response_action == ResponseAction.FAIL:
                error_message = (
                    error_message or f"Request to {response.request.url} failed with status code {response.status_code} and error message {self.parse_response_error_message(response)}"
                )
                raise AirbyteTracedException(
                    internal_message=error_message,
                    message=error_message,
                    failure_type=failure_type,
                )

            if response_action == ResponseAction.IGNORE:
                self._logger.info(
                    f"Ignoring response with status code {response.status_code} for request to {response.request.url}"
                )

        if self._retry_strategy.should_retry(response, response_action):
            custom_backoff_time = self._retry_strategy.backoff_time(response)
            error_message = self._retry_strategy.error_message(response)
            if custom_backoff_time:
                raise UserDefinedBackoffException(
                    backoff=custom_backoff_time, request=request, response=response, error_message=error_message
                )
            else:
                raise DefaultBackoffException(request=request, response=response, error_message=error_message)
        elif self._retry_strategy.raise_on_http_errors:
            # Raise any HTTP exceptions that happened in case there were unexpected ones
            try:
                response.raise_for_status()
            except requests.HTTPError as exc:
                self._logger.error(response.text)
                raise exc

        return response

    @classmethod
    def parse_response_error_message(cls, response: requests.Response) -> Optional[str]:
        """
        Parses the raw response object from a failed request into a user-friendly error message.
        By default, this method tries to grab the error message from JSON responses by following common API patterns. Override to parse differently.

        :param response:
        :return: A user-friendly message that indicates the cause of the error
        """
        # default logic to grab error from common fields
        def _try_get_error(value: Any) -> Any:
            if isinstance(value, str):
                return value
            elif isinstance(value, list):
                error_list = [_try_get_error(v) for v in value]
                return ", ".join(v for v in error_list if v is not None)
            elif isinstance(value, dict):
                new_value = (
                    value.get("message")
                    or value.get("messages")
                    or value.get("error")
                    or value.get("errors")
                    or value.get("failures")
                    or value.get("failure")
                    or value.get("details")
                    or value.get("detail")
                )
                return _try_get_error(new_value)
            return None

        try:
            body = response.json()
            error = _try_get_error(body)
            return str(error) if error else None
        except requests.exceptions.JSONDecodeError:
            return None

    def send_request(
            self,
            http_method: str,
            url: str,
            headers: Optional[Mapping[str, str]] = None,
            params: Optional[Mapping[str, str]] = None,
            json: Optional[Mapping[str, Any]] = None,
            data: Optional[Union[str, Mapping[str, Any]]] = None,
            dedupe_query_params: bool = False,
            request_kwargs: Optional[Mapping[str, Any]] = None,
        ) -> Tuple[requests.PreparedRequest, requests.Response]:
        """
        Prepares and sends request and return request and response objects.
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
            request=request,
            request_kwargs=request_kwargs
        )

        return request, response
