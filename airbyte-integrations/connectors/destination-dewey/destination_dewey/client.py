#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import io
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Mapping, Optional, Tuple

import backoff
import requests

from destination_dewey.config import DeweyConfig


# Dewey upload metadata keys we own. Anything starting with `_ab_` is reserved.
METADATA_STREAM_FIELD = "_ab_stream"
METADATA_NAMESPACE_FIELD = "_ab_namespace"
METADATA_PK_FIELD = "_ab_pk"

STREAM_TAG_PREFIX = "airbyte_stream:"
PK_TAG_PREFIX = "airbyte_pk:"


def normalize_tag(tag: str) -> str:
    """Match Dewey's server-side tag normalization (lowercased + trimmed).

    Dewey applies this in `apps/api/src/routes/documents.ts` (`normalizeTags`) before
    persisting, so any client-side filter must lowercase as well or it will silently
    miss tags that contained uppercase characters at upload time.
    """
    return tag.lower().strip()


# Dewey caps batch deletes at 1000 ids and document listing at 500 per page.
MAX_DELETE_IDS_PER_BATCH = 1000
MAX_LIST_PAGE_SIZE = 500
PARALLELISM_LIMIT = 8

logger = logging.getLogger("airbyte")


def _is_user_error(e: Exception) -> bool:
    if not isinstance(e, requests.exceptions.RequestException):
        return False
    response = e.response
    if response is None:
        return False
    # Don't retry 4xx — except 408 (timeout) and 429 (rate limit), which the caller treats as transient.
    return 400 <= response.status_code < 500 and response.status_code not in (408, 429)


class DeweyApiError(Exception):
    """Raised when Dewey returns a non-2xx response."""

    def __init__(self, status_code: int, body: Any, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class DeweyClient:
    def __init__(self, config: DeweyConfig):
        if isinstance(config, Mapping):
            config = DeweyConfig.parse_obj(config)
        self.api_key = config.api_key
        self.base_url = config.base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
                "User-Agent": "airbyte-destination-dewey",
            }
        )

    # ---- low-level request helpers ------------------------------------------------

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5, giveup=_is_user_error)
    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[Mapping[str, Any]] = None,
        files: Optional[List[Tuple[str, Any]]] = None,
        data: Optional[Mapping[str, Any]] = None,
        params: Optional[Mapping[str, Any]] = None,
        expect_json: bool = True,
    ) -> Any:
        url = f"{self.base_url}{path}"
        kwargs: Dict[str, Any] = {"params": params, "timeout": 60}
        if files is not None:
            kwargs["files"] = files
            if data is not None:
                kwargs["data"] = data
        elif json_body is not None:
            kwargs["json"] = json_body
        response = self.session.request(method, url, **kwargs)
        if not response.ok:
            try:
                body = response.json()
            except ValueError:
                body = response.text
            message = response.text
            if isinstance(body, dict):
                err = body.get("error")
                if isinstance(err, dict):
                    message = err.get("message") or response.text
                elif isinstance(err, str):
                    message = err
                elif "message" in body:
                    message = body.get("message") or response.text
            raise DeweyApiError(response.status_code, body, f"{method} {path} -> {response.status_code}: {message}")
        if not expect_json or response.status_code == 204 or not response.content:
            return None
        return response.json()

    # ---- check ---------------------------------------------------------------------

    def check(self) -> Optional[str]:
        """Return None on success, error string otherwise."""
        try:
            # GET /collections is org-scoped and requires a valid API key. An invalid key
            # returns 401 (Dewey's authenticateApiKey hook); a valid key returns the org's
            # collection list (possibly empty).
            self._request("GET", "/collections")
        except DeweyApiError as e:
            if e.status_code in (401, 403):
                return f"Authentication failed: {e}"
            if e.status_code == 404:
                return f"Endpoint not found at {self.base_url} — verify base_url. ({e})"
            return str(e)
        except requests.exceptions.RequestException as e:
            return f"Could not reach Dewey at {self.base_url}: {e}"
        return None

    # ---- collections ---------------------------------------------------------------

    def get_collection(self, collection_id: str) -> Optional[Mapping[str, Any]]:
        try:
            return self._request("GET", f"/collections/{collection_id}")
        except DeweyApiError as e:
            if e.status_code == 404:
                return None
            raise

    def create_collection(self, name: str, *, visibility: str = "private") -> Mapping[str, Any]:
        return self._request(
            "POST",
            "/collections",
            json_body={"name": name, "visibility": visibility},
        )

    # ---- documents -----------------------------------------------------------------

    def list_documents(
        self,
        collection_id: str,
        *,
        page_size: int = MAX_LIST_PAGE_SIZE,
    ):
        """Yields document dicts across all pages."""
        offset = 0
        while True:
            page = self._request(
                "GET",
                f"/collections/{collection_id}/documents",
                params={"limit": page_size, "offset": offset},
            )
            docs = page.get("documents", []) if isinstance(page, dict) else []
            if not docs:
                return
            for doc in docs:
                yield doc
            if len(docs) < page_size:
                return
            offset += len(docs)

    def upload_document(
        self,
        collection_id: str,
        *,
        filename: str,
        content: bytes,
        content_type: str = "application/json",
        tags: Optional[List[str]] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # tags + metadata as plain form fields (no per-part Content-Type) — works regardless
        # of multipart ordering and avoids any ambiguity about field-vs-file classification.
        form_data: Dict[str, str] = {}
        if tags:
            form_data["tags"] = json.dumps([normalize_tag(t) for t in tags])
        if metadata:
            form_data["metadata"] = json.dumps(metadata)
        files: List[Tuple[str, Any]] = [("file", (filename, io.BytesIO(content), content_type))]
        return self._request(
            "POST",
            f"/collections/{collection_id}/documents",
            files=files,
            data=form_data,
            params={"filename": filename},
        )

    def upload_documents(self, uploads: List[Mapping[str, Any]], *, parallelize: bool) -> List[Mapping[str, Any]]:
        if not uploads:
            return []
        if not parallelize:
            return [self.upload_document(**u) for u in uploads]
        results: List[Mapping[str, Any]] = []
        with ThreadPoolExecutor(max_workers=PARALLELISM_LIMIT) as ex:
            futures = [ex.submit(self.upload_document, **u) for u in uploads]
            for f in as_completed(futures):
                results.append(f.result())
        return results

    def delete_documents(self, collection_id: str, document_ids: List[str]) -> None:
        if not document_ids:
            return
        for i in range(0, len(document_ids), MAX_DELETE_IDS_PER_BATCH):
            chunk = document_ids[i : i + MAX_DELETE_IDS_PER_BATCH]
            self._request(
                "DELETE",
                f"/collections/{collection_id}/documents/batch",
                json_body={"ids": chunk},
                expect_json=False,
            )

    def find_document_ids_by_tag(self, collection_id: str, tag: str) -> List[str]:
        """List collection docs and filter client-side by tag — Dewey lacks server-side tag filter on list."""
        target = normalize_tag(tag)
        ids: List[str] = []
        for doc in self.list_documents(collection_id):
            tags = doc.get("tags") or []
            if target in tags:
                doc_id = doc.get("id")
                if doc_id:
                    ids.append(doc_id)
        return ids
