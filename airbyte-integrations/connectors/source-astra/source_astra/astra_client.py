import json
import logging
from typing import Any, Dict, List, Optional, Union

import requests
from pydantic.dataclasses import dataclass

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@dataclass
class Response:
    id: str
    text: Optional[str]
    values: Optional[list]
    metadata: Optional[dict]
    score: Optional[float]


@dataclass
class QueryResponse:
    matches: List[Response]

    def get(self, key):
        return self.__dict__[key]


class AstraClient:
    """
    A client for interacting with an Astra index via JSON API
    """

    def __init__(
        self,
        astra_endpoint: str,
        astra_application_token: str,
        keyspace_name: str,
        collection_name: str,
        embedding_dim: int,
        similarity_function: str,
    ):
        self.astra_endpoint = astra_endpoint
        self.astra_application_token = astra_application_token
        self.keyspace_name = keyspace_name
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim
        self.similarity_function = similarity_function

        self.request_url = f"{self.astra_endpoint}/api/json/v1/{self.keyspace_name}/{self.collection_name}"
        self.request_header = {
            "x-cassandra-token": self.astra_application_token,
            "Content-Type": "application/json",
        }
        self.create_url = (
            f"{self.astra_endpoint}/api/json/v1/{self.keyspace_name}"
        )

        index_exists = self.find_index()
        if not index_exists:
            self.create_index()

    def find_index(self):
        find_query = {"findCollections": {"options": {"explain": True}}}
        response = requests.request("POST", self.create_url, headers=self.request_header, data=json.dumps(find_query))
        response_dict = json.loads(response.text)

        if response.status_code == 200:
            if "status" in response_dict:
                collection_name_matches = list(
                    filter(lambda d: d['name'] == self.collection_name, response_dict["status"]["collections"])
                )

                if len(collection_name_matches) == 0:
                    logger.warning(
                        f"Astra collection {self.collection_name} not found under {self.keyspace_name}. Will be created."
                    )
                    return False

                collection_embedding_dim = collection_name_matches[0]["options"]["vector"]["dimension"]
                if collection_embedding_dim != self.embedding_dim:
                    raise Exception(
                        f"Collection vector dimension is not valid, expected {self.embedding_dim}, "
                        f"found {collection_embedding_dim}"
                    )

            else:
                raise Exception(f"status not in response: {response.text}")

        else:
            raise Exception(f"Astra DB not available. Status code: {response.status_code}, {response.text}")
            # Retry or handle error better

        return True

    def create_index(self):
        create_query = {
            "createCollection": {
                "name": self.collection_name,
                "options": {"vector": {"dimension": self.embedding_dim, "metric": self.similarity_function}},
            }
        }
        response = requests.request("POST", self.create_url, headers=self.request_header, data=json.dumps(create_query))
        response_dict = json.loads(response.text)
        if response.status_code == 200 and "status" in response_dict:
            logger.info(f"Collection {self.collection_name} created: {response.text}")
        else:
            raise Exception(
                f"Create Astra collection ailed with the following error: status code {response.status_code}, {response.text}"
            )

    def query(
        self,
        vector: Optional[List[float]] = None,
        filter: Optional[Dict[str, Union[str, float, int, bool, List, dict]]] = None,
        top_k: Optional[int] = None,
        namespace: Optional[str] = None,
        include_metadata: Optional[bool] = None,
        include_values: Optional[bool] = None,
    ) -> QueryResponse:
        """
        The Query operation searches a namespace, using a query vector.
        It retrieves the ids of the most similar items in a namespace, along with their similarity scores.

        Args:
            vector (List[float]): The query vector. This should be the same length as the dimension of the index
                                  being queried. Each `query()` request can contain only one of the parameters
                                  `queries`, `id` or `vector`.. [optional]
            top_k (int): The number of results to return for each query. Must be an integer greater than 1.
            filter (Dict[str, Union[str, float, int, bool, List, dict]):
                    The filter to apply. You can use vector metadata to limit your search. [optional]
            include_metadata (bool): Indicates whether metadata is included in the response as well as the ids.
                                     If omitted the server will use the default value of False  [optional]
            include_values (bool): Indicates whether values/vector is included in the response as well as the ids.
                                     If omitted the server will use the default value of False  [optional]

        Returns: object which contains the list of the closest vectors as ScoredVector objects,
                 and namespace name.
        """
        # get vector data and scores
        if vector is None:
            responses = self._query_without_vector(top_k, filter)
        else:
            responses = self._query(vector, top_k, filter)

        # include_metadata means return all columns in the table (including text that got embedded)
        # include_values means return the vector of the embedding for the searched items
        formatted_response = self._format_query_response(responses, include_metadata, include_values)

        return formatted_response

    def _query_without_vector(self, top_k, filters=None):
        query = {"filter": filters, "options": {"limit": top_k}}
        return self.find_documents(query)

    @staticmethod
    def _format_query_response(responses, include_metadata, include_values):
        final_res = []
        for response in responses:
            _id = response.pop("_id")
            score = response.pop("$similarity") if "$similarity" in response else None
            _values = response.pop("$vector") if "$vector" in response else None
            text = response.pop("text") if "text" in response else None
            values = _values if include_values else []
            # TODO double check
            metadata = response.pop("metadata") if "metadata" in response and include_metadata else dict()
            rsp = Response(_id, text, values, metadata, score)
            final_res.append(rsp)
        return QueryResponse(final_res)

    def _query(self, vector, top_k, filters=None):
        query = {"sort": {"$vector": vector}, "options": {"limit": top_k, "includeSimilarity": True}}
        if filters is not None:
            query["filter"] = filters
        result = self.find_documents(query)
        return result

    def find_documents(self, find_query):
        query = json.dumps({"find": find_query})
        response = requests.request(
            "POST",
            self.request_url,
            headers=self.request_header,
            data=query,
        )
        response_dict = json.loads(response.text)
        if response.status_code == 200:
            if "data" in response_dict and "documents" in response_dict["data"]:
                return response_dict["data"]["documents"]
            else:
                logger.warning("No documents found", response_dict)
        else:
            raise Exception(f"Astra DB request error - status code: {response.status_code} response {response.text}")

    def get_documents(self, ids: List[str], batch_size: int = 20) -> QueryResponse:
        document_batch = []

        def batch_generator(chunks, batch_size):
            for i in range(0, len(chunks), batch_size):
                i_end = min(len(chunks), i + batch_size)
                batch = chunks[i:i_end]
                yield batch

        for id_batch in batch_generator(ids, batch_size):
            document_batch.extend(self.find_documents({"filter": {"_id": {"$in": id_batch}}}))
        formatted_docs = self._format_query_response(document_batch, include_metadata=True, include_values=True)
        return formatted_docs

    def insert(self, documents: List[Dict]):
        query = json.dumps({"insertMany": {"options": {"ordered": False}, "documents": documents}})
        response = requests.request(
            "POST",
            self.request_url,
            headers=self.request_header,
            data=query,
        )
        response_dict = json.loads(response.text)

        if response.status_code == 200:
            inserted_ids = (
                response_dict["status"]["insertedIds"]
                if "status" in response_dict and "insertedIds" in response_dict["status"]
                else []
            )
            if "errors" in response_dict:
                logger.error(response_dict["errors"])
            return inserted_ids
        else:
            raise Exception(f"Astra DB request error - status code: {response.status_code} response {response.text}")

    def update_document(self, document: Dict, id_key: str):
        document_id = document.pop(id_key)
        query = json.dumps(
            {
                "findOneAndUpdate": {
                    "filter": {id_key: document_id},
                    "update": {"$set": document},
                    "options": {"returnDocument": "after"},
                }
            }
        )
        response = requests.request(
            "POST",
            self.request_url,
            headers=self.request_header,
            data=query,
        )
        response_dict = json.loads(response.text)
        document[id_key] = document_id

        if response.status_code == 200:
            if "status" in response_dict and "errors" not in response_dict:
                if "matchedCount" in response_dict["status"] and "modifiedCount" in response_dict["status"]:
                    if response_dict["status"]["matchedCount"] == 1 and response_dict["status"]["modifiedCount"] == 1:
                        return True
            logger.warning(f"Documents {document_id} not updated in Astra {response.text}")
            return False
        else:
            raise Exception(f"Astra DB request error - status code: {response.status_code} response {response.text}")

    def delete(
        self,
        ids: Optional[List[str]] = None,
        delete_all: Optional[bool] = None,
        filter: Optional[Dict[str, Union[str, float, int, bool, List, dict]]] = None,
    ) -> Response:
        if delete_all:
            query = {"deleteMany": {}}
        if ids is not None:
            query = {"deleteMany": {"filter": {"_id": {"$in": ids}}}}
        if filter is not None:
            query = {"deleteMany": {"filter": filter}}
        response = requests.request(
            "POST",
            self.request_url,
            headers=self.request_header,
            data=json.dumps(query),
        )
        return response

    def count_documents(self) -> int:
        """
        Returns how many documents are present in the document store.
        """
        count = requests.request(
            "POST",
            self.request_url,
            headers=self.request_header,
            data=json.dumps({"countDocuments": {}}),
        ).json()["status"]["count"]
        return count
