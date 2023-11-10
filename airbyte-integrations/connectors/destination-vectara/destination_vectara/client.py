#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import json
import requests
import traceback
import uuid

from typing import Any, Mapping

from destination_vectara.config import VectaraConfig



METADATA_STREAM_FIELD = "_ab_stream"
# METADATA_RECORD_ID_FIELD = "_ab_record_id"

class VectaraClient:

    BASE_URL = "https://api.vectara.io/v1"

    def __init__(self, config: VectaraConfig):
        self.customer_id = config.customer_id
        self.corpus_name = config.corpus_name
        self.client_id = config.oauth2.client_id
        self.client_secret = config.oauth2.client_secret
        # self.corpus_id = config.corpus_id

    def check(self):
        try:
            jwt_token = self._get_jwt_token()
            if not jwt_token:
                return "Unable to get JWT Token. Confirm your Client ID and Client Secret."

            list_corpora_response = self._request(
                endpoint="list-corpora",
                data={
                    "numResults": 100, 
                    "filter": self.corpus_name
                    }
                )
            possible_corpora_ids_names_map = {corpus.get("id"): corpus.get("name") for corpus in list_corpora_response.get("corpus") if corpus.get("name") == self.corpus_name}
            if len(possible_corpora_ids_names_map) > 1:
                return f"Multiple Corpora exist with name {self.corpus_name}"
            if len(possible_corpora_ids_names_map) == 1:
                self.corpus_id = list(possible_corpora_ids_names_map.keys())[0]
            else:
                create_corpus_response = self._request(
                    endpoint="create-corpus",
                    data={
                        "corpus": {
                            "name": self.corpus_name,
                            "filterAttributes": [
                                    {
                                        "name": METADATA_STREAM_FIELD,
                                        "indexed": True,
                                        "type": "FILTER_ATTRIBUTE_TYPE__TEXT",
                                        "level": "FILTER_ATTRIBUTE_LEVEL__DOCUMENT"
                                    },
                                    # {
                                    #     "name": METADATA_RECORD_ID_FIELD,
                                    #     "indexed": True,
                                    #     "type": "FILTER_ATTRIBUTE_TYPE__TEXT",
                                    #     "level": "FILTER_ATTRIBUTE_LEVEL__DOCUMENT"
                                    # }
                                ]
                            }
                        }
                    )
                self.corpus_id = create_corpus_response.get("corpusId")

        except Exception as e:
            return str(e) + "\n" + "".join(traceback.TracebackException.from_exception(e).format())
        
    def _get_jwt_token(self):
        """Connect to the server and get a JWT token."""
        token_endpoint = f"https://vectara-prod-{self.customer_id}.auth.us-west-2.amazoncognito.com/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            }
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        request_time = datetime.datetime.now().timestamp()
        response = requests.request(method="POST", url=token_endpoint, headers=headers, data=data)
        response_json = response.json()

        self.jwt_token = response_json.get("access_token")
        self.jwt_token_expires_ts = request_time + response_json.get("expires_in")
        return self.jwt_token
    
    def _request(
        self, endpoint: str, http_method: str = "POST", params: Mapping[str, Any] = None, data: Mapping[str, Any] = None
        ):
        
        url = f"{self.BASE_URL}/{endpoint}"

        current_ts = datetime.datetime.now().timestamp()
        if self.jwt_token_expires_ts - current_ts <= 60:
            self._get_jwt_token()

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json", 
            "Authorization": f"Bearer {self.jwt_token}",
            "customer-id": self.customer_id
            }

        response = requests.request(method=http_method, url=url, headers=headers, params=params, data=json.dumps(data))
        response.raise_for_status()
        return response.json()

    def _delete_doc_by_metadata(self, metadata_field_name, metadata_field_values):
        document_ids = []
        for value in metadata_field_values:
            query_documents_response = self._request(
                endpoint="query",
                data= {
                    "query": [
                            {
                                "query": "", 
                                "numResults": 100,
                                "corpusKey": [
                                    {
                                    "customerId": self.customer_id,
                                    "corpusId": self.corpus_id,
                                    "metadataFilter": f"doc.{metadata_field_name} = '{value}'"
                                    }
                                ]
                            }
                        ]
                    }
                )
            document_ids.extend([document.get("id") for document in query_documents_response.get("responseSet").get("document")])
        documents_not_deleted = []
        for document_id in document_ids:
            delete_document_response = self._request(
                endpoint="delete-doc",
                data={
                    "customerId": self.customer_id, 
                    "corpusId": self.corpus_id,
                    "documentId": document_id
                    }
                )
            # TODO whether this is needed?
            if delete_document_response:
                documents_not_deleted.append(document_id)
        return documents_not_deleted

    def _index_documents(self, documents):
        for stream_name, document_content in documents:            
            document_metadata = self._normalize({METADATA_STREAM_FIELD: stream_name})
            index_document_response = self._request(
                endpoint="index",
                data={
                        "customerId": self.customer_id, 
                        "corpusId": self.corpus_id,
                        "document": {
                            "documentId": uuid.uuid4().int,
                            "metadataJson": json.dumps(document_metadata),
                            "section": [
                                {
                                    "title": "Content",
                                    "text": document_content,
                                }
                            ]
                        }
                    }
                )
            assert index_document_response.get("status").get("code") == "OK", index_document_response.get("status").get("statusDetail")
    
    def _normalize(self, metadata: dict) -> dict:
        result = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                result[key] = value
            else:
                # JSON encode all other types
                result[key] = json.dumps(value)
        return result
