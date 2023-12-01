#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import abstractmethod
from string import Template
from typing import List, Optional, Union

from graphql_query import Argument, Field, Operation, Query

PARENT_KEY: str = "__parentId"


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

    def build_query(
        self,
        name: str,
        edges: Optional[Union[List[Field], Field]] = None,
        filter_query: Optional[str] = None,
        sort_key: Optional[str] = None,
    ) -> Query:
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
    def edge_nodes(self) -> List[str]:
        """
        Defines the fields for final graph selection.
        https://shopify.dev/docs/api/admin-graphql
        """

    @abstractmethod
    def resolve_query(
        self,
        query_path: Optional[Union[List[str], str]] = None,
        filter_query: Optional[str] = None,
        sort_key: Optional[str] = None,
    ) -> str:
        """
        Defines how query object should be resolved based on the base query selection.
        """

    def __new__(
        self,
        query_path: Optional[Union[List[str], str]] = None,
        filter_field: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        sort_key: Optional[str] = None,
    ) -> str:
        if not query_path:
            raise ValueError("The `query_path` is not defined.")
        else:
            # define filter query string
            filter_query = f"{filter_field}:>='{start}' AND {filter_field}:<='{end}'" if filter_field else None
            return self.resolve_query(self, query_path, filter_query, sort_key)


class Metafields(ShopifyBulkQuery):

    record_identifier = "Metafield"
    edge_name = "metafields"

    # list of available fields:
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
        query_path: Optional[Union[List[str], str]] = None,
        filter_query: Optional[str] = None,
        sort_key: Optional[str] = None,
    ) -> str:
        """
        Defines how query object should be constructed and resolved based on the root query selection.
        Only 2 lvl nesting is available: https://shopify.dev/docs/api/usage/bulk-operations/queries#operation-restrictions
        Output example to BULK query `customers.metafields` with `filter query` by `updated_at` sorted `ASC`:
            {
                customers(
                    query: "updated_at:>='2023-04-13' AND updated_at:<='2023-12-01'"
                    sortKey: UPDATED_AT
                ) {
                    edges {
                        node {
                            id
                            metafields {
                                edges {
                                    node {
                                        id
                                        namespace
                                        value
                                        key
                                        description
                                        createdAt
                                        updatedAt
                                        type
                                    }
                                }
                            }
                        }
                    }
                }
            }
        """
        # resolve query path if the List[str] is provided
        if isinstance(query_path, list):
            if len(query_path) > 3:
                raise Exception(f"The `query_path` length should be limited to 3 elements, actual: {query_path}.")
            else:
                if len(query_path) == 1:
                    # resolve query path for single list element
                    query = self.builder.build_query(
                        query_path[0], self.builder.get_edge_node(self.edge_name, self.edge_nodes), filter_query, sort_key
                    )
                elif len(query_path) == 2:
                    # resolve query path for 2 list elements
                    # first is `root`, second is it's entity
                    edges = self.builder.get_edge_node(query_path[1], ["id", self.builder.get_edge_node(self.edge_name, self.edge_nodes)])
                    query = self.builder.build_query(query_path[0], edges, filter_query, sort_key)
                elif len(query_path) == 3:
                    # resolve query path for 3 list elements (max)
                    # first is `root`, second and third are it's entities
                    edges = self.builder.get_edge_node(
                        query_path[1],
                        [
                            "id",
                            self.builder.get_edge_node(query_path[2], ["id", self.builder.get_edge_node(self.edge_name, self.edge_nodes)]),
                        ],
                    )
                    query = self.builder.build_query(query_path[0], edges, filter_query, sort_key)
        # resolve quey path if `str` is provided for the single entity, basically the query `root`
        elif isinstance(query_path, str):
            query = self.builder.build_query(
                query_path, self.builder.get_edge_node(self.edge_name, self.edge_nodes), filter_query, sort_key
            )
        # return the constructed query operation
        return Operation(type="", queries=[query]).render()
