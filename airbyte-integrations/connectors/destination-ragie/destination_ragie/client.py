# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import datetime
import json
import logging
import os
import time
import traceback
from typing import Any, Dict, List, Mapping, Optional, Set, Union

import backoff
import requests

from airbyte_cdk.utils.traced_exception import AirbyteTracedException, FailureType

from .config import RagieConfig


logger = logging.getLogger("airbyte.destination_ragie.client")


# --- Error Handling Functions (remain mostly the same) ---
class RagieApiError(Exception):
    """Custom exception for Ragie API errors."""

    pass


def user_error(e: Exception) -> bool:
    """Return True if this exception is likely a user configuration error (4xx)."""
    # Added check for RagieApiError originating from HTTPError
    if isinstance(e, RagieApiError) and isinstance(e.__cause__, requests.exceptions.HTTPError):
        response = e.__cause__.response
    elif isinstance(e, requests.exceptions.RequestException):
        response = e.response
    else:
        return False  # Not an HTTP-related error we can easily classify

    if response is None:
        return False  # Cannot determine status code

    # Exclude 404, 429 from user errors that give up immediately
    return bool(400 <= response.status_code < 500 and response.status_code not in [404, 429])


def transient_error(e: Exception) -> bool:
    """Return True if this exception is likely transient (5xx or rate limit)."""
    # Added check for RagieApiError originating from HTTPError or RequestException
    if isinstance(e, RagieApiError):
        if isinstance(e.__cause__, requests.exceptions.HTTPError):
            response = e.__cause__.response
        elif isinstance(e.__cause__, requests.exceptions.RequestException):
            # Network errors wrapped in RagieApiError are transient
            return True
        else:
            # Other RagieApiErrors (e.g., manual raises) likely not transient
            return False
    elif isinstance(e, requests.exceptions.RequestException):
        # Direct RequestExceptions (like ConnectionError, Timeout) are transient
        # Also check response status code if available
        response = e.response
        if response is None:  # Connection error, Timeout etc.
            return True
    else:
        # Other exception types (e.g., programming errors) are not transient network issues
        return False

    if response is None:
        # Should have been caught above, but for safety: if no response, assume transient network issue
        return True

    # Check for 5xx or 429 status codes
    return bool(response.status_code >= 500 or response.status_code == 429)


# --- End Error Handling ---


class RagieClient:
    # --- Constants ---
    DEFAULT_API_URL = "https://api.ragie.ai"
    # Endpoint for JSON data uploads (assuming this is correct, based on previous impl)
    DOCUMENTS_RAW_ENDPOINT = "/documents/raw"
    # Endpoint for Listing/Deleting/Querying (based on previous impl and connection check)
    DOCUMENTS_GENERAL_ENDPOINT = "/documents"

    METADATA_AIRBYTE_STREAM_FIELD = "airbyte_stream"  # Use this key in RagieWriter as well

    def __init__(self, config: RagieConfig):
        self.config = config
        self.base_url = config.api_url.rstrip("/") if config.api_url else self.DEFAULT_API_URL
        self.api_key = config.api_key
        self.session = self._create_session()
        # Store partition header for reuse on *non-file-upload* requests
        self.partition_header = {"partition": config.partition} if config.partition else {}
        logger.info(f"RagieClient initialized. Base URL: {self.base_url}, Default Partition Scope: {config.partition or 'Account-wide'}")

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update(
            {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json", "X-source": "airbyte-destination-ragie"}
        )
        return session

    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.RequestException, RagieApiError),
        max_tries=5,
        giveup=user_error,
        on_backoff=lambda details: logger.warning(
            f"Transient error detected ({details['exception']}). Retrying in {details['wait']:.1f}s."
        ),
        factor=3,
    )
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,  # For form data
        files: Optional[Dict[str, Any]] = None,  # For file uploads
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """Makes an HTTP request with error handling, retries, and optional extra headers."""
        full_url = f"{self.base_url}{endpoint}"
        # Start with session headers (includes Auth, Accept, X-source)
        request_headers = self.session.headers.copy()

        # Apply specific per-request headers (like partition for non-file requests)
        if extra_headers:
            request_headers.update(extra_headers)

        # Content-Type management:
        # - If 'json_data' is present, set Content-Type to application/json
        # - If 'files' is present, requests handles multipart/form-data Content-Type automatically
        # - If only 'data' is present, requests handles application/x-www-form-urlencoded
        # - Avoid setting Content-Type explicitly if 'files' are involved.
        if json_data is not None and files is None:
            request_headers["Content-Type"] = "application/json"
        elif files is not None:
            # Remove potentially conflicting Content-Type if files are present
            request_headers.pop("Content-Type", None)

        log_json = f" json_data: {json.dumps(json_data)[:200]}..." if json_data else ""
        log_data = f" data_keys: {list(data.keys())}" if data else ""
        log_files = f" files_keys: {list(files.keys())}" if files else ""
        log_params = f" params: {params}" if params else ""
        # Log effective headers *before* the request
        logger.debug(f"Making {method} request to {full_url}{log_params}{log_json}{log_data}{log_files} with headers: {request_headers}")

        try:
            response = self.session.request(
                method=method, url=full_url, params=params, json=json_data, data=data, files=files, headers=request_headers
            )
            logger.debug(f"Response status code: {response.status_code}")
            response.raise_for_status()  # Raises HTTPError for 4xx/5xx
            return response
        except requests.exceptions.HTTPError as e:
            error_message = f"HTTP error {e.response.status_code} for {method} {full_url}."
            try:
                error_details = e.response.json()
                error_message += f" Response: {json.dumps(error_details)}"
            except json.JSONDecodeError:
                error_message += f" Response Body: {e.response.text[:500]}"  # Log raw response if not JSON
            logger.error(error_message)
            raise RagieApiError(error_message) from e
        except requests.exceptions.RequestException as e:
            # Network errors, timeouts etc.
            logger.error(f"Request failed for {method} {full_url}: {e}")
            raise RagieApiError(f"Request failed: {e}") from e  # Wrap in custom error

    def check_connection(self) -> Optional[str]:
        """Checks API key and connectivity using GET /documents."""
        logger.info(
            f"Performing connection check using GET {self.DOCUMENTS_GENERAL_ENDPOINT} with partition scope: {self.config.partition or 'default'}"
        )
        try:
            # Use the general partition header for this GET request
            response = self._request("GET", self.DOCUMENTS_GENERAL_ENDPOINT, params={"page_size": 1}, extra_headers=self.partition_header)
            logger.info(f"Connection check successful (Endpoint {self.DOCUMENTS_GENERAL_ENDPOINT} responded with {response.status_code}).")
            return None
        except RagieApiError as e:
            error_str = str(e)
            if "401" in error_str:
                return "Authentication failed: Invalid API Key."
            if "403" in error_str:
                return "Authorization failed: API Key lacks permissions for the specified partition or action."
            # Check for other 4xx errors based on the status code in the message
            status_code = None
            if e.__cause__ and isinstance(e.__cause__, requests.exceptions.HTTPError):
                status_code = e.__cause__.response.status_code
            if status_code and 400 <= status_code < 500 and status_code not in [401, 403]:
                return f"Connection check failed with status {status_code}. Check API URL, Partition, and configuration. Error: {error_str}"
            # Generic API error or network error
            return f"Failed to connect to Ragie API at {self.base_url}. Error: {e}"
        except Exception as e:
            logger.error(f"Unexpected error during connection check: {repr(e)}", exc_info=True)
            return f"An unexpected error occurred during connection check: {repr(e)}"

    def index_documents(self, documents: List[Dict[str, Any]]):
        """
        Indexes documents one by one.
        Uses POST /documents/raw for JSON data uploads (application/json).
        """
        if not documents:
            return
        logger.info(f"Indexing {len(documents)} JSON documents one by one...")
        successful_count = 0

        for item_payload in documents:
            doc_id_log = item_payload.get("external_id") or item_payload.get("name", "N/A")

            try:
                # --- Handle JSON Data Upload via POST /documents/raw ---
                endpoint = self.DOCUMENTS_RAW_ENDPOINT
                method = "POST"
                # For JSON uploads, we do want the partition header if set
                headers = self.partition_header

                logger.debug(
                    f"Indexing JSON document via {endpoint}: Name='{item_payload.get('name', 'N/A')}', ExternalID='{item_payload.get('external_id')}'"
                )
                # Make the request with json_data and potential partition header
                self._request(
                    method=method,
                    endpoint=endpoint,
                    json_data=item_payload,  # Send the whole payload as JSON body
                    extra_headers=headers,  # Pass partition header
                )
                logger.debug(
                    f"Successfully requested indexing for JSON document: Name='{item_payload.get('name', 'N/A')}', ExternalID='{item_payload.get('external_id')}'"
                )

                successful_count += 1

            except Exception as e:
                logger.error(f"Failed to index document '{doc_id_log}': {e}", exc_info=True)

                internal_msg = f"PayloadKeys: {list(item_payload.keys())}"
                error_details = str(e) if isinstance(e, RagieApiError) else repr(e)
                internal_msg += f", Error: {error_details}"

                # Determine failure type
                failure_type = FailureType.system_error  # Default
                if isinstance(e, RagieApiError) and e.__cause__:
                    if isinstance(e.__cause__, requests.exceptions.HTTPError):
                        status = e.__cause__.response.status_code
                        if 400 <= status < 500 and status not in [404, 429]:
                            failure_type = FailureType.config_error  # User config likely caused 4xx

                raise AirbyteTracedException(
                    message=f"Failed to index document '{doc_id_log}' into Ragie.",
                    internal_message=internal_msg[:1000],  # Limit length
                    failure_type=failure_type,
                ) from e
        logger.info(f"Successfully processed {successful_count} indexing requests.")

    # --- Metadata Filtering/Querying (_build_filter_json, find_ids_by_metadata, find_docs_by_metadata) ---
    def _build_filter_json(self, filter_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Builds a Ragie filter JSON object structure. (No changes needed)"""
        if not filter_conditions:
            logger.warning("Attempted to build filter JSON from empty conditions.")
            return {}
        and_conditions = []
        supported_operators = {"$eq", "$ne", "$gt", "$gte", "$lt", "$lte", "$in", "$nin"}
        for key, value in filter_conditions.items():
            filter_key_path = f"{key}"

            if isinstance(value, dict) and next(iter(value)) in supported_operators:
                condition = {filter_key_path: value}
            elif isinstance(value, (str, int, float, bool)):
                condition = {filter_key_path: {"$eq": value}}
            elif isinstance(value, list):
                condition = {filter_key_path: {"$in": value}}
            else:
                logger.warning(f"Unsupported value type ({type(value)}) for filter key '{key}'. Skipping condition.")
                continue
            and_conditions.append(condition)
        if not and_conditions:
            return {}
        final_filter_obj = and_conditions[0] if len(and_conditions) == 1 else {"$and": and_conditions}
        logger.debug(f"Built filter JSON: {final_filter_obj}")
        return final_filter_obj

    def find_ids_by_metadata(self, filter_conditions: Dict[str, Any]) -> List[str]:
        """Finds internal Ragie document IDs using GET /documents."""
        logger.info(f"Querying Ragie document IDs with filter: {filter_conditions}")
        found_internal_ids = []
        cursor = None
        page_size = 100
        filter_json_obj = self._build_filter_json(filter_conditions)
        if not filter_json_obj:
            return []
        filter_param_string = json.dumps(filter_json_obj)
        # Use general partition header for GET requests
        headers = self.partition_header
        while True:
            params = {"page_size": page_size, "filter": filter_param_string}
            if cursor:
                params["cursor"] = cursor
            try:
                # Use the general endpoint for listing/querying
                response = self._request("GET", self.DOCUMENTS_GENERAL_ENDPOINT, params=params, extra_headers=headers)
                response_data = response.json()
                documents_on_page = response_data.get("documents", [])
                if not documents_on_page:
                    break
                page_ids = [doc.get("id") for doc in documents_on_page if doc.get("id")]
                found_internal_ids.extend(page_ids)
                logger.debug(f"Found {len(page_ids)} IDs page. Total: {len(found_internal_ids)}")
                cursor = response_data.get("pagination", {}).get("next_cursor")
                if not cursor:
                    break
            except Exception as e:
                logger.error(f"Failed during document ID query (filter='{filter_param_string}', cursor='{cursor}'): {e}", exc_info=True)
                raise AirbyteTracedException(
                    message="Failed to query Ragie document IDs.",
                    internal_message=f"Filter: {filter_param_string}, Error: {e}",
                    failure_type=FailureType.system_error,
                ) from e
        logger.info(f"Found {len(found_internal_ids)} total document IDs matching filter.")
        return found_internal_ids

    def find_docs_by_metadata(self, filter_conditions: Dict[str, Any], fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Finds full documents using GET /documents."""
        logger.info(f"Querying Ragie documents with filter: {filter_conditions}" + (f" fields: {fields}" if fields else ""))
        found_docs = []
        cursor = None
        page_size = 100
        filter_json_obj = self._build_filter_json(filter_conditions)
        if not filter_json_obj:
            return []
        filter_param_string = json.dumps(filter_json_obj)
        # Use general partition header for GET requests
        headers = self.partition_header
        while True:
            params = {"page_size": page_size, "filter": filter_param_string}
            if fields:
                params["fields"] = ",".join(fields)
            if cursor:
                params["cursor"] = cursor
            try:
                # Use the general endpoint for listing/querying
                response = self._request("GET", self.DOCUMENTS_GENERAL_ENDPOINT, params=params, extra_headers=headers)
                response_data = response.json()
                documents_on_page = response_data.get("documents", [])
                if not documents_on_page:
                    break
                found_docs.extend(documents_on_page)
                logger.debug(f"Found {len(documents_on_page)} docs page. Total: {len(found_docs)}")
                cursor = response_data.get("pagination", {}).get("next_cursor")
                if not cursor:
                    break
            except Exception as e:
                logger.error(f"Failed during document query (filter='{filter_param_string}', cursor='{cursor}'): {e}", exc_info=True)
                raise AirbyteTracedException(
                    message="Failed to query Ragie documents.",
                    internal_message=f"Filter: {filter_param_string}, Fields: {fields}, Error: {e}",
                    failure_type=FailureType.system_error,
                ) from e
        logger.info(f"Found {len(found_docs)} total documents matching filter.")
        return found_docs

    # --- Deletion Logic ---
    def delete_documents_by_id(self, internal_ids: List[str]):
        """Deletes documents one by one using DELETE /documents/{internal_id}."""
        if not internal_ids:
            return
        logger.info(f"Attempting to delete {len(internal_ids)} documents by internal Ragie ID.")
        successful_deletes = 0
        failed_deletes = 0
        # Use general partition header for DELETE requests
        headers = self.partition_header
        for internal_id in internal_ids:
            if not internal_id or not isinstance(internal_id, str):
                logger.warning(f"Invalid internal ID for deletion: {internal_id}. Skipping.")
                failed_deletes += 1
                continue
            # Construct endpoint using the general documents endpoint base
            delete_endpoint = f"{self.DOCUMENTS_GENERAL_ENDPOINT}/{internal_id}"
            try:
                self._request("DELETE", delete_endpoint, extra_headers=headers)
                successful_deletes += 1
                logger.debug(f"Successfully deleted document with internal_id: {internal_id}")
            except RagieApiError as e:
                error_str = str(e)
                status_code = None
                if e.__cause__ and isinstance(e.__cause__, requests.exceptions.HTTPError):
                    status_code = e.__cause__.response.status_code

                if status_code == 404:
                    logger.warning(f"Document internal_id {internal_id} not found for deletion (404). Assuming deleted.")
                    successful_deletes += 1  # Count 404 as success during delete
                else:
                    logger.error(f"Failed to delete document internal_id {internal_id}: {e}")
                    failed_deletes += 1
            except Exception as e:
                logger.error(f"Unexpected error deleting document internal_id {internal_id}: {e}", exc_info=True)
                failed_deletes += 1
        logger.info(f"Deletion result: {successful_deletes} successful (incl 404s), {failed_deletes} failures.")
        if failed_deletes > 0:
            raise AirbyteTracedException(
                message=f"Failed to delete {failed_deletes} out of {len(internal_ids)} documents (excluding 404s).",
                failure_type=FailureType.system_error,
            )
