#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import abstractmethod
from string import Template
from typing import Any, List, Union

from graphql_query import Argument, Field, Operation, Query

PARERNT_KEY: str = "__parentId"


class ShopifyBulkTemplates:
    @staticmethod
    def status(bulk_job_id: str) -> str:
        return Template(
            """query {
                    node(id: "$job_id") {
                        ... on BulkOperation {
                            id
                            status
                            errorCode
                            objectCount
                            fileSize
                            url
                            partialDataUrl
                        }
                    }
                }"""
        ).substitute(job_id=bulk_job_id)

    @staticmethod
    def prepare(query: str) -> str:
        bulk_template = Template(
            '''mutation {
                bulkOperationRunQuery(
                    query: """
                    $query
                    """
                ) {
                    bulkOperation {
                        id
                        status
                    }
                    userErrors {
                        field
                        message
                    }
                }
            }'''
        )
        return bulk_template.substitute(query=query)


class GraphQlQueryBuilder:

    operation = "query"
    edge_key = "edges"
    node_key = "node"

    def get_edge(self, name: str, fields: Union[List[str], List[Field], str]) -> Field:
        """
        Defines the edge of the graph and it's fields to select.
        """
        return Field(name=name, fields=[Field(name=self.edge_key, fields=[Field(name=self.node_key, fields=fields)])])

    def get_query(self, name: str, edges: Union[List[Field], Field] = None, filter_query: str = None, sort_key: str = None) -> Query:
        """
        Defines the root of the graph with edges.
        """
        args: List[Argument] = []
        # constructing arguments
        if filter_query:
            args.append(Argument(name=self.operation, value=f'"{filter_query}"'))
        if sort_key:
            args.append(Argument(name="sortKey", value=sort_key))
        # constructing edges
        fields = [
            Field(name=self.edge_key, fields=[Field(name=self.node_key, fields=["id", edges] if edges else ["id"])]),
        ]
        # return constucted query
        return Query(name=name, arguments=args, fields=fields)


class ShopifyBulkQuery(GraphQlQueryBuilder):
    @property
    @abstractmethod
    def record_identifier(self) -> str:
        """
        Defines the record identifier to fetch only records related to the choosen stream.
        Example:
            { "admin_graphql_api_id": "gid://shopify/Metafield/22533588451517" }
            In this example the record could be identified by it's reference = ".../Metafield/..."
        The property should be defined like:
            record_identifier = "Metafield"
        """

    @property
    @abstractmethod
    def graph_edge(self) -> str:
        """
        Defines the final graph node name to fetch from.
        """

    @property
    @abstractmethod
    def graph_fields(self) -> Union[List[str], List[Any]]:
        """
        Defines the fields for final graph selection.
        """

    @abstractmethod
    def resolve_query(
        self,
        query_path: Union[List[str], str] = None,
        filter_query: str = None,
        sort_key: str = None,
    ) -> Operation:
        """
        Defines how query object should be resolved based on the base query selection.
        """

    def __new__(
        self,
        query_path: Union[List[str], str] = None,
        filter_field: str = None,
        start: str = None,
        end: str = None,
        sort_key: str = None,
    ) -> str:
        if not query_path:
            raise NotImplementedError("The `query_path` is not defined.")
        else:
            # define query string
            filter_query = f"{filter_field}:>='{start}' AND {filter_field}:<='{end}'" if filter_field else None
            return self.resolve_query(self, query_path, filter_query, sort_key)


class Metafields(ShopifyBulkQuery):

    record_identifier = "Metafield"
    graph_edge = "metafields"

    # list of available fieds:
    # https://shopify.dev/docs/api/admin-graphql/unstable/objects/Metafield
    graph_fields = [
        "id",
        "namespace",
        "value",
        "key",
        "description",
        "createdAt",
        "updatedAt",
        "type",
    ]

    def resolve_query(
        self,
        query_path: Union[List[str], str] = None,
        filter_query: str = None,
        sort_key: str = None,
    ) -> Operation:
        """
        Defines how query object should be constructed and resolved based on the base query selection.
        """
        if isinstance(query_path, list):
            if len(query_path) == 2:
                edges = self.get_edge(self, query_path[1], ["id", self.get_edge(self, self.graph_edge, self.graph_fields)])
                query = self.get_query(self, query_path[0], edges, filter_query, sort_key)
            if len(query_path) == 3:
                edges = self.get_edge(
                    self,
                    query_path[1],
                    ["id", self.get_edge(self, query_path[2], ["id", self.get_edge(self, self.graph_edge, self.graph_fields)])],
                )
                query = self.get_query(self, query_path[0], edges, filter_query, sort_key)
            if len(query_path) == 1:
                query = self.get_query(self, query_path[0], self.get_edge(self, self.graph_edge, self.graph_fields), filter_query, sort_key)
        elif isinstance(query_path, str):
            query = self.get_query(self, query_path, self.get_edge(self, self.graph_edge, self.graph_fields), filter_query, sort_key)

        return Operation(type="", queries=[query]).render()
