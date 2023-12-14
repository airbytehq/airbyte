#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import abstractmethod
from string import Template
from typing import Any, List, Mapping, Optional, Union

from graphql_query import Argument, Field, InlineFragment, Operation, Query

from .tools import BULK_PARENT_KEY, BulkTools


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

    def get_edge_inline_frargment(self, name: str, fields: Union[List[InlineFragment], InlineFragment]) -> Field:
        """
        Defines the edge of the graph and it's fields to select for Shopify BULK Operaion.
        https://shopify.dev/docs/api/usage/bulk-operations/queries#the-jsonl-data-format
        """
        return Field(name=name, fields=fields)

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
            Field(name=self.edge_key, fields=[Field(name=self.node_key, fields=["id"] + edges if edges else ["id"])]),
        ]
        # return constucted query
        return Query(name=name, arguments=args, fields=fields)


class ShopifyBulkQuery:
    def __new__(
        cls,
        query_path: Optional[Union[List[str], str]],
        filter_field: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        sort_key: Optional[str] = None,
    ) -> str:

        # builder instance
        cls.builder: GraphQlQueryBuilder = GraphQlQueryBuilder()
        cls.tools: BulkTools = BulkTools()

        if not query_path:
            raise ValueError("The `query_path` is not defined.")
        else:
            # define filter query string, if passed
            filter_query = f"{filter_field}:>='{start}' AND {filter_field}:<='{end}'" if filter_field else None
            # building query
            cls.built_query: Query = cls.query(query_path, filter_query, sort_key)
            # resolving
            cls.operation: str = cls.resolve_query(cls.built_query)
            # returning objec class
            return object.__new__(cls)

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
    def edge_name(self) -> str:
        """
        Defines the root graph node name to fetch from.
        https://shopify.dev/docs/api/admin-graphql
        """

    @property
    @classmethod
    def edge_nodes(cls) -> Optional[Union[List[Field], List[str]]]:
        """
        Defines the fields for final graph selection.
        https://shopify.dev/docs/api/admin-graphql
        """

    @property
    @classmethod
    def edge_inline_fragments(cls) -> Optional[Union[List[InlineFragment], InlineFragment]]:
        """
        Defines the inline frragments for final graph selection.
        https://shopify.dev/docs/api/admin-graphql
        """
        ...

    @classmethod
    def query(
        cls,
        query_path: Optional[Union[List[str], str]] = None,
        filter_query: Optional[str] = None,
        sort_key: Optional[str] = None,
    ) -> Query:
        """
        Output example to BULK query `<query_path>` with `filter query`:
            {
                <query_path>(query: "<filter_query>") {
                    edges {
                        node {
                            id
                        }
                    }
                }
            }
        """
        # return the constructed query operation
        return cls.builder.build_query(query_path, cls.edge_nodes, filter_query, sort_key)

    @classmethod
    def resolve_query(cls, query: Query) -> str:
        """
        Default query resolver from type(Operation) > type(str).
        """
        # return the constructed query operation
        return Operation(type="", queries=[query]).render()


class Metafield(ShopifyBulkQuery):

    record_identifier = "Metafield"
    edge_name = "metafields"

    # list of available fields:
    # https://shopify.dev/docs/api/admin-graphql/unstable/objects/Metafield
    edge_nodes: List[Field] = [
        Field(name="id"),
        Field(name="namespace"),
        Field(name="value"),
        Field(name="key"),
        Field(name="description"),
        Field(name="createdAt"),
        Field(name="updatedAt"),
        Field(name="type"),
    ]

    @classmethod
    def query(
        cls,
        query_path: Optional[Union[List[str], str]] = None,
        filter_query: Optional[str] = None,
        sort_key: Optional[str] = None,
    ) -> Query:
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
                    query = cls.builder.build_query(
                        query_path[0], [cls.builder.get_edge_node(cls.edge_name, cls.edge_nodes)], filter_query, sort_key
                    )
                elif len(query_path) == 2:
                    # resolve query path for 2 list elements
                    # first is `root`, second is it's entity
                    edges = cls.builder.get_edge_node(query_path[1], ["id", cls.builder.get_edge_node(cls.edge_name, cls.edge_nodes)])
                    query = cls.builder.build_query(query_path[0], [edges], filter_query, sort_key)
                elif len(query_path) == 3:
                    # resolve query path for 3 list elements (max)
                    # first is `root`, second and third are it's entities
                    edges = cls.builder.get_edge_node(
                        query_path[1],
                        [
                            "id",
                            cls.builder.get_edge_node(query_path[2], ["id", cls.builder.get_edge_node(cls.edge_name, cls.edge_nodes)]),
                        ],
                    )
                    query = cls.builder.build_query(query_path[0], [edges], filter_query, sort_key)
        # resolve quey path if `str` is provided for the single entity, basically the query `root`
        elif isinstance(query_path, str):
            query = cls.builder.build_query(query_path, [cls.builder.get_edge_node(cls.edge_name, cls.edge_nodes)], filter_query, sort_key)
        # return the constructed query operation
        return query


class DiscountCode(ShopifyBulkQuery):

    record_identifier = None
    edge_name = "codeDiscount"

    edge_nodes: List[Field] = [
        Field(name="discountClass", alias="discountType"),
        Field(
            name="codes",
            fields=[
                Field(
                    name="edges",
                    fields=[
                        Field(
                            name="node",
                            fields=[
                                Field(name="asyncUsageCount", alias="usageCount"),
                                Field(name="code"),
                                Field(name="id"),
                            ],
                        )
                    ],
                )
            ],
        ),
    ]

    @classmethod
    def edge_inline_fragments(cls) -> Optional[Union[List[InlineFragment], InlineFragment]]:
        mandatory_fields = ["updatedAt", "createdAt"]
        return [
            # the type: DiscountCodeApp has no `"summary"` field available
            InlineFragment(type="DiscountCodeApp", fields=[*mandatory_fields, *cls.edge_nodes]),
            InlineFragment(type="DiscountCodeBasic", fields=[*mandatory_fields, "summary", *cls.edge_nodes]),
            InlineFragment(type="DiscountCodeBxgy", fields=[*mandatory_fields, "summary", *cls.edge_nodes]),
            InlineFragment(type="DiscountCodeFreeShipping", fields=[*mandatory_fields, "summary", *cls.edge_nodes]),
        ]

    @classmethod
    def query(
        cls,
        query_path: Optional[Union[List[str], str]] = None,
        filter_query: Optional[str] = None,
        sort_key: Optional[str] = None,
    ) -> Query:
        """
        Output example to BULK query `codeDiscountNodes` with `filter query` by `updated_at` sorted `ASC`:
            {
                codeDiscountNodes(query: "updated_at:>='2023-12-07T00:00:00Z' AND updated_at:<='2023-12-30T00:00:00Z'", sortKey: UPDATED_AT) {
                    edges {
                        node {
                            id
                            codeDiscount {
                                ... on DiscountCodeApp {
                                    updatedAt
                                    createdAt
                                    discountType: discountClass
                                    codes {
                                        edges {
                                            node {
                                                usageCount: asyncUsageCount
                                                code
                                                id
                                            }
                                        }
                                    }
                                }
                                ... on DiscountCodeBasic {
                                    createdAt
                                    updatedAt
                                    discountType: discountClass
                                    summary
                                    codes {
                                        edges {
                                            node {
                                                usageCount: asyncUsageCount
                                                code
                                                id
                                            }
                                        }
                                    }
                                }
                                ... on DiscountCodeBxgy {
                                    updatedAt
                                    createdAt
                                    discountType: discountClass
                                    summary
                                    codes {
                                        edges {
                                            node {
                                                usageCount: asyncUsageCount
                                                code
                                                id
                                            }
                                        }
                                    }
                                }
                                ... on DiscountCodeFreeShipping {
                                    updatedAt
                                    createdAt
                                    discountType: discountClass
                                    summary
                                    codes {
                                        edges {
                                            node {
                                                usageCount: asyncUsageCount
                                                code
                                                id
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        """

        edges = cls.builder.get_edge_inline_frargment(cls.edge_name, cls.edge_inline_fragments())
        # return the constructed query operation
        return cls.builder.build_query(query_path, [edges], filter_query, sort_key)


class Collection(ShopifyBulkQuery):

    record_identifier = None

    edge_nodes: List[Field] = [
        Field(name="handle"),
        Field(name="title"),
        Field(name="updatedAt"),
        Field(name="descriptionHtml", alias="bodyHtml"),
        Field(
            name="publications",
            fields=[Field(name="edges", fields=[Field(name="node", fields=[Field(name="publishDate", alias="publishedAt")])])],
        ),
        Field(name="sortOrder"),
        Field(name="templateSuffix"),
        Field(name="productsCount"),
    ]


class InventoryItem(ShopifyBulkQuery):

    record_identifier = None

    edge_nodes: List[Field] = [
        Field(name="unitCost", fields=[Field(name="amount", alias="cost")]),
        Field(name="countryCodeOfOrigin"),
        Field(
            name="countryHarmonizedSystemCodes",
            fields=[Field(name="edges", fields=[Field(name="node", fields=["harmonizedSystemCode", "countryCode"])])],
        ),
        Field(name="harmonizedSystemCode"),
        Field(name="provinceCodeOfOrigin"),
        Field(name="updatedAt"),
        Field(name="createdAt"),
        Field(name="sku"),
        Field(name="tracked"),
        Field(name="requiresShipping"),
    ]


class InventoryLevel(ShopifyBulkQuery):

    record_identifier = "InventoryLevel"

    edge_nodes: List[Field] = [
        Field(name="available"),
        Field(name="item", fields=[Field(name="id", alias="inventory_item_id")]),
        Field(name="updatedAt"),
    ]

    @classmethod
    def query(
        cls,
        query_path: Optional[Union[List[str], str]] = None,
        filter_query: Optional[str] = None,
        sort_key: Optional[str] = None,
    ) -> Query:
        """
        Output example to BULK query `inventory_levels` from `locations` with `filter query` by `updated_at`:
            {
                locations {
                    edges {
                        node {
                            id
                            inventoryLevels(query: "updated_at:>='2023-04-14T00:00:00+00:00'") {
                                edges {
                                    node {
                                        id
                                        available
                                        item {
                                            inventory_item_id: id
                                        }
                                        updatedAt
                                    }
                                }
                            }
                        }
                    }
                }
            }
        """
        # resolve query path if the List[str] is provided
        # build the nested query first with `filter_query` to have the incremental syncs
        edges = cls.builder.build_query(query_path[1], [*cls.edge_nodes], filter_query, sort_key)
        # build the main query around previous
        query = cls.builder.build_query(query_path[0], [edges], sort_key)
        # return the constructed query operation
        return query


class FulfillmentOrder(ShopifyBulkQuery):
    """
    Output example to BULK query `fulfillmentOrders` from `orders` with `filter query` by `updated_at`, sorted by `UPDATED_AT`:
        {
            orders(query: "updated_at:>='2023-04-13T05:00:09Z' and updated_at:<='2023-04-15T05:00:09Z'", sortKey: UPDATED_AT){
                edges {
                    node {
                        __typename
                        id
                        fulfillmentOrders {
                            edges {
                                node {
                                    __typename
                                    id
                                    assignedLocation {
                                        location {
                                            locationId: id
                                        }
                                        address1
                                        address2
                                        city
                                        countryCode
                                        name
                                        phone
                                        province
                                        zip
                                    }
                                    destination {
                                        id
                                        address1
                                        address2
                                        city
                                        company
                                        countryCode
                                        email
                                        firstName
                                        lastName
                                        phone
                                        province
                                        zip
                                    }
                                    deliveryMethod {
                                        id
                                        methodType
                                    }
                                    fulfillAt
                                    fulfillBy
                                    internationalDuties {
                                        incoterm
                                    }
                                    fulfillmentHolds {
                                        reason
                                        reasonNotes
                                    }
                                    lineItems {
                                        edges {
                                            node {
                                                __typename
                                                id
                                                inventoryItemId
                                                lineItem {
                                                    lineItemId: id
                                                    fulfillableQuantity
                                                    quantity: currentQuantity
                                                    variant {
                                                        variantId: id
                                                    }
                                                }
                                            }
                                        }
                                    }
                                    createdAt
                                    updatedAt
                                    requestStatus
                                    status
                                    supportedActions {
                                        action
                                        externalUrl
                                    }
                                    merchantRequests {
                                        edges {
                                            node {
                                                __typename
                                                id
                                                message
                                                kind
                                                requestOptions
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    """

    record_identifier = None

    edge_nodes: List[Field] = [
        "__typename",
        Field(
            name="fulfillmentOrders",
            fields=[
                Field(
                    name="edges",
                    fields=[
                        Field(
                            name="node",
                            fields=[
                                "__typename",
                                "id",
                                Field(
                                    name="assignedLocation",
                                    fields=[
                                        "address1",
                                        "address2",
                                        "city",
                                        "countryCode",
                                        "name",
                                        "phone",
                                        "province",
                                        "zip",
                                        Field(
                                            name="location",
                                            fields=[
                                                Field(name="id", alias="locationId"),
                                            ],
                                        ),
                                    ],
                                ),
                                Field(
                                    name="destination",
                                    fields=[
                                        "id",
                                        "address1",
                                        "address2",
                                        "city",
                                        "company",
                                        "countryCode",
                                        "email",
                                        "firstName",
                                        "lastName",
                                        "phone",
                                        "province",
                                        "zip",
                                    ],
                                ),
                                Field(
                                    name="deliveryMethod",
                                    fields=[
                                        "id",
                                        "methodType",
                                        "minDeliveryDateTime",
                                        "maxDeliveryDateTime",
                                    ],
                                ),
                                "fulfillAt",
                                "fulfillBy",
                                Field(
                                    name="internationalDuties",
                                    fields=[
                                        "incoterm",
                                    ],
                                ),
                                Field(
                                    name="fulfillmentHolds",
                                    fields=[
                                        "reason",
                                        "reasonNotes",
                                    ],
                                ),
                                Field(
                                    name="lineItems",
                                    fields=[
                                        Field(
                                            name="edges",
                                            fields=[
                                                Field(
                                                    name="node",
                                                    fields=[
                                                        "__typename",
                                                        "id",
                                                        "inventoryItemId",
                                                        Field(
                                                            name="lineItem",
                                                            fields=[
                                                                Field(name="id", alias="lineItemId"),
                                                                "fulfillableQuantity",
                                                                Field(name="currentQuantity", alias="quantity"),
                                                                Field(name="variant", fields=[Field(name="id", alias="variantId")]),
                                                            ],
                                                        ),
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                ),
                                "createdAt",
                                "updatedAt",
                                "requestStatus",
                                "status",
                                Field(
                                    name="supportedActions",
                                    fields=[
                                        "action",
                                        "externalUrl",
                                    ],
                                ),
                                Field(
                                    name="merchantRequests",
                                    fields=[
                                        Field(
                                            name="edges",
                                            fields=[
                                                Field(
                                                    name="node",
                                                    fields=[
                                                        "__typename",
                                                        "id",
                                                        "message",
                                                        "kind",
                                                        "requestOptions",
                                                    ],
                                                )
                                            ],
                                        )
                                    ],
                                ),
                            ],
                        )
                    ],
                )
            ],
        ),
    ]

    @classmethod
    def prep_fulfillment_order(cls, record: Mapping[str, Any], shop_id: Optional[int] = 0) -> Mapping[str, Any]:
        # addings
        record["shop_id"] = shop_id
        record["order_id"] = record.get(BULK_PARENT_KEY)
        # unnest nested locationId to the `assignedLocation`
        location_id = record.get("assignedLocation", {}).get("location", {}).get("locationId")
        record["assignedLocation"]["locationId"] = location_id
        record["assignedLocationId"] = location_id
        # create nested placeholders for other parts
        record["line_items"] = []
        record["merchant_requests"] = []
        # cleaning
        record.pop("__typename")
        record.pop(BULK_PARENT_KEY)
        record.get("assignedLocation").pop("location", None)
        # resolve ids from `str` to `int`
        # location id
        location = record.get("assignedLocation", {})
        if location:
            location_id = location.get("locationId")
            if location_id:
                record["assignedLocation"]["locationId"] = cls.tools.resolve_str_id(location_id)
        # assigned_location_id
        record["assignedLocationId"] = cls.tools.resolve_str_id(record.get("assignedLocationId"))
        # destination id
        destination = record.get("destination", {})
        if destination:
            destination_id = destination.get("id")
            if destination_id:
                record["destination"]["id"] = cls.tools.resolve_str_id(destination_id)
        # delivery method id
        delivery_method = record.get("deliveryMethod", {})
        if delivery_method:
            delivery_method_id = delivery_method.get("id")
            if delivery_method_id:
                record["deliveryMethod"]["id"] = cls.tools.resolve_str_id(delivery_method_id)
        # order id
        record["order_id"] = cls.tools.resolve_str_id(record.get("order_id"))
        # field names to snake for nested objects
        # `assignedLocation`(object) field names to snake case
        record["assignedLocation"] = cls.tools.fields_names_to_snake_case(record.get("assignedLocation"))
        # `deliveryMethod`(object) field names to snake case
        record["deliveryMethod"] = cls.tools.fields_names_to_snake_case(record.get("deliveryMethod"))
        # `destination`(object) field names to snake case
        record["destination"] = cls.tools.fields_names_to_snake_case(record.get("destination"))
        # `fulfillmentHolds`(list[object]) field names to snake case
        record["fulfillmentHolds"] = [cls.tools.fields_names_to_snake_case(el) for el in record.get("fulfillmentHolds", [])]
        # `supportedActions`(list[object]) field names to snake case
        record["supportedActions"] = [cls.tools.fields_names_to_snake_case(el) for el in record.get("supportedActions", [])]
        return record

    @classmethod
    def prep_line_item(cls, record: Mapping[str, Any], shop_id: Optional[int] = 0) -> Mapping[str, Any]:
        # addings
        record["shop_id"] = shop_id
        record["fulfillmentOrderId"] = record.get(BULK_PARENT_KEY)
        # unnesting nested `lineItem`
        line_item = record.get("lineItem", {})
        if line_item:
            record["quantity"] = line_item.get("quantity")
            record["lineItemId"] = line_item.get("lineItemId")
            record["fulfillableQuantity"] = line_item.get("fulfillableQuantity")
            variant = line_item.get("variant", {})
            if variant:
                record["variantId"] = variant.get("variantId")
        # cleaning
        record.pop("__typename")
        record.pop(BULK_PARENT_KEY)
        record.pop("lineItem")
        # resolve ids from `str` to `int`
        record["id"] = cls.tools.resolve_str_id(record.get("id"))
        # inventoryItemId
        record["inventoryItemId"] = cls.tools.resolve_str_id(record.get("inventoryItemId"))
        # fulfillmentOrderId
        record["fulfillmentOrderId"] = cls.tools.resolve_str_id(record.get("fulfillmentOrderId"))
        # lineItemId
        record["lineItemId"] = cls.tools.resolve_str_id(record.get("lineItemId"))
        # variantId
        record["variantId"] = cls.tools.resolve_str_id(record.get("variantId"))
        # field names to snake case
        record = cls.tools.fields_names_to_snake_case(record)
        return record

    @classmethod
    def prep_merchant_request(cls, record: Mapping[str, Any]) -> Mapping[str, Any]:
        # cleaning
        record.pop("__typename")
        record.pop(BULK_PARENT_KEY)
        # resolve ids from `str` to `int`
        record["id"] = cls.tools.resolve_str_id(record.get("id"))
        # field names to snake case
        record = cls.tools.fields_names_to_snake_case(record)
        return record
