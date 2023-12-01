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

    def get_edge_node(self, name: str, fields: Union[List[str], List[Field], str]) -> Field:
        """
        Defines the edge of the graph and it's fields to select for Shopify BULK Operaion.
        https://shopify.dev/docs/api/usage/bulk-operations/queries#the-jsonl-data-format
        """
        return Field(name=name, fields=[Field(name=self.edge_key, fields=[Field(name=self.node_key, fields=fields)])])

    def build_query(self, name: str, edges: Union[List[Field], Field] = None, filter_query: str = None, sort_key: str = None) -> Query:
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


class ShopifyBulkQuery:

    builder: GraphQlQueryBuilder = GraphQlQueryBuilder()

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
    def edge_name(self) -> str:
        """
        Defines the root graph node name to fetch from.
        https://shopify.dev/docs/api/admin-graphql
        """

    @property
    @abstractmethod
    def edge_nodes(self) -> Union[List[str], List[Any]]:
        """
        Defines the fields for final graph selection.
        https://shopify.dev/docs/api/admin-graphql
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
            # define filter query string
            filter_query = f"{filter_field}:>='{start}' AND {filter_field}:<='{end}'" if filter_field else None
            return self.resolve_query(self, query_path, filter_query, sort_key)


class Metafields(ShopifyBulkQuery):

    record_identifier = "Metafield"
    edge_name = "metafields"

    # list of available fieds:
    # https://shopify.dev/docs/api/admin-graphql/unstable/objects/Metafield
    edge_nodes = [
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
        Defines how query object should be constructed and resolved based on the root query selection.
        Only 2 lvl nesting is available: https://shopify.dev/docs/api/usage/bulk-operations/queries#operation-restrictions
        """

        if isinstance(query_path, list):
            if len(query_path) == 2:
                edges = self.builder.get_edge_node(query_path[1], ["id", self.builder.get_edge_node(self.edge_name, self.edge_nodes)])
                query = self.builder.build_query(query_path[0], edges, filter_query, sort_key)
            if len(query_path) == 3:
                edges = self.builder.get_edge_node(
                    query_path[1],
                    ["id", self.builder.get_edge_node(query_path[2], ["id", self.builder.get_edge_node(self.edge_name, self.edge_nodes)])],
                )
                query = self.builder.build_query(query_path[0], edges, filter_query, sort_key)
            if len(query_path) == 1:
                query = self.builder.build_query(
                    query_path[0], self.builder.get_edge_node(self.edge_name, self.edge_nodes), filter_query, sort_key
                )
        elif isinstance(query_path, str):
            query = self.builder.build_query(
                query_path, self.builder.get_edge_node(self.edge_name, self.edge_nodes), filter_query, sort_key
            )

        return Operation(type="", queries=[query]).render()
