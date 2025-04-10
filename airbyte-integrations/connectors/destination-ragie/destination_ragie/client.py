
import datetime
import json
import logging
import time
import traceback
from typing import Any, Mapping, List, Dict, Optional, Set, Union

import backoff
import requests
from airbyte_cdk.utils.traced_exception import AirbyteTracedException, FailureType

from .config import RagieConfig

from .config import RagieConfig

logger = logging.getLogger("airbyte.destination_ragie.client")

# --- Error Handling Functions (remain the same) ---
class RagieApiError(Exception):
    """Custom exception for Ragie API errors."""
    pass

def user_error(e: Exception) -> bool:
    """Return True if this exception is likely a user configuration error (4xx)."""
    if not isinstance(e, requests.exceptions.RequestException):
        return False
    # Exclude 404 from user errors that give up immediately
    return bool(e.response and 400 <= e.response.status_code < 500 and e.response.status_code not in [404, 429])

def transient_error(e: Exception) -> bool:
    """Return True if this exception is likely transient (5xx or rate limit)."""
    if not isinstance(e, requests.exceptions.RequestException):
        return isinstance(e, (requests.exceptions.ConnectionError, requests.exceptions.Timeout))
    return bool(e.response and (e.response.status_code >= 500 or e.response.status_code == 429))
# --- End Error Handling ---


class RagieClient:
    # --- Constants ---
    DEFAULT_API_URL = "https://api.ragie.ai"
    DOCUMENTS_RAW_ENDPOINT = "/documents/raw" # For creating/indexing
    DOCUMENTS_ENDPOINT = "/documents"        # For listing/querying and deleting by internal ID

    # !! CHANGED: Renamed metadata key to avoid leading underscore !!
    METADATA_AIRBYTE_STREAM_FIELD = "airbyte_stream" # Use this key in RagieWriter as well

    def __init__(self, config: RagieConfig):
        self.config = config
        self.base_url = config.api_url.rstrip("/") if config.api_url else self.DEFAULT_API_URL
        self.api_key = config.api_key
        self.session = self._create_session()
        # Store partition header for reuse
        self.partition_header = {"partition": config.partition or "default"}
        logger.info(f"RagieClient initialized. Base URL: {self.base_url}, Partition Scope: {config.partition or 'Default/Account-wide'}")

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-source": "airbyte-destination-ragie"
        })
        return session

    @backoff.on_exception(backoff.expo,
                          requests.exceptions.RequestException,
                          max_tries=5,
                          giveup=user_error,
                          on_backoff=lambda details: logger.warning(f"Transient error detected. Retrying in {details['wait']:.1f}s. Details: {details['exception']}"),
                          factor=3)
    def _request(self,
                 method: str,
                 endpoint: str,
                 params: Optional[Dict[str, Any]] = None,
                 json_data: Optional[Dict[str, Any]] = None,
                 extra_headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """Makes an HTTP request with error handling, retries, and optional extra headers."""
        full_url = f"{self.base_url}{endpoint}"
        request_headers = self.session.headers.copy()
        # Combine session headers with specific request headers (like partition)
        if extra_headers:
            request_headers.update(extra_headers)

        log_data = f" data: {json.dumps(json_data)[:200]}..." if json_data else ""
        log_params = f" params: {params}" if params else ""
        log_headers = f" headers: {request_headers}" # Log all effective headers
        logger.debug(f"Making {method} request to {full_url}{log_params}{log_data}{log_headers}")

        try:
            response = self.session.request(
                method=method,
                url=full_url,
                params=params,
                json=json_data,
                headers=request_headers # Use combined headers
            )
            response.raise_for_status() # Raises HTTPError for 4xx/5xx
            return response
        except requests.exceptions.HTTPError as e:
            error_message = f"HTTP error {e.response.status_code} for {method} {full_url}."
            try:
                error_details = e.response.json()
                error_message += f" Response: {json.dumps(error_details)}"
            except json.JSONDecodeError:
                error_message += f" Response Body: {e.response.text[:500]}"
            logger.error(error_message)
            raise e
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {method} {full_url}: {e}")
            raise e

    def check_connection(self) -> Optional[str]:
        """Checks API key and connectivity. Returns error message string or None if successful."""
        logger.info(f"Performing connection check using GET {self.DOCUMENTS_ENDPOINT} with partition scope: {self.config.partition or 'Default/Account-wide'}")
        try:
            response = self._request(
                "GET",
                self.DOCUMENTS_ENDPOINT,
                params={"page_size": 1},
                extra_headers=self.partition_header # Pass partition header
            )
            logger.info(f"Connection check successful (Endpoint {self.DOCUMENTS_ENDPOINT} responded with {response.status_code}).")
            return None
        except requests.exceptions.RequestException as e:
            if e.response is not None:
                if e.response.status_code == 401:
                    return "Authentication failed: Invalid API Key."
                if e.response.status_code == 403:
                    return "Authorization failed: API Key lacks permissions for the specified partition or action."
                if 400 <= e.response.status_code < 500:
                    return f"Connection check failed with status {e.response.status_code}. Check API URL, Partition, and configuration. Response: {e.response.text[:500]}"
            return f"Failed to connect to Ragie API at {self.base_url}. Error: {e}"
        except Exception as e:
            logger.error(f"Unexpected error during connection check: {repr(e)}", exc_info=True)
            return f"An unexpected error occurred during connection check: {repr(e)}"

    def index_documents(self, documents: List[Dict[str, Any]]):
        """Indexes documents one by one using POST /documents/raw."""
        if not documents:
            return
        logger.info(f"Indexing {len(documents)} documents one by one...")
        successful_count = 0
        # Use partition header if configured
        headers = self.partition_header

        for doc_payload in documents:
            try:
                self._request(
                    "POST",
                    self.DOCUMENTS_RAW_ENDPOINT,
                    json_data=doc_payload,
                    extra_headers=headers # Pass partition header
                )
                successful_count += 1
                logger.debug(f"Successfully indexed document: Name='{doc_payload.get('name', 'N/A')}', ExternalID='{doc_payload.get('external_id')}'")
            except Exception as e:
                doc_id = doc_payload.get("external_id") or doc_payload.get("name", "N/A")
                logger.error(f"Failed to index document '{doc_id}': {e}", exc_info=True)
                raise AirbyteTracedException(
                    message=f"Failed to index document '{doc_id}'",
                    internal_message=f"Payload: {json.dumps(doc_payload)[:500]}... Error: {e}",
                    failure_type=FailureType.system_error
                ) from e
        logger.info(f"Successfully indexed {successful_count} documents.")


    def _format_filter_value(self, value: Any) -> str:
        """Formats a Python value for Ragie filter strings."""
        if isinstance(value, str):
            # Escape single quotes within the string if necessary
            escaped_value = value.replace("'", "\\'")
            return f"'{escaped_value}'"
        elif isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            # Fallback for unexpected types - log warning and convert to string
            logger.warning(f"Unsupported type for filtering: {type(value)}. Converting to string.")
            return f"'{str(value)}'"
    # NEW: Function to build the filter JSON object
    def _build_filter_json(self, filter_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds a Ragie filter JSON object structure from a dictionary.
        Assumes simple key-value inputs imply $eq and multiple conditions are combined with $and.
        Handles determining if the key is top-level (external_id) or metadata.
        """
        if not filter_conditions:
            logger.warning("Attempted to build filter JSON from empty conditions.")
            return {} # Return empty dict if no conditions

        and_conditions = []
        supported_operators = {"$eq", "$ne", "$gt", "$gte", "$lt", "$lte", "$in", "$nin"}

        for key, value in filter_conditions.items():
            # 1. Determine the filter key path (metadata. vs top-level)
            #    Based on Ragie docs, only specific fields are top-level. Assume 'external_id'.
            #    All user-defined fields go under 'metadata.'.
            if key == "external_id":
                filter_key_path = "external_id"
            # Add other known top-level filterable fields if discovered (e.g., 'id', 'name'?)
            # elif key == "id": filter_key_path = "id"
            else:
                # Assume it's a user-defined metadata field
                filter_key_path = f"{key}"

            # 2. Check if the value already includes an operator
            if isinstance(value, dict) and next(iter(value)) in supported_operators:
                # Value is already in the correct operator format, e.g., {"$gte": 2020}
                condition = {filter_key_path: value}
                logger.debug(f"Using pre-structured operator for filter key '{filter_key_path}': {value}")
            elif isinstance(value, (str, int, float, bool, list)):
                 # If simple value (or list, maybe for future $in use), assume $eq
                 # List values are only valid with $in/$nin according to docs, but we default to $eq here.
                 # This might need refinement if $in is passed via simple lists.
                 condition = {filter_key_path: {"$eq": value}}
                 logger.debug(f"Applying default '$eq' operator for filter key '{filter_key_path}' with value: {value}")
            else:
                 # Log warning and skip unsupported types
                 logger.warning(f"Unsupported value type ({type(value)}) for filter key '{key}'. Skipping this filter condition.")
                 continue # Skip this key-value pair

            and_conditions.append(condition)

        # 3. Combine conditions
        if not and_conditions:
            return {} # No valid conditions were built
        elif len(and_conditions) == 1:
            # If only one condition, return it directly without $and wrapper
            final_filter_obj = and_conditions[0]
            logger.debug(f"Built single filter condition: {final_filter_obj}")
            return final_filter_obj
        else:
            # If multiple conditions, wrap them in $and
            final_filter_obj = {"$and": and_conditions}
            logger.debug(f"Built combined filter conditions with '$and': {final_filter_obj}")
            return final_filter_obj

    def find_ids_by_metadata(self, filter_conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Finds documents matching filter conditions using GET /documents.
        Handles pagination and returns a list of dicts [{'internal_id': '...'}]
        """
        logger.info(f"Querying Ragie for documents with filter conditions: {filter_conditions}")
        found_docs_summary = []
        cursor = None
        page_size = 100 # Max allowed per docs

        # Build the filter JSON object structure
        filter_json_obj = self._build_filter_json(filter_conditions)
        if not filter_json_obj:
            logger.warning("Filter conditions resulted in an empty filter object. Cannot query.")
            return [] # Return empty list if filter is invalid/empty

        # Convert the JSON object to a string for the query parameter
        # Requests library usually handles URL encoding for params dictionary values
        filter_param_string = json.dumps(filter_json_obj)
        logger.info(f"Using filter string for query parameter: {filter_param_string}")

        # Use partition header if configured
        headers = self.partition_header

        while True:
            params = {
                "page_size": page_size,
                "filter": filter_param_string, # Pass the JSON string here
            }
            if cursor:
                params["cursor"] = cursor

            try:
                response = self._request(
                    "GET",
                    self.DOCUMENTS_ENDPOINT,
                    params=params,
                    extra_headers=headers
                )
                response_data = response.json()

                documents_on_page = response_data.get("documents", [])
                if not documents_on_page:
                    logger.debug("No more documents found on this page.")
                    break

                page_results = []
                for doc in documents_on_page:
                     internal_id = doc.get("id")
                     if internal_id:
                         # Only need internal_id for deletion logic later
                         page_results.append(internal_id)
                     else:
                          logger.warning(f"Found document in response without internal 'id': {doc}")

                found_docs_summary.extend(page_results)
                logger.debug(f"Found {len(page_results)} documents on this page. Total found so far: {len(found_docs_summary)}")

                pagination_info = response_data.get("pagination", {})
                cursor = pagination_info.get("next_cursor")
                if not cursor:
                    logger.debug("No next_cursor returned, assuming end of results.")
                    break
                else:
                    logger.debug(f"Received next_cursor: {cursor[:10]}...")

            except Exception as e:
                logger.error(f"Failed during document query (filter='{filter_param_string}', cursor='{cursor}'): {e}", exc_info=True)
                raise AirbyteTracedException(
                    message=f"Failed to query Ragie documents using filter.",
                    internal_message=f"Filter: {filter_param_string}, Error: {e}",
                    failure_type=FailureType.system_error
                ) from e

        logger.info(f"Found total of {len(found_docs_summary)} documents matching filter conditions: {filter_conditions}")
        return found_docs_summary

    def find_docs_by_metadata(self, filter_conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Finds documents matching filter conditions using GET /documents.
        Handles pagination and returns a list of dicts [{'internal_id': '...'}]
        """
        logger.info(f"Querying Ragie for documents with filter conditions: {filter_conditions}")
        found_docs_summary = []
        cursor = None
        page_size = 100 # Max allowed per docs

        # Build the filter JSON object structure
        filter_json_obj = self._build_filter_json(filter_conditions)
        if not filter_json_obj:
            logger.warning("Filter conditions resulted in an empty filter object. Cannot query.")
            return [] # Return empty list if filter is invalid/empty

        # Convert the JSON object to a string for the query parameter
        # Requests library usually handles URL encoding for params dictionary values
        filter_param_string = json.dumps(filter_json_obj)
        logger.info(f"Using filter string for query parameter: {filter_param_string}")

        # Use partition header if configured
        headers = self.partition_header

        while True:
            params = {
                "page_size": page_size,
                "filter": filter_param_string, # Pass the JSON string here
            }
            if cursor:
                params["cursor"] = cursor

            try:
                response = self._request(
                    "GET",
                    self.DOCUMENTS_ENDPOINT,
                    params=params,
                    extra_headers=headers
                )
                response_data = response.json()

                documents_on_page = response_data.get("documents", [])
                if not documents_on_page:
                    logger.debug("No more documents found on this page.")
                    break

                page_results = []
                for doc in documents_on_page:
                    # Only need internal_id for deletion logic later
                    page_results.append(doc)

                found_docs_summary.extend(page_results)
                logger.debug(f"Found {len(page_results)} documents on this page. Total found so far: {len(found_docs_summary)}")

                pagination_info = response_data.get("pagination", {})
                cursor = pagination_info.get("next_cursor")
                while cursor !='null':
                    self._request(
                        "GET",
                        self.DOCUMENTS_ENDPOINT,
                        params=params,
                        extra_headers=headers
                    )
                if not cursor:
                    logger.debug("No next_cursor returned, assuming end of results.")
                    break
                else:
                    logger.debug(f"Received next_cursor: {cursor[:10]}...")

            except Exception as e:
                logger.error(f"Failed during document query (filter='{filter_param_string}', cursor='{cursor}'): {e}", exc_info=True)
                raise AirbyteTracedException(
                    message=f"Failed to query Ragie documents using filter.",
                    internal_message=f"Filter: {filter_param_string}, Error: {e}",
                    failure_type=FailureType.system_error
                ) from e

        logger.info(f"Found total of {len(found_docs_summary)} documents matching filter conditions: {filter_conditions}")
        return found_docs_summary


    def delete_documents_by_id(self, internal_ids: List[str]):
        """Deletes documents one by one using DELETE /documents/{internal_id}."""
        if not internal_ids:
            return
        logger.info(f"Attempting to delete {len(internal_ids)} documents by internal Ragie ID.")

        successful_deletes = 0
        failed_deletes = 0
        # Use partition header if configured
        headers = self.partition_header

        for internal_id in internal_ids:
            # Construct endpoint using the internal ID
            delete_endpoint = f"{self.DOCUMENTS_ENDPOINT}/{internal_id}"
            try:
                self._request(
                    "DELETE",
                    delete_endpoint,
                    extra_headers=headers # Pass partition header
                )
                successful_deletes += 1
                logger.debug(f"Successfully deleted document with internal_id: {internal_id}")
            except requests.exceptions.HTTPError as e:
                 if e.response.status_code == 404:
                     logger.warning(f"Document with internal_id {internal_id} not found for deletion (status 404). Assuming already deleted.")
                     successful_deletes +=1 # Count as success
                 else:
                     logger.error(f"Failed to delete document with internal_id {internal_id}: {e}")
                     failed_deletes += 1
            except Exception as e:
                 logger.error(f"Unexpected error deleting document with internal_id {internal_id}: {e}", exc_info=True)
                 failed_deletes += 1

        logger.info(f"Deletion result: {successful_deletes} successful requests, {failed_deletes} failed.")
        if failed_deletes > 0:
             raise AirbyteTracedException(
                 message=f"Failed to delete {failed_deletes} out of {len(internal_ids)} documents. Check logs for details.",
                 failure_type=FailureType.system_error
             )