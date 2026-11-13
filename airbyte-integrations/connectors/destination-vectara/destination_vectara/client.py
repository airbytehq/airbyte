#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import json
import re
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Mapping, Optional
from urllib.parse import quote

import backoff
import requests

from destination_vectara.config import VectaraConfig


METADATA_STREAM_FIELD = "_ab_stream"


def user_error(e: Exception) -> bool:
    """
    Return True if this exception is caused by user error, False otherwise.
    """
    if not isinstance(e, requests.exceptions.RequestException):
        return False
    return bool(e.response is not None and 400 <= e.response.status_code < 500)


class VectaraClient:
    # Vectara REST API v2 (https://docs.vectara.com/docs/rest-api/). API v1 was retired on 2025-08-16.
    BASE_URL = "https://api.vectara.io/v2"
    # OAuth 2.0 client-credentials token endpoint (https://docs.vectara.com/docs/api-reference/auth-apis/oauth-2).
    AUTH_URL = "https://auth.vectara.com/oauth2/token"
    CORPUS_KEY_MAX_LENGTH = 50

    def __init__(self, config: VectaraConfig):
        if isinstance(config, dict):
            config = VectaraConfig.parse_obj(config)
        self.customer_id = config.customer_id
        self.corpus_name = config.corpus_name
        self.client_id = config.oauth2.client_id
        self.client_secret = config.oauth2.client_secret
        self.parallelize = config.parallelize
        self.corpus_key: Optional[str] = None
        self.jwt_token: Optional[str] = None
        self.jwt_token_expires_ts = 0.0
        self.check()

    def check(self):
        """
        Check for an existing corpus in Vectara.
        If more than one exists - then return a message
        If exactly one exists with this name - use it.
        If not, create it with the metadata filter attribute the connector relies on.
        """
        try:
            jwt_token = self._get_jwt_token()
            if not jwt_token:
                return "Unable to get JWT Token. Confirm your Client ID and Client Secret."

            matching_corpora = [corpus for corpus in self._list_corpora() if corpus.get("name") == self.corpus_name]
            if len(matching_corpora) > 1:
                return f"Multiple Corpora exist with name {self.corpus_name}"
            if len(matching_corpora) == 1:
                self.corpus_key = matching_corpora[0].get("key")
            else:
                data = {
                    "key": self._corpus_key_from_name(self.corpus_name),
                    "name": self.corpus_name,
                    "filter_attributes": [
                        {
                            "name": METADATA_STREAM_FIELD,
                            "level": "document",
                            "type": "text",
                            "indexed": True,
                        },
                    ],
                }
                create_corpus_response = self._request(endpoint="corpora", data=data)
                self.corpus_key = create_corpus_response.get("key")

        except Exception as e:
            return str(e) + "\n" + "".join(traceback.TracebackException.from_exception(e).format())

    def _list_corpora(self):
        corpora = []
        params = {"limit": 100, "filter": self.corpus_name}
        while True:
            response = self._request(endpoint="corpora", http_method="GET", params=params)
            corpora.extend(response.get("corpora") or [])
            page_key = (response.get("metadata") or {}).get("page_key")
            if not page_key:
                return corpora
            params = {**params, "page_key": page_key}

    @classmethod
    def _corpus_key_from_name(cls, corpus_name: str) -> str:
        """Corpus keys may only contain [a-zA-Z0-9_=-] and be at most 50 characters long."""
        return re.sub(r"[^a-zA-Z0-9_=\-]", "_", corpus_name)[: cls.CORPUS_KEY_MAX_LENGTH]

    def _get_jwt_token(self):
        """Connect to the server and get a JWT token."""
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "client_credentials", "client_id": self.client_id, "client_secret": self.client_secret}

        request_time = datetime.datetime.now().timestamp()
        response = requests.request(method="POST", url=self.AUTH_URL, headers=headers, data=data)
        response_json = response.json()

        self.jwt_token = response_json.get("access_token")
        self.jwt_token_expires_ts = request_time + (response_json.get("expires_in") or 0)
        return self.jwt_token

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=5, giveup=user_error)
    def _request(self, endpoint: str, http_method: str = "POST", params: Mapping[str, Any] = None, data: Mapping[str, Any] = None):
        url = f"{self.BASE_URL}/{endpoint}"

        current_ts = datetime.datetime.now().timestamp()
        if self.jwt_token_expires_ts - current_ts <= 60:
            self._get_jwt_token()

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.jwt_token}",
            "X-source": "airbyte",
        }

        response = requests.request(
            method=http_method, url=url, headers=headers, params=params, data=json.dumps(data) if data is not None else None
        )
        response.raise_for_status()
        if response.status_code == 204 or not response.content:
            return {}
        return response.json()

    def _documents_endpoint(self) -> str:
        return f"corpora/{quote(self.corpus_key, safe='')}/documents"

    def delete_doc_by_metadata(self, metadata_field_name, metadata_field_values):
        document_ids = []
        for value in metadata_field_values:
            params = {"limit": 1000, "metadata_filter": f"doc.{metadata_field_name} = '{value}'"}
            while True:
                list_documents_response = self._request(endpoint=self._documents_endpoint(), http_method="GET", params=params)
                document_ids.extend([document.get("id") for document in list_documents_response.get("documents") or []])
                page_key = (list_documents_response.get("metadata") or {}).get("page_key")
                if not page_key:
                    break
                params = {**params, "page_key": page_key}
        self.delete_docs_by_id(document_ids=document_ids)

    def delete_docs_by_id(self, document_ids):
        for document_id in document_ids:
            try:
                self._request(endpoint=f"{self._documents_endpoint()}/{quote(document_id, safe='')}", http_method="DELETE")
            except requests.exceptions.HTTPError as e:
                # The document may already have been deleted or never indexed
                if e.response is None or e.response.status_code != 404:
                    raise

    def index_document(self, document):
        document_section, document_metadata, document_title, document_id = document
        if len(document_section) == 0:
            return None  # Document is empty, so skip it
        document_metadata = self._normalize(document_metadata)
        data = {
            "id": document_id,
            "type": "structured",
            "title": document_title,
            "metadata": document_metadata,
            "sections": [
                {"text": f"{section_key}: {section_value}"}
                for section_key, section_value in document_section.items()
                if section_key != METADATA_STREAM_FIELD
            ],
        }
        try:
            return self._request(endpoint=self._documents_endpoint(), data=data)
        except requests.exceptions.HTTPError as e:
            # A document with this id is already indexed; keep the existing one (same behavior as API v1's ALREADY_EXISTS status)
            if e.response is not None and e.response.status_code == 409:
                return None
            raise

    def index_documents(self, documents):
        if self.parallelize:
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(self.index_document, doc) for doc in documents]
                for future in futures:
                    future.result()
        else:
            for doc in documents:
                self.index_document(doc)

    def _normalize(self, metadata: dict) -> dict:
        result = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                result[key] = value
            else:
                # JSON encode all other types
                result[key] = json.dumps(value)
        return result
