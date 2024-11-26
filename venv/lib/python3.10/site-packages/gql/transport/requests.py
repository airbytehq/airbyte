import io
import json
import logging
from typing import Any, Collection, Dict, List, Optional, Tuple, Type, Union

import requests
from graphql import DocumentNode, ExecutionResult, print_ast
from requests.adapters import HTTPAdapter, Retry
from requests.auth import AuthBase
from requests.cookies import RequestsCookieJar
from requests_toolbelt.multipart.encoder import MultipartEncoder

from gql.transport import Transport

from ..graphql_request import GraphQLRequest
from ..utils import extract_files
from .exceptions import (
    TransportAlreadyConnected,
    TransportClosed,
    TransportProtocolError,
    TransportServerError,
)

log = logging.getLogger(__name__)


class RequestsHTTPTransport(Transport):
    """:ref:`Sync Transport <sync_transports>` used to execute GraphQL queries
    on remote servers.

    The transport uses the requests library to send HTTP POST requests.
    """

    file_classes: Tuple[Type[Any], ...] = (io.IOBase,)
    _default_retry_codes = (429, 500, 502, 503, 504)

    def __init__(
        self,
        url: str,
        headers: Optional[Dict[str, Any]] = None,
        cookies: Optional[Union[Dict[str, Any], RequestsCookieJar]] = None,
        auth: Optional[AuthBase] = None,
        use_json: bool = True,
        timeout: Optional[int] = None,
        verify: Union[bool, str] = True,
        retries: int = 0,
        method: str = "POST",
        retry_backoff_factor: float = 0.1,
        retry_status_forcelist: Collection[int] = _default_retry_codes,
        **kwargs: Any,
    ):
        """Initialize the transport with the given request parameters.

        :param url: The GraphQL server URL.
        :param headers: Dictionary of HTTP Headers to send with the :class:`Request`
            (Default: None).
        :param cookies: Dict or CookieJar object to send with the :class:`Request`
            (Default: None).
        :param auth: Auth tuple or callable to enable Basic/Digest/Custom HTTP Auth
            (Default: None).
        :param use_json: Send request body as JSON instead of form-urlencoded
            (Default: True).
        :param timeout: Specifies a default timeout for requests (Default: None).
        :param verify: Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. (Default: True).
        :param retries: Pre-setup of the requests' Session for performing retries
        :param method: HTTP method used for requests. (Default: POST).
        :param retry_backoff_factor: A backoff factor to apply between attempts after
            the second try. urllib3 will sleep for:
            {backoff factor} * (2 ** ({number of previous retries}))
        :param retry_status_forcelist: A set of integer HTTP status codes that we
            should force a retry on. A retry is initiated if the request method is
            in allowed_methods and the response status code is in status_forcelist.
            (Default: [429, 500, 502, 503, 504])
        :param kwargs: Optional arguments that ``request`` takes.
            These can be seen at the `requests`_ source code or the official `docs`_

        .. _requests: https://github.com/psf/requests/blob/master/requests/api.py
        .. _docs: https://requests.readthedocs.io/en/master/
        """
        self.url = url
        self.headers = headers
        self.cookies = cookies
        self.auth = auth
        self.use_json = use_json
        self.default_timeout = timeout
        self.verify = verify
        self.retries = retries
        self.method = method
        self.retry_backoff_factor = retry_backoff_factor
        self.retry_status_forcelist = retry_status_forcelist
        self.kwargs = kwargs

        self.session = None

        self.response_headers = None

    def connect(self):
        if self.session is None:
            # Creating a session that can later be re-use to configure custom mechanisms
            self.session = requests.Session()

            # If we specified some retries, we provide a predefined retry-logic
            if self.retries > 0:
                adapter = HTTPAdapter(
                    max_retries=Retry(
                        total=self.retries,
                        backoff_factor=self.retry_backoff_factor,
                        status_forcelist=self.retry_status_forcelist,
                        allowed_methods=None,
                    )
                )
                for prefix in "http://", "https://":
                    self.session.mount(prefix, adapter)
        else:
            raise TransportAlreadyConnected("Transport is already connected")

    def execute(  # type: ignore
        self,
        document: DocumentNode,
        variable_values: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        timeout: Optional[int] = None,
        extra_args: Optional[Dict[str, Any]] = None,
        upload_files: bool = False,
    ) -> ExecutionResult:
        """Execute GraphQL query.

        Execute the provided document AST against the configured remote server. This
        uses the requests library to perform a HTTP POST request to the remote server.

        :param document: GraphQL query as AST Node object.
        :param variable_values: Dictionary of input parameters (Default: None).
        :param operation_name: Name of the operation that shall be executed.
            Only required in multi-operation documents (Default: None).
        :param timeout: Specifies a default timeout for requests (Default: None).
        :param extra_args: additional arguments to send to the requests post method
        :param upload_files: Set to True if you want to put files in the variable values
        :return: The result of execution.
            `data` is the result of executing the query, `errors` is null
            if no errors occurred, and is a non-empty array if an error occurred.
        """

        if not self.session:
            raise TransportClosed("Transport is not connected")

        query_str = print_ast(document)
        payload: Dict[str, Any] = {"query": query_str}

        if operation_name:
            payload["operationName"] = operation_name

        post_args = {
            "headers": self.headers,
            "auth": self.auth,
            "cookies": self.cookies,
            "timeout": timeout or self.default_timeout,
            "verify": self.verify,
        }

        if upload_files:
            # If the upload_files flag is set, then we need variable_values
            assert variable_values is not None

            # If we upload files, we will extract the files present in the
            # variable_values dict and replace them by null values
            nulled_variable_values, files = extract_files(
                variables=variable_values,
                file_classes=self.file_classes,
            )

            # Save the nulled variable values in the payload
            payload["variables"] = nulled_variable_values

            # Add the payload to the operations field
            operations_str = json.dumps(payload)
            log.debug("operations %s", operations_str)

            # Generate the file map
            # path is nested in a list because the spec allows multiple pointers
            # to the same file. But we don't support that.
            # Will generate something like {"0": ["variables.file"]}
            file_map = {str(i): [path] for i, path in enumerate(files)}

            # Enumerate the file streams
            # Will generate something like {'0': <_io.BufferedReader ...>}
            file_streams = {str(i): files[path] for i, path in enumerate(files)}

            # Add the file map field
            file_map_str = json.dumps(file_map)
            log.debug("file_map %s", file_map_str)

            fields = {"operations": operations_str, "map": file_map_str}

            # Add the extracted files as remaining fields
            for k, f in file_streams.items():
                name = getattr(f, "name", k)
                content_type = getattr(f, "content_type", None)

                if content_type is None:
                    fields[k] = (name, f)
                else:
                    fields[k] = (name, f, content_type)

            # Prepare requests http to send multipart-encoded data
            data = MultipartEncoder(fields=fields)

            post_args["data"] = data

            if post_args["headers"] is None:
                post_args["headers"] = {}
            else:
                post_args["headers"] = {**post_args["headers"]}

            post_args["headers"]["Content-Type"] = data.content_type

        else:
            if variable_values:
                payload["variables"] = variable_values

            data_key = "json" if self.use_json else "data"
            post_args[data_key] = payload

        # Log the payload
        if log.isEnabledFor(logging.INFO):
            log.info(">>> %s", json.dumps(payload))

        # Pass kwargs to requests post method
        post_args.update(self.kwargs)

        # Pass post_args to requests post method
        if extra_args:
            post_args.update(extra_args)

        # Using the created session to perform requests
        response = self.session.request(
            self.method, self.url, **post_args  # type: ignore
        )
        self.response_headers = response.headers

        def raise_response_error(resp: requests.Response, reason: str):
            # We raise a TransportServerError if the status code is 400 or higher
            # We raise a TransportProtocolError in the other cases

            try:
                # Raise a HTTPError if response status is 400 or higher
                resp.raise_for_status()
            except requests.HTTPError as e:
                raise TransportServerError(str(e), e.response.status_code) from e

            result_text = resp.text
            raise TransportProtocolError(
                f"Server did not return a GraphQL result: "
                f"{reason}: "
                f"{result_text}"
            )

        try:
            result = response.json()

            if log.isEnabledFor(logging.INFO):
                log.info("<<< %s", response.text)

        except Exception:
            raise_response_error(response, "Not a JSON answer")

        if "errors" not in result and "data" not in result:
            raise_response_error(response, 'No "data" or "errors" keys in answer')

        return ExecutionResult(
            errors=result.get("errors"),
            data=result.get("data"),
            extensions=result.get("extensions"),
        )

    def execute_batch(  # type: ignore
        self,
        reqs: List[GraphQLRequest],
        timeout: Optional[int] = None,
        extra_args: Optional[Dict[str, Any]] = None,
    ) -> List[ExecutionResult]:
        """Execute multiple GraphQL requests in a batch.

        Execute the provided requests against the configured remote server. This
        uses the requests library to perform a HTTP POST request to the remote server.

        :param reqs: GraphQL requests as a list of GraphQLRequest objects.
        :param timeout: Specifies a default timeout for requests (Default: None).
        :param extra_args: additional arguments to send to the requests post method
        :return: A list of results of execution.
            For every result `data` is the result of executing the query,
            `errors` is null if no errors occurred, and is a non-empty array
            if an error occurred.
        """

        if not self.session:
            raise TransportClosed("Transport is not connected")

        # Using the created session to perform requests
        response = self.session.request(
            self.method,
            self.url,
            **self._build_batch_post_args(reqs, timeout, extra_args),
        )
        self.response_headers = response.headers

        answers = self._extract_response(response)

        self._validate_answer_is_a_list(answers)
        self._validate_num_of_answers_same_as_requests(reqs, answers)
        self._validate_every_answer_is_a_dict(answers)
        self._validate_data_and_errors_keys_in_answers(answers)

        return [self._answer_to_execution_result(answer) for answer in answers]

    def _answer_to_execution_result(self, result: Dict[str, Any]) -> ExecutionResult:
        return ExecutionResult(
            errors=result.get("errors"),
            data=result.get("data"),
            extensions=result.get("extensions"),
        )

    def _validate_answer_is_a_list(self, results: Any) -> None:
        if not isinstance(results, list):
            self._raise_invalid_result(
                str(results),
                "Answer is not a list",
            )

    def _validate_data_and_errors_keys_in_answers(
        self, results: List[Dict[str, Any]]
    ) -> None:
        for result in results:
            if "errors" not in result and "data" not in result:
                self._raise_invalid_result(
                    str(results),
                    'No "data" or "errors" keys in answer',
                )

    def _validate_every_answer_is_a_dict(self, results: List[Dict[str, Any]]) -> None:
        for result in results:
            if not isinstance(result, dict):
                self._raise_invalid_result(str(results), "Not every answer is dict")

    def _validate_num_of_answers_same_as_requests(
        self,
        reqs: List[GraphQLRequest],
        results: List[Dict[str, Any]],
    ) -> None:
        if len(reqs) != len(results):
            self._raise_invalid_result(
                str(results),
                "Invalid answer length",
            )

    def _raise_invalid_result(self, result_text: str, reason: str) -> None:
        raise TransportProtocolError(
            f"Server did not return a valid GraphQL result: "
            f"{reason}: "
            f"{result_text}"
        )

    def _extract_response(self, response: requests.Response) -> Any:
        try:
            response.raise_for_status()
            result = response.json()

            if log.isEnabledFor(logging.INFO):
                log.info("<<< %s", response.text)

        except requests.HTTPError as e:
            raise TransportServerError(str(e), e.response.status_code) from e

        except Exception:
            self._raise_invalid_result(str(response.text), "Not a JSON answer")

        return result

    def _build_batch_post_args(
        self,
        reqs: List[GraphQLRequest],
        timeout: Optional[int] = None,
        extra_args: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        post_args: Dict[str, Any] = {
            "headers": self.headers,
            "auth": self.auth,
            "cookies": self.cookies,
            "timeout": timeout or self.default_timeout,
            "verify": self.verify,
        }

        data_key = "json" if self.use_json else "data"
        post_args[data_key] = [self._build_data(req) for req in reqs]

        # Log the payload
        if log.isEnabledFor(logging.INFO):
            log.info(">>> %s", json.dumps(post_args[data_key]))

        # Pass kwargs to requests post method
        post_args.update(self.kwargs)

        # Pass post_args to requests post method
        if extra_args:
            post_args.update(extra_args)

        return post_args

    def _build_data(self, req: GraphQLRequest) -> Dict[str, Any]:
        query_str = print_ast(req.document)
        payload: Dict[str, Any] = {"query": query_str}

        if req.operation_name:
            payload["operationName"] = req.operation_name

        if req.variable_values:
            payload["variables"] = req.variable_values

        return payload

    def close(self):
        """Closing the transport by closing the inner session"""
        if self.session:
            self.session.close()
            self.session = None
