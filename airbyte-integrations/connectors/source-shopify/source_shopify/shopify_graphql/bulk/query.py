#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from string import Template
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

from attr import dataclass
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
                            createdAt
                            objectCount
                            fileSize
                            url
                            partialDataUrl
                        }
                    }
                }"""
        ).substitute(job_id=bulk_job_id)

    @staticmethod
    def cancel(bulk_job_id: str) -> str:
        return Template(
            """mutation {
                bulkOperationCancel(id: "$job_id") {
                    bulkOperation {
                        id
                        status
                        createdAt
                    }
                    userErrors {
                        field
                        message
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
                        createdAt
                    }
                    userErrors {
                        field
                        message
                    }
                }
            }'''
        )
        return bulk_template.substitute(query=query)


@dataclass
class ShopifyBulkQuery:
    shop_id: int

    @property
    def tools(self) -> BulkTools:
        return BulkTools()

    @property
    @abstractmethod
    def query_name(self) -> str:
        """
        Defines the root graph node name to fetch from: https://shopify.dev/docs/api/admin-graphql
        """

    @property
    def record_composition(self) -> Optional[Mapping[str, Any]]:
        """
        Example:
            {
                "new_record": "Collection", // the GQL Typename of the parent entity
                "record_components": [
                    "CollectionPublication" // each `collection` has List `publications`
                ],
            }
        """
        return {}

    @property
    def sort_key(self) -> Optional[str]:
        """
        The field name by which the records are ASC sorted, if defined.
        """
        return None

    @property
    def query_nodes(self) -> Optional[Union[List[Field], List[str]]]:
        """
        Defines the fields for final graph selection.
        https://shopify.dev/docs/api/admin-graphql
        """
        return ["__typename", "id"]

    def get(self, filter_field: Optional[str] = None, start: Optional[str] = None, end: Optional[str] = None) -> str:
        # define filter query string, if passed
        filter_query = f"{filter_field}:>='{start}' AND {filter_field}:<='{end}'" if filter_field else None
        # building query
        query: Query = self.query(filter_query)
        # resolving
        return self.resolve(query)

    def query(self, filter_query: Optional[str] = None) -> Query:
        """
        Overide this method, if you need to customize query build logic.
        Output example to BULK query `<query_name>` with `filter query`:
            {
                <query_name>(query: "<filter_query>") {
                    edges {
                        node {
                            id
                        }
                    }
                }
            }
        """
        # return the constructed query operation
        return self.build(self.query_name, self.query_nodes, filter_query)

    def build(
        self,
        name: str,
        edges: Optional[Union[List[Field], List[InlineFragment], Field, InlineFragment]] = None,
        filter_query: Optional[str] = None,
        additional_query_args: Optional[Mapping[str, Any]] = None,
    ) -> Query:
        """
        Defines the root of the graph with edges.
        """
        query_args: List[Argument] = []
        # constructing arguments
        if filter_query:
            query_args.append(Argument(name="query", value=f'"{filter_query}"'))
        if self.sort_key:
            query_args.append(Argument(name="sortKey", value=self.sort_key))
        if additional_query_args:
            for k, v in additional_query_args.items():
                query_args.append(Argument(name=k, value=v))
        # constructing edges
        query_fields = [
            Field(name="edges", fields=[Field(name="node", fields=edges if edges else ["id"])]),
        ]
        # return constucted query
        return Query(name=name, arguments=query_args, fields=query_fields)

    def resolve(self, query: Query) -> str:
        """
        Default query resolver from type(Operation) > type(str).
        Overide this method to build multiple queries in one, if needed.
        """
        # return the constructed query operation
        return Operation(type="", queries=[query]).render()

    def record_process_components(self, record: MutableMapping[str, Any]) -> Iterable[MutableMapping[str, Any]]:
        """
        Defines how to process collected components, default `as is`.
        """
        yield record


class MetafieldType(Enum):
    CUSTOMERS = "customers"
    ORDERS = "orders"
    DRAFT_ORDERS = "draftOrders"
    PRODUCTS = "products"
    PRODUCT_IMAGES = ["products", "images"]
    PRODUCT_VARIANTS = "productVariants"
    COLLECTIONS = "collections"
    LOCATIONS = "locations"


class Metafield(ShopifyBulkQuery):
    """
    Only 2 lvl nesting is available: https://shopify.dev/docs/api/usage/bulk-operations/queries#operation-restrictions
    Output example to BULK query `customers.metafields` with `filter query` by `updated_at` sorted `ASC`:
    {
        <Type>(
            query: "updated_at:>='2023-04-13' AND updated_at:<='2023-12-01'"
            sortKey: UPDATED_AT
        ) {
            edges {
                node {
                    __typename
                    id
                    metafields {
                        edges {
                            node {
                                __typename
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

    sort_key = "UPDATED_AT"
    record_composition = {"new_record": "Metafield"}

    metafield_fields: List[Field] = [
        "__typename",
        "id",
        "namespace",
        "value",
        "key",
        "description",
        "createdAt",
        "updatedAt",
        "type",
    ]

    @property
    def query_name(self) -> str:
        if isinstance(self.type.value, list):
            return self.type.value[0]
        elif isinstance(self.type.value, str):
            return self.type.value

    @property
    @abstractmethod
    def type(self) -> MetafieldType:
        """
        Defines the Metafield type to fetch, see `MetafieldType` for more info.
        """

    def get_edge_node(self, name: str, fields: Union[List[str], List[Field], str]) -> Field:
        """
        Defines the edge of the graph and it's fields to select for Shopify BULK Operaion.
        https://shopify.dev/docs/api/usage/bulk-operations/queries#the-jsonl-data-format
        """
        return Field(name=name, fields=[Field(name="edges", fields=[Field(name="node", fields=fields)])])

    @property
    def query_nodes(self) -> List[Field]:
        """
        List of available fields:
        https://shopify.dev/docs/api/admin-graphql/unstable/objects/Metafield
        """
        # define metafield node
        metafield_node = self.get_edge_node("metafields", self.metafield_fields)

        if isinstance(self.type.value, list):
            return ["__typename", "id", self.get_edge_node(self.type.value[1], ["__typename", "id", metafield_node])]
        elif isinstance(self.type.value, str):
            return ["__typename", "id", metafield_node]

    def record_process_components(self, record: MutableMapping[str, Any]) -> Iterable[MutableMapping[str, Any]]:
        # resolve parent id from `str` to `int`
        record["owner_id"] = self.tools.resolve_str_id(record.get(BULK_PARENT_KEY))
        # add `owner_resource` field
        record["owner_resource"] = self.tools.camel_to_snake(record.get(BULK_PARENT_KEY, "").split("/")[3])
        # remove `__parentId` from record
        record.pop(BULK_PARENT_KEY, None)
        # convert dates from ISO-8601 to RFC-3339
        record["createdAt"] = self.tools.from_iso8601_to_rfc3339(record, "createdAt")
        record["updatedAt"] = self.tools.from_iso8601_to_rfc3339(record, "updatedAt")
        record = self.tools.fields_names_to_snake_case(record)
        yield record


class MetafieldCollection(Metafield):
    """
    {
        collections(query: "updated_at:>='2023-02-07T00:00:00+00:00' AND updated_at:<='2023-12-04T00:00:00+00:00'", sortKey: UPDATED_AT) {
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

    type = MetafieldType.COLLECTIONS


class MetafieldCustomer(Metafield):
    """
    {
        customers(query: "updated_at:>='2023-02-07T00:00:00+00:00' AND updated_at:<='2023-12-04T00:00:00+00:00'", sortKey: UPDATED_AT) {
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

    type = MetafieldType.CUSTOMERS


class MetafieldLocation(Metafield):
    """
    {
        locations {
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

    sort_key = None
    type = MetafieldType.LOCATIONS


class MetafieldOrder(Metafield):
    """
    {
        orders(query: "updated_at:>='2023-02-07T00:00:00+00:00' AND updated_at:<='2023-12-04T00:00:00+00:00'", sortKey: UPDATED_AT) {
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

    type = MetafieldType.ORDERS


class MetafieldDraftOrder(Metafield):
    """
    {
        draftOrders(query: "updated_at:>='2023-02-07T00:00:00+00:00' AND updated_at:<='2023-12-04T00:00:00+00:00'", sortKey: UPDATED_AT) {
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

    type = MetafieldType.DRAFT_ORDERS


class MetafieldProduct(Metafield):
    """
    {
        products(query: "updated_at:>='2023-02-07T00:00:00+00:00' AND updated_at:<='2023-12-04T00:00:00+00:00'", sortKey: UPDATED_AT) {
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

    type = MetafieldType.PRODUCTS


class MetafieldProductImage(Metafield):
    """
    {
        products(query: "updated_at:>='2023-02-07T00:00:00+00:00' AND updated_at:<='2023-12-04T00:00:00+00:00'", sortKey: UPDATED_AT) {
            edges {
                node {
                    id
                    images{
                        edges{
                            node{
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
            }
        }
    }
    """

    type = MetafieldType.PRODUCT_IMAGES


class MetafieldProductVariant(Metafield):
    """
    {
        productVariants(query: "updated_at:>='2023-02-07T00:00:00+00:00' AND updated_at:<='2023-12-04T00:00:00+00:00'") {
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

    sort_key = None
    type = MetafieldType.PRODUCT_VARIANTS


class DiscountCode(ShopifyBulkQuery):
    """
    Output example to BULK query `codeDiscountNodes` with `filter query` by `updated_at` sorted `ASC`:
        {
            codeDiscountNodes(query: "updated_at:>='2023-12-07T00:00:00Z' AND updated_at:<='2023-12-30T00:00:00Z'", sortKey: UPDATED_AT) {
                edges {
                    node {
                        __typename
                        id
                        codeDiscount {
                            ... on DiscountCodeApp {
                                updatedAt
                                createdAt
                                discountType: discountClass
                                codes {
                                    edges {
                                        node {
                                            __typename
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
                                            __typename
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
                                            __typename
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
                                            __typename
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

    query_name = "codeDiscountNodes"
    sort_key = "UPDATED_AT"

    code_discount_fields: List[Field] = [
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
                                "__typename",
                                Field(name="asyncUsageCount", alias="usageCount"),
                                "code",
                                "id",
                            ],
                        )
                    ],
                )
            ],
        ),
    ]

    code_discount_fragments: List[InlineFragment] = [
        # the type: DiscountCodeApp has no `"summary"` field available
        InlineFragment(type="DiscountCodeApp", fields=["updatedAt", "createdAt", *code_discount_fields]),
        InlineFragment(type="DiscountCodeBasic", fields=["updatedAt", "createdAt", "summary", *code_discount_fields]),
        InlineFragment(type="DiscountCodeBxgy", fields=["updatedAt", "createdAt", "summary", *code_discount_fields]),
        InlineFragment(type="DiscountCodeFreeShipping", fields=["updatedAt", "createdAt", "summary", *code_discount_fields]),
    ]

    query_nodes: List[Field] = [
        "__typename",
        "id",
        Field(name="codeDiscount", fields=code_discount_fragments),
    ]

    record_composition = {
        "new_record": "DiscountCodeNode",
        # each DiscountCodeNode has `DiscountRedeemCode`
        "record_components": ["DiscountRedeemCode"],
    }

    def record_process_components(self, record: MutableMapping[str, Any]) -> Optional[Iterable[MutableMapping[str, Any]]]:
        """
        Defines how to process collected components.
        """

        record_components = record.get("record_components", {})
        if record_components:
            discounts = record_components.get("DiscountRedeemCode", [])
            if len(discounts) > 0:
                for discount in discounts:
                    # resolve parent id from `str` to `int`
                    discount["admin_graphql_api_id"] = discount.get("id")
                    discount["price_rule_id"] = self.tools.resolve_str_id(discount.get(BULK_PARENT_KEY))
                    discount["id"] = self.tools.resolve_str_id(discount.get("id"))
                    code_discount = record.get("codeDiscount", {})
                    if code_discount:
                        discount.update(**code_discount)
                        discount.pop(BULK_PARENT_KEY, None)
                        # field names to snake case for discount
                        discount = self.tools.fields_names_to_snake_case(discount)
                        # convert dates from ISO-8601 to RFC-3339
                        discount["created_at"] = self.tools.from_iso8601_to_rfc3339(discount, "created_at")
                        discount["updated_at"] = self.tools.from_iso8601_to_rfc3339(discount, "updated_at")
                    yield discount


class Collection(ShopifyBulkQuery):
    """
    {
        collections(query: "updated_at:>='2023-02-07T00:00:00+00:00' AND updated_at:<='2023-12-04T00:00:00+00:00'", sortKey: UPDATED_AT) {
            edges {
                node {
                    __typename
                    id
                    handle
                    title
                    updatedAt
                    bodyHtml: descriptionHtml
                    publications {
                        edges {
                            node {
                                __typename
                                publishedAt: publishDate
                            }
                        }
                    }
                    sortOrder
                    templateSuffix
                    productsCount
                }
            }
        }
    }
    """

    query_name = "collections"
    sort_key = "UPDATED_AT"

    publications_fields: List[Field] = [
        Field(name="edges", fields=[Field(name="node", fields=["__typename", Field(name="publishDate", alias="publishedAt")])])
    ]

    query_nodes: List[Field] = [
        "__typename",
        "id",
        Field(name="handle"),
        Field(name="title"),
        Field(name="updatedAt"),
        Field(name="descriptionHtml", alias="bodyHtml"),
        Field(name="publications", fields=publications_fields),
        Field(name="sortOrder"),
        Field(name="templateSuffix"),
        Field(name="productsCount", fields=[Field(name="count", alias="products_count")]),
    ]

    record_composition = {
        "new_record": "Collection",
        # each collection has `publications`
        "record_components": ["CollectionPublication"],
    }

    def record_process_components(self, record: MutableMapping[str, Any]) -> Iterable[MutableMapping[str, Any]]:
        """
        Defines how to process collected components.
        """
        record_components = record.get("record_components", {})
        if record_components:
            publications = record_components.get("CollectionPublication", [])
            if len(publications) > 0:
                record["published_at"] = publications[0].get("publishedAt")
                record.pop("record_components")
        # convert dates from ISO-8601 to RFC-3339
        record["published_at"] = self.tools.from_iso8601_to_rfc3339(record, "published_at")
        record["updatedAt"] = self.tools.from_iso8601_to_rfc3339(record, "updatedAt")
        # unnest `product_count` to the root lvl
        record["products_count"] = record.get("productsCount", {}).get("products_count")
        # remove leftovers
        record.pop(BULK_PARENT_KEY, None)
        yield record


class CustomerAddresses(ShopifyBulkQuery):
    """
    {
        customers(query: "updated_at:>='2024-01-20T00:00:00+00:00' AND updated_at:<'2024-01-24T00:00:00+00:00'", sortKey:UPDATED_AT) {
            edges {
                node {
                    __typename
                    customerId: id
                    defaultAddress {
                        id
                    }
                    addresses {
                        address1
                        address2
                        city
                        country
                        countryCode
                        company
                        firstName
                        id
                        lastName
                        name
                        phone
                        province
                        provinceCode
                        zip
                    }
                }
            }
        }
    }
    """

    query_name = "customers"
    sort_key = "UPDATED_AT"

    addresses_fields: List[str] = [
        "address1",
        "address2",
        "city",
        "country",
        "countryCode",
        "company",
        "firstName",
        "id",
        "lastName",
        "name",
        "phone",
        "province",
        "provinceCode",
        "zip",
    ]
    query_nodes: List[Field] = [
        "__typename",
        "id",
        Field(name="defaultAddress", fields=["id"]),
        Field(name="addresses", fields=addresses_fields),
        # add `Customer.updated_at` field to provide the parent state
        "updatedAt",
    ]

    record_composition = {
        "new_record": "Customer",
    }

    def set_default_address(
        self, record: MutableMapping[str, Any], address_record: MutableMapping[str, Any]
    ) -> Iterable[MutableMapping[str, Any]]:
        default_address = record.get("defaultAddress", {})
        # the default_address could be literal `None`, additional check is required
        if default_address:
            if address_record.get("id") == record.get("defaultAddress", {}).get("id"):
                address_record["default"] = True
        return address_record

    def record_process_components(self, record: MutableMapping[str, Any]) -> Optional[Iterable[MutableMapping[str, Any]]]:
        """
        Defines how to process collected components.
        """
        if "addresses" in record.keys():
            addresses = record.get("addresses")
            if len(addresses) > 0:
                for customer_address in addresses:
                    # add `customer_id` to each address entry
                    customer_address["customer_id"] = record.get("id")
                    # add `country_name` from `country`
                    customer_address["country_name"] = customer_address.get("country")
                    # default address check
                    customer_address = self.set_default_address(record, customer_address)
                    # resolve address id
                    customer_address["id"] = self.tools.resolve_str_id(customer_address.get("id"))
                    # add PARENT stream cursor_field to the root level of the record
                    # providing the ability to track the PARENT state as well
                    # convert dates from ISO-8601 to RFC-3339
                    customer_address["updated_at"] = self.tools.from_iso8601_to_rfc3339(record, "updatedAt")
                    # names to snake
                    customer_address = self.tools.fields_names_to_snake_case(customer_address)
                    yield customer_address


class CustomerJourney(ShopifyBulkQuery):
    """
    Output example to BULK query `customer_journey_summary` from `orders` with `filter query` by `updated_at` sorted `ASC`:
        {
            orders(query: "updated_at:>='2020-01-20T00:00:00+00:00' AND updated_at:<'2024-04-25T00:00:00+00:00'", sortKey:UPDATED_AT) {
                edges {
                    node {
                        __typename
                        order_id: id
                        createdAt
                        updatedAt
                        customerJourneySummary {
                            ready
                            momentsCount {
                                count
                                precision
                            }
                            customerOrderIndex
                            daysToConversion
                            firstVisit {
                                id
                                landingPage
                                landingPageHtml
                                occurredAt
                                referralCode
                                referrerUrl
                                source
                                sourceType
                                sourceDescription
                                utmParameters {
                                    campaign
                                    content
                                    medium
                                    source
                                    term
                                }
                            }
                            lastVisit {
                                id
                                landingPage
                                landingPageHtml
                                occurredAt
                                referralCode
                                referrerUrl
                                source
                                sourceType
                                sourceDescription
                                utmParameters {
                                    campaign
                                    content
                                    medium
                                    source
                                    term
                                }
                            }
                        }
                    }
                }
            }
        }
    """

    query_name = "orders"
    sort_key = "UPDATED_AT"

    visit_fields: List[Field] = [
        "id",
        "landingPage",
        "landingPageHtml",
        "occurredAt",
        "referralCode",
        "referrerUrl",
        "source",
        "sourceType",
        "sourceDescription",
        Field(name="utmParameters", fields=["campaign", "content", "medium", "source", "term"]),
    ]
    customer_journey_summary_fields: List[Field] = [
        "ready",
        Field(name="momentsCount", fields=["count", "precision"]),
        "customerOrderIndex",
        "daysToConversion",
        Field(name="firstVisit", fields=visit_fields),
        Field(name="lastVisit", fields=visit_fields),
    ]

    query_nodes: List[Field] = [
        "__typename",
        Field(name="id", alias="order_id"),
        "createdAt",
        "updatedAt",
        Field(name="customerJourneySummary", fields=customer_journey_summary_fields),
    ]

    record_composition = {
        "new_record": "Order",
    }

    def process_visit(
        self,
        visit_data: Mapping[str, Any],
    ) -> MutableMapping[str, Any]:
        # save the id before it's resolved
        visit_data["admin_graphql_api_id"] = visit_data.get("id")
        # resolve the order_id to str
        visit_data["id"] = self.tools.resolve_str_id(visit_data.get("id"))
        # convert dates from ISO-8601 to RFC-3339
        visit_data["occurredAt"] = self.tools.from_iso8601_to_rfc3339(visit_data, "occurredAt")
        # cast field names to snake_case
        visit_data = self.tools.fields_names_to_snake_case(visit_data)
        return visit_data

    def process_customer_journey(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        customer_journey_summary = record.get("customerJourneySummary", {})
        if customer_journey_summary:
            # process first, last visit data
            first_visit = customer_journey_summary.get("firstVisit", {})
            last_visit = customer_journey_summary.get("lastVisit", {})
            customer_journey_summary["firstVisit"] = self.process_visit(first_visit) if first_visit else {}
            customer_journey_summary["lastVisit"] = self.process_visit(last_visit) if last_visit else {}
        # cast field names to snake_case
        customer_journey_summary = self.tools.fields_names_to_snake_case(customer_journey_summary)
        return customer_journey_summary

    def record_process_components(self, record: MutableMapping[str, Any]) -> Optional[Iterable[MutableMapping[str, Any]]]:
        """
        Defines how to process collected components.
        """

        # save the id before it's resolved
        record["admin_graphql_api_id"] = record.get("order_id")
        # resolve the order_id to str
        record["order_id"] = self.tools.resolve_str_id(record.get("order_id"))
        # convert dates from ISO-8601 to RFC-3339
        record["createdAt"] = self.tools.from_iso8601_to_rfc3339(record, "createdAt")
        record["updatedAt"] = self.tools.from_iso8601_to_rfc3339(record, "updatedAt")
        # process customerJourneySummary property
        record["customerJourneySummary"] = self.process_customer_journey(record)
        # cast field names to snake_case
        record = self.tools.fields_names_to_snake_case(record)
        yield record


class InventoryItem(ShopifyBulkQuery):
    """
    {
        inventoryItems(query: "updated_at:>='2022-04-13T00:00:00+00:00' AND updated_at:<='2023-02-07T00:00:00+00:00'") {
            edges {
                node {
                    __typename
                    unitCost {
                        cost: amount
                    }
                    countryCodeOfOrigin
                    countryHarmonizedSystemCodes {
                        edges {
                            node {
                                harmonizedSystemCode
                                countryCode
                            }
                        }
                    }
                    harmonizedSystemCode
                    provinceCodeOfOrigin
                    updatedAt
                    createdAt
                    sku
                    tracked
                    requiresShipping
                }
            }
        }
    }
    """

    query_name = "inventoryItems"

    country_harmonizedS_system_codes: List[Field] = [
        Field(name="edges", fields=[Field(name="node", fields=["__typename", "harmonizedSystemCode", "countryCode"])])
    ]

    query_nodes: List[Field] = [
        "__typename",
        "id",
        Field(name="unitCost", fields=[Field(name="amount", alias="cost")]),
        Field(name="countryCodeOfOrigin"),
        Field(name="countryHarmonizedSystemCodes", fields=country_harmonizedS_system_codes),
        Field(name="harmonizedSystemCode"),
        Field(name="provinceCodeOfOrigin"),
        Field(name="updatedAt"),
        Field(name="createdAt"),
        Field(name="sku"),
        Field(name="tracked"),
        Field(name="requiresShipping"),
    ]

    record_composition = {
        "new_record": "InventoryItem",
    }

    def record_process_components(self, record: MutableMapping[str, Any]) -> Iterable[MutableMapping[str, Any]]:
        """
        Defines how to process collected components.
        """

        # resolve `cost` to root lvl as `number`
        unit_cost = record.get("unitCost", {})
        if unit_cost:
            record["cost"] = float(unit_cost.get("cost"))
        else:
            record["cost"] = None
        # clean up
        record.pop("unitCost", None)
        # add empty `country_harmonized_system_codes` array, if missing for record
        if "countryHarmonizedSystemCodes" not in record.keys():
            record["country_harmonized_system_codes"] = []
        # convert dates from ISO-8601 to RFC-3339
        record["createdAt"] = self.tools.from_iso8601_to_rfc3339(record, "createdAt")
        record["updatedAt"] = self.tools.from_iso8601_to_rfc3339(record, "updatedAt")
        record = self.tools.fields_names_to_snake_case(record)
        yield record


class InventoryLevel(ShopifyBulkQuery):
    """
    Output example to BULK query `inventory_levels` from `locations` with `filter query` by `updated_at`:
        {
            locations(includeLegacy: true, includeInactive: true) {
                edges {
                    node {
                        __typename
                        id
                        inventoryLevels(query: "updated_at:>='2023-04-14T00:00:00+00:00'") {
                            edges {
                                node {
                                    __typename
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

    query_name = "locations"
    # in order to return all the locations, additional query args must be provided
    # https://shopify.dev/docs/api/admin-graphql/2023-10/queries/locations#query-arguments
    locations_query_args = {
        "includeLegacy": "true",
        "includeInactive": "true",
    }
    record_composition = {
        "new_record": "InventoryLevel",
    }

    # quantity related fields and filtering options
    quantities_names_filter: List[str] = [
        '"available"',
        '"incoming"',
        '"committed"',
        '"damaged"',
        '"on_hand"',
        '"quality_control"',
        '"reserved"',
        '"safety_stock"',
    ]
    # quantities fields
    quantities_fields: List[str] = [
        "id",
        "name",
        "quantity",
        "updatedAt",
    ]

    inventory_levels_fields: List[Field] = [
        "__typename",
        "id",
        Field(name="item", fields=[Field(name="id", alias="inventory_item_id")]),
        Field(name="updatedAt"),
    ]

    def _quantities_query(self) -> Query:
        """
        Defines the `quantities` nested query.
        """

        return Query(
            name="quantities",
            arguments=[Argument(name="names", value=self.quantities_names_filter)],
            fields=self.quantities_fields,
        )

    def _process_quantities(self, quantities: Iterable[MutableMapping[str, Any]] = None) -> Iterable[Mapping[str, Any]]:
        if quantities:
            for quantity in quantities:
                # save the original string id
                quantity["admin_graphql_api_id"] = quantity.get("id")
                # resolve the int id from str id
                quantity["id"] = self.tools.resolve_str_id(quantity.get("id"))
                # convert dates from ISO-8601 to RFC-3339
                quantity["updatedAt"] = self.tools.from_iso8601_to_rfc3339(quantity, "updatedAt")
            return quantities
        return []

    def query(self, filter_query: Optional[str] = None) -> Query:
        # construct the `quantities` query piece
        quantities: List[Query] = [self._quantities_query()]
        # build the nested query first with `filter_query` to have the incremental syncs
        inventory_levels: List[Query] = [self.build("inventoryLevels", self.inventory_levels_fields + quantities, filter_query)]
        # build the main query around previous
        # return the constructed query operation
        return self.build(
            name=self.query_name,
            edges=self.query_nodes + inventory_levels,
            # passing more query args for `locations` query
            additional_query_args=self.locations_query_args,
        )

    def record_process_components(self, record: MutableMapping[str, Any]) -> Iterable[MutableMapping[str, Any]]:
        """
        Defines how to process collected components.
        """
        # process quantities
        quantities = record.get("quantities", [])
        record["quantities"] = self._process_quantities(quantities)
        # resolve `inventory_item_id` to root lvl +  resolve to int
        record["inventory_item_id"] = self.tools.resolve_str_id(record.get("item", {}).get("inventory_item_id"))
        # add `location_id` from `__parentId`
        record["location_id"] = self.tools.resolve_str_id(record[BULK_PARENT_KEY])
        # make composite `id` from `location_id|inventory_item_id`
        record["id"] = "|".join((str(record.get("location_id", "")), str(record.get("inventory_item_id", ""))))
        # convert dates from ISO-8601 to RFC-3339
        record["updatedAt"] = self.tools.from_iso8601_to_rfc3339(record, "updatedAt")
        # remove leftovers
        record.pop("item", None)
        record.pop(BULK_PARENT_KEY, None)
        record = self.tools.fields_names_to_snake_case(record)
        yield record


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
                                        minDeliveryDateTime
                                        maxDeliveryDateTime
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

    query_name = "orders"
    sort_key = "UPDATED_AT"

    assigned_location_fields: List[Field] = [
        "address1",
        "address2",
        "city",
        "countryCode",
        "name",
        "phone",
        "province",
        "zip",
        Field(name="location", fields=[Field(name="id", alias="locationId")]),
    ]

    destination_fields: List[Field] = [
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
    ]

    delivery_method_fields: List[Field] = [
        "id",
        "methodType",
        "minDeliveryDateTime",
        "maxDeliveryDateTime",
    ]

    line_items_fields: List[Field] = [
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
    ]

    merchant_requests_fields: List[Field] = [
        "__typename",
        "id",
        "message",
        "kind",
        "requestOptions",
    ]

    fulfillment_order_fields: List[Field] = [
        "__typename",
        "id",
        Field(name="assignedLocation", fields=assigned_location_fields),
        Field(name="destination", fields=destination_fields),
        Field(name="deliveryMethod", fields=delivery_method_fields),
        "fulfillAt",
        "fulfillBy",
        Field(name="internationalDuties", fields=["incoterm"]),
        Field(name="fulfillmentHolds", fields=["reason", "reasonNotes"]),
        Field(name="lineItems", fields=[Field(name="edges", fields=[Field(name="node", fields=line_items_fields)])]),
        "createdAt",
        "updatedAt",
        "requestStatus",
        "status",
        Field(name="supportedActions", fields=["action", "externalUrl"]),
        Field(name="merchantRequests", fields=[Field(name="edges", fields=[Field(name="node", fields=merchant_requests_fields)])]),
    ]

    query_nodes: List[Field] = [
        "__typename",
        "id",
        Field(name="fulfillmentOrders", fields=[Field(name="edges", fields=[Field(name="node", fields=fulfillment_order_fields)])]),
    ]

    record_composition = {
        "new_record": "FulfillmentOrder",
        # each FulfillmentOrder has multiple `FulfillmentOrderLineItem` and `FulfillmentOrderMerchantRequest`
        "record_components": [
            "FulfillmentOrderLineItem",
            "FulfillmentOrderMerchantRequest",
        ],
    }

    def process_fulfillment_order(self, record: MutableMapping[str, Any], shop_id: int) -> MutableMapping[str, Any]:
        # addings
        record["shop_id"] = shop_id
        record["order_id"] = record.get(BULK_PARENT_KEY)
        # unnest nested locationId to the `assignedLocation`
        location_id = record.get("assignedLocation", {}).get("location", {}).get("locationId")
        record["assignedLocation"]["locationId"] = location_id
        record["assigned_location_id"] = location_id
        # create nested placeholders for other parts
        record["line_items"] = []
        record["merchant_requests"] = []
        # cleaning
        record.pop(BULK_PARENT_KEY)
        record.get("assignedLocation").pop("location", None)
        # resolve ids from `str` to `int`
        # location id
        location = record.get("assignedLocation", {})
        if location:
            location_id = location.get("locationId")
            if location_id:
                record["assignedLocation"]["locationId"] = self.tools.resolve_str_id(location_id)
        # assigned_location_id
        record["assigned_location_id"] = self.tools.resolve_str_id(record.get("assigned_location_id"))
        # destination id
        destination = record.get("destination", {})
        if destination:
            destination_id = destination.get("id")
            if destination_id:
                record["destination"]["id"] = self.tools.resolve_str_id(destination_id)
        # delivery method id
        delivery_method = record.get("deliveryMethod", {})
        if delivery_method:
            delivery_method_id = delivery_method.get("id")
            if delivery_method_id:
                record["deliveryMethod"]["id"] = self.tools.resolve_str_id(delivery_method_id)
        # order id
        record["order_id"] = self.tools.resolve_str_id(record.get("order_id"))
        # field names to snake for nested objects
        # `assignedLocation`(object) field names to snake case
        record["assignedLocation"] = self.tools.fields_names_to_snake_case(record.get("assignedLocation"))
        # `deliveryMethod`(object) field names to snake case
        record["deliveryMethod"] = self.tools.fields_names_to_snake_case(record.get("deliveryMethod"))
        # `destination`(object) field names to snake case
        record["destination"] = self.tools.fields_names_to_snake_case(record.get("destination"))
        # `fulfillmentHolds`(list[object]) field names to snake case
        record["fulfillment_holds"] = [self.tools.fields_names_to_snake_case(el) for el in record.get("fulfillment_holds", [])]
        # `supportedActions`(list[object]) field names to snake case
        record["supported_actions"] = [self.tools.fields_names_to_snake_case(el) for el in record.get("supported_actions", [])]
        return record

    def process_line_item(self, record: MutableMapping[str, Any], shop_id: int) -> MutableMapping[str, Any]:
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
        record.pop(BULK_PARENT_KEY)
        record.pop("lineItem")
        # resolve ids from `str` to `int`
        record["id"] = self.tools.resolve_str_id(record.get("id"))
        # inventoryItemId
        record["inventoryItemId"] = self.tools.resolve_str_id(record.get("inventoryItemId"))
        # fulfillmentOrderId
        record["fulfillmentOrderId"] = self.tools.resolve_str_id(record.get("fulfillmentOrderId"))
        # lineItemId
        record["lineItemId"] = self.tools.resolve_str_id(record.get("lineItemId"))
        # variantId
        record["variantId"] = self.tools.resolve_str_id(record.get("variantId"))
        # field names to snake case
        record = self.tools.fields_names_to_snake_case(record)
        return record

    def process_merchant_request(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        # cleaning
        record.pop(BULK_PARENT_KEY)
        # resolve ids from `str` to `int`
        record["id"] = self.tools.resolve_str_id(record.get("id"))
        # field names to snake case
        record = self.tools.fields_names_to_snake_case(record)
        return record

    def record_process_components(self, record: MutableMapping[str, Any]) -> Iterable[MutableMapping[str, Any]]:
        """
        Defines how to process collected components.
        """

        record = self.process_fulfillment_order(record, self.shop_id)
        record_components = record.get("record_components", {})
        if record_components:
            line_items = record_components.get("FulfillmentOrderLineItem", [])
            if len(line_items) > 0:
                for line_item in line_items:
                    record["line_items"].append(self.process_line_item(line_item, self.shop_id))
            merchant_requests = record_components.get("FulfillmentOrderMerchantRequest", [])
            if len(merchant_requests) > 0:
                for merchant_request in merchant_requests:
                    record["merchant_requests"].append(self.process_merchant_request(merchant_request))
            record.pop("record_components")
        # convert dates from ISO-8601 to RFC-3339
        record["updatedAt"] = self.tools.from_iso8601_to_rfc3339(record, "updatedAt")
        # convert dates from ISO-8601 to RFC-3339
        record["fulfillAt"] = self.tools.from_iso8601_to_rfc3339(record, "fulfillAt")
        record["createdAt"] = self.tools.from_iso8601_to_rfc3339(record, "createdAt")
        record["updatedAt"] = self.tools.from_iso8601_to_rfc3339(record, "updatedAt")
        # delivery method
        delivery_method = record.get("deliveryMethod", {})
        if delivery_method:
            record["deliveryMethod"]["min_delivery_date_time"] = self.tools.from_iso8601_to_rfc3339(
                delivery_method, "min_delivery_date_time"
            )
            record["deliveryMethod"]["max_delivery_date_time"] = self.tools.from_iso8601_to_rfc3339(
                delivery_method, "max_delivery_date_time"
            )
        yield record


class Transaction(ShopifyBulkQuery):
    """
    Output example to BULK query `transactions` from `orders` with `filter query` by `updated_at` sorted `ASC`:
        {
            orders(query: "updated_at:>='2021-05-23T00:00:00+00:00' AND updated_at:<'2021-12-22T00:00:00+00:00'", sortKey:UPDATED_AT) {
                edges {
                    node {
                        __typename
                        id
                        currency: currencyCode
                        transactions {
                            id
                            errorCode
                            parentTransaction {
                                parentId: id
                            }
                            test
                            kind
                            amount
                            receipt: receiptJson
                            gateway
                            authorization: authorizationCode
                            createdAt
                            status
                            processedAt
                            totalUnsettledSet {
                                presentmentMoney {
                                    amount
                                    currency: currencyCode
                                }
                                shopMoney {
                                    amount
                                    currency: currencyCode
                                }
                            }
                            paymentId
                            paymentDetails {
                                ... on CardPaymentDetails {
                                        avsResultCode
                                        creditCardBin: bin
                                        creditCardCompany: company
                                        creditCardNumber: number
                                        creditCardName: name
                                        cvvResultCode
                                        creditCardWallet: wallet
                                        creditCardExpirationYear: expirationYear
                                        creditCardExpirationMonth: expirationMonth
                                }
                            }
                        }
                    }
                }
            }
        }
    """

    query_name = "orders"
    sort_key = "UPDATED_AT"

    total_unsettled_set_fields: List[Field] = [
        Field(name="presentmentMoney", fields=["amount", Field(name="currencyCode", alias="currency")]),
        Field(name="shopMoney", fields=["amount", Field(name="currencyCode", alias="currency")]),
    ]

    payment_details: List[InlineFragment] = [
        InlineFragment(
            type="CardPaymentDetails",
            fields=[
                "avsResultCode",
                "cvvResultCode",
                Field(name="bin", alias="creditCardBin"),
                Field(name="company", alias="creditCardCompany"),
                Field(name="number", alias="creditCardNumber"),
                Field(name="name", alias="creditCardName"),
                Field(name="wallet", alias="creditCardWallet"),
                Field(name="expirationYear", alias="creditCardExpirationYear"),
                Field(name="expirationMonth", alias="creditCardExpirationMonth"),
            ],
        )
    ]

    query_nodes: List[Field] = [
        "__typename",
        "id",
        Field(name="currencyCode", alias="currency"),
        Field(
            name="transactions",
            fields=[
                "id",
                "errorCode",
                Field(name="parentTransaction", fields=[Field(name="id", alias="parentId")]),
                "test",
                "kind",
                "amount",
                Field(name="receiptJson", alias="receipt"),
                "gateway",
                Field(name="authorizationCode", alias="authorization"),
                "createdAt",
                "status",
                "processedAt",
                Field(name="totalUnsettledSet", fields=total_unsettled_set_fields),
                "paymentId",
                Field(name="paymentDetails", fields=payment_details),
            ],
        ),
    ]

    record_composition = {
        "new_record": "Order",
    }

    def process_transaction(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        # save the id before it's resolved
        record["admin_graphql_api_id"] = record.get("id")
        # unnest nested fields
        parent_transaction = record.get("parentTransaction", {})
        if parent_transaction:
            record["parent_id"] = parent_transaction.get("parentId")
        # str values to float
        record["amount"] = float(record.get("amount"))
        # convert dates from ISO-8601 to RFC-3339
        record["processedAt"] = self.tools.from_iso8601_to_rfc3339(record, "processedAt")
        record["createdAt"] = self.tools.from_iso8601_to_rfc3339(record, "createdAt")
        # resolve ids
        record["id"] = self.tools.resolve_str_id(record.get("id"))
        record["parent_id"] = self.tools.resolve_str_id(record.get("parent_id"))
        # remove leftovers
        record.pop("parentTransaction", None)
        # field names to snake case
        total_unsettled_set = record.get("totalUnsettledSet", {})
        if total_unsettled_set:
            record["totalUnsettledSet"] = self.tools.fields_names_to_snake_case(total_unsettled_set)
            # nested str values to float
            record["totalUnsettledSet"]["presentment_money"]["amount"] = float(
                total_unsettled_set.get("presentmentMoney", {}).get("amount")
            )
            record["totalUnsettledSet"]["shop_money"]["amount"] = float(total_unsettled_set.get("shopMoney", {}).get("amount"))
        payment_details = record.get("paymentDetails", {})
        if payment_details:
            record["paymentDetails"] = self.tools.fields_names_to_snake_case(payment_details)
        # field names to snake case for root level
        record = self.tools.fields_names_to_snake_case(record)
        return record

    def record_process_components(self, record: MutableMapping[str, Any]) -> Optional[Iterable[MutableMapping[str, Any]]]:
        """
        Defines how to process collected components.
        """

        if "transactions" in record.keys():
            transactions = record.get("transactions")
            if len(transactions) > 0:
                for transaction in transactions:
                    # populate parent record keys
                    transaction["order_id"] = record.get("id")
                    transaction["currency"] = record.get("currency")
                    yield self.process_transaction(transaction)


class Product(ShopifyBulkQuery):
    """
    {
        products(query: "updated_at:>='2020-01-20T00:00:00+00:00' AND updated_at:<'2024-04-25T00:00:00+00:00'", sortKey:UPDATED_AT) {
            edges {
                node {
                    __typename
                    id
                    publishedAt
                    createdAt
                    status
                    vendor
                    updatedAt
                    bodyHtml
                    productType
                    tags
                    options {
                        __typename
                        id
                        values
                        position
                    }
                    handle
                    images {
                        edges {
                            node {
                                __typename
                                id
                            }
                        }

                    }
                    templateSuffix
                    title
                    variants {
                        edges {
                            node {
                                __typename
                                id
                            }
                        }
                    }
                    description
                    descriptionHtml
                    isGiftCard
                    legacyResourceId
                    media_count: mediaCount {
                        media_count: count
                    }
                    onlineStorePreviewUrl
                    onlineStoreUrl
                    totalInventory
                    tracksInventory
                    total_variants: variantsCount {
                        total_variants: count
                    }
                }
            }
        }
    }
    """

    query_name = "products"
    sort_key = "UPDATED_AT"
    # images property fields
    images_fields: List[Field] = [Field(name="edges", fields=[Field(name="node", fields=["__typename", "id"])])]
    # variants property fields, we re-use the same field names as for the `images` property
    variants_fields: List[Field] = images_fields
    # main query
    query_nodes: List[Field] = [
        "__typename",
        "id",
        "publishedAt",
        "createdAt",
        "status",
        "vendor",
        "updatedAt",
        "bodyHtml",
        "productType",
        "tags",
        "handle",
        "templateSuffix",
        "title",
        "description",
        "descriptionHtml",
        "isGiftCard",
        "legacyResourceId",
        "onlineStorePreviewUrl",
        "onlineStoreUrl",
        "totalInventory",
        "tracksInventory",
        Field(name="variantsCount", alias="total_variants", fields=[Field(name="count", alias="total_variants")]),
        Field(name="mediaCount", alias="media_count", fields=[Field(name="count", alias="media_count")]),
        Field(name="options", fields=["id", "name", "values", "position"]),
        Field(name="images", fields=images_fields),
        Field(name="variants", fields=variants_fields),
    ]

    record_composition = {
        "new_record": "Product",
        # each product could have `Image` and `ProductVariant` associated with the product
        "record_components": ["Image", "ProductVariant"],
    }

    def _process_component(self, entity: List[dict]) -> List[dict]:
        for item in entity:
            # remove the `__parentId` from the object
            if BULK_PARENT_KEY in item:
                item.pop(BULK_PARENT_KEY)
            # resolve the id from string
            item["id"] = self.tools.resolve_str_id(item.get("id"))
        return entity

    def _process_options(self, options: List[dict], product_id: Optional[int] = None) -> List[dict]:
        for option in options:
            # add product_id to each option
            option["product_id"] = product_id if product_id else None
        return options

    def _unnest_tags(self, record: MutableMapping[str, Any]) -> Optional[str]:
        # we keep supporting 1 tag only, as it was for the REST stream,
        # to avoid breaking change.
        tags = record.get("tags", [])
        return ", ".join(tags) if tags else None

    def record_process_components(self, record: MutableMapping[str, Any]) -> Iterable[MutableMapping[str, Any]]:
        """
        Defines how to process collected components.
        """
        # get the joined record components collected for the record
        record_components = record.get("record_components", {})

        # process record components
        if record_components:
            record["images"] = self._process_component(record_components.get("Image", []))
            record["variants"] = self._process_component(record_components.get("ProductVariant", []))
            record["options"] = self._process_component(record.get("options", []))
            # add the product_id to the `options`
            product_id = record.get("id")
            record["options"] = self._process_options(record.get("options", []), product_id)
            record.pop("record_components")
        # unnest the `tags` (the list of 1)
        record["tags"] = self._unnest_tags(record)
        # unnest `total_variants`
        record["total_variants"] = record.get("total_variants", {}).get("total_variants")
        # unnest `media_count`
        record["media_count"] = record.get("media_count", {}).get("media_count")
        # convert dates from ISO-8601 to RFC-3339
        record["published_at"] = self.tools.from_iso8601_to_rfc3339(record, "publishedAt")
        record["updatedAt"] = self.tools.from_iso8601_to_rfc3339(record, "updatedAt")
        record["createdAt"] = self.tools.from_iso8601_to_rfc3339(record, "createdAt")

        yield record


class ProductImage(ShopifyBulkQuery):
    """
    {
        products(
            query: "updated_at:>='2019-04-13T00:00:00+00:00' AND updated_at:<='2024-04-30T12:16:17.273363+00:00'"
            sortKey: UPDATED_AT
        ) {
            edges {
                node {
                    __typename
                    id
                    # THE MEDIA NODE IS NEEDED TO PROVIDE THE CURSORS
                    media {
                        edges {
                            node {
                            ... on MediaImage {
                                    __typename
                                    createdAt
                                    updatedAt
                                    image {
                                        url
                                    }
                                }
                            }
                        }
                    }
                    # THIS IS THE MAIN NODE WE WANT TO GET
                    images {
                        edges {
                            node {
                                __typename
                                id
                                height
                                alt: altText
                                src
                                url
                                width
                            }
                        }
                    }
                }
            }
        }
    }
    """

    query_name = "products"
    sort_key = "UPDATED_AT"

    # images property fields
    images_fields: List[Field] = [
        Field(
            name="edges",
            fields=[
                Field(
                    name="node",
                    fields=[
                        "__typename",
                        "id",
                        "height",
                        Field(name="altText", alias="alt"),
                        "src",
                        "url",
                        "width",
                    ],
                )
            ],
        )
    ]

    # media fragment, contains the info about when the Image was created or updated.
    media_fragment: List[InlineFragment] = [
        InlineFragment(
            type="MediaImage",
            fields=[
                "__typename",
                "createdAt",
                "updatedAt",
                # fetch the `url` as the key for the later join
                Field(name="image", fields=["url"]),
            ],
        ),
    ]

    # media property fields
    media_fields: List[Field] = [Field(name="edges", fields=[Field(name="node", fields=media_fragment)])]

    # main query
    query_nodes: List[Field] = [
        "__typename",
        "id",
        Field(name="media", fields=media_fields),
        Field(name="images", fields=images_fields),
    ]

    record_composition = {
        "new_record": "Product",
        # each product could have `MediaImage` associated with the product,
        # each product could have `Image` assiciated with the product and the related `MediaImage`,
        # there could be multiple `MediaImage` and `Image` assigned to the product.
        "record_components": ["MediaImage", "Image"],
    }

    def _process_component(self, entity: List[dict]) -> List[dict]:
        for item in entity:
            # remove the `__parentId` from the object
            if BULK_PARENT_KEY in item:
                item.pop(BULK_PARENT_KEY)
            # resolve the id from string
            item["admin_graphql_api_id"] = item.get("id")
            item["id"] = self.tools.resolve_str_id(item.get("id"))
        return entity

    def _add_product_id(self, options: List[dict], product_id: Optional[int] = None) -> List[dict]:
        for option in options:
            # add product_id to each option
            option["product_id"] = product_id if product_id else None
        return options

    def _merge_with_media(self, record_components: List[dict]) -> Optional[Iterable[MutableMapping[str, Any]]]:
        media = record_components.get("MediaImage", [])
        images = record_components.get("Image", [])

        # Create a dictionary to map the 'url' key in images
        url_map = {item["url"]: item for item in images}

        # Merge images with data from media when 'image.url' matches 'url'
        for item in media:
            # remove the `__parentId` from Media
            if BULK_PARENT_KEY in item:
                item.pop(BULK_PARENT_KEY)

            image_url = item.get("image", {}).get("url")
            if image_url in url_map:
                # Merge images into media
                item.update(url_map.get(image_url))
                # remove lefovers
                item.pop("image", None)
                item.pop("url", None)
                # make the `alt` None, if it's an empty str, since server sends the "" instead of Null
                alt = item.get("alt")
                item["alt"] = None if not alt else alt

        # return merged list of images
        return media

    def _convert_datetime_to_rfc3339(self, images: List[dict]) -> MutableMapping[str, Any]:
        for image in images:
            image["createdAt"] = self.tools.from_iso8601_to_rfc3339(image, "createdAt")
            image["updatedAt"] = self.tools.from_iso8601_to_rfc3339(image, "updatedAt")
        return images

    def record_process_components(self, record: MutableMapping[str, Any]) -> Iterable[MutableMapping[str, Any]]:
        """
        Defines how to process collected components.
        """
        # get the joined record components collected for the record
        record_components = record.get("record_components", {})

        # process record components
        if record_components:
            record["images"] = self._process_component(record_components.get("Image", []))
            # add the product_id to each `Image`
            record["images"] = self._add_product_id(record.get("images", []), record.get("id"))
            record["images"] = self._merge_with_media(record_components)
            record.pop("record_components")
            # produce images records
            if len(record.get("images", [])) > 0:
                # convert dates from ISO-8601 to RFC-3339
                record["images"] = self._convert_datetime_to_rfc3339(record.get("images", []))
                yield from record.get("images", [])


class ProductVariant(ShopifyBulkQuery):
    """
    {
        productVariants(
            query: "updated_at:>='2019-04-13T00:00:00+00:00' AND updated_at:<='2024-04-30T12:16:17.273363+00:00'"
            sortKey: UPDATED_AT
        ) {
            edges {
                node {
                    __typename
                    id
                    product {
                        product_id: id
                    }
                    title
                    price
                    sku
                    position
                    inventoryPolicy
                    compareAtPrice
                    fulfillmentService {
                        fulfillment_service: handle
                    }
                    inventoryManagement
                    createdAt
                    updatedAt
                    taxable
                    barcode
                    grams: weight
                    weight
                    weightUnit
                    inventoryItem {
                        inventory_item_id: id
                    }
                    inventoryQuantity
                    old_inventory_quantity: inventoryQuantity
                    presentmentPrices {
                        edges {
                            node {
                                __typename
                                price {
                                    amount
                                    currencyCode
                                }
                                compareAtPrice {
                                    amount
                                    currencyCode
                                }
                            }
                        }
                    }
                    requiresShipping
                    image {
                        image_id: id
                    }
                }
            }
        }
    }
    """

    query_name = "productVariants"
    sort_key = "ID"

    prices_fields: List[str] = ["amount", "currencyCode"]
    presentment_prices_fields: List[Field] = [
        Field(
            name="edges",
            fields=[
                Field(
                    name="node",
                    fields=["__typename", Field(name="price", fields=prices_fields), Field(name="compareAtPrice", fields=prices_fields)],
                )
            ],
        )
    ]

    # main query
    query_nodes: List[Field] = [
        "__typename",
        "id",
        "title",
        "price",
        "sku",
        "position",
        "inventoryPolicy",
        "compareAtPrice",
        "inventoryManagement",
        "createdAt",
        "updatedAt",
        "taxable",
        "barcode",
        "weight",
        "weightUnit",
        "inventoryQuantity",
        "requiresShipping",
        Field(name="weight", alias="grams"),
        Field(name="image", fields=[Field(name="id", alias="image_id")]),
        Field(name="inventoryQuantity", alias="old_inventory_quantity"),
        Field(name="product", fields=[Field(name="id", alias="product_id")]),
        Field(name="fulfillmentService", fields=[Field(name="handle", alias="fulfillment_service")]),
        Field(name="inventoryItem", fields=[Field(name="id", alias="inventory_item_id")]),
        Field(name="presentmentPrices", fields=presentment_prices_fields),
    ]

    record_composition = {
        "new_record": "ProductVariant",
        # each `ProductVariant` could have `ProductVariantPricePair` associated with the product variant.
        "record_components": ["ProductVariantPricePair"],
    }

    def _process_presentment_prices(self, entity: List[dict]) -> List[dict]:
        for item in entity:
            # remove the `__parentId` from the object
            if BULK_PARENT_KEY in item:
                item.pop(BULK_PARENT_KEY)

            # these objects could be literally `Null/None` from the response,
            # this is treated like a real value, so we need to assigne the correct values instead
            price: Optional[Mapping[str, Any]] = item.get("price", {})
            if not price:
                price = {}
            # get the amount values
            price_amount = price.get("amount") if price else None
            # make the nested object's values up to the schema, (cast the `str` > `float`)
            item["price"]["amount"] = float(price_amount) if price_amount else None
            # convert field names to snake case
            item["price"] = self.tools.fields_names_to_snake_case(item.get("price"))

            compare_at_price: Optional[Mapping[str, Any]] = item.get("compareAtPrice", {})
            if not compare_at_price:
                compare_at_price = {}
                # assign the correct value, if there is no object from response
                item["compareAtPrice"] = compare_at_price
            compare_at_price_amount = compare_at_price.get("amount") if compare_at_price else None
            item["compareAtPrice"]["amount"] = float(compare_at_price_amount) if compare_at_price_amount else None
            item["compare_at_price"] = self.tools.fields_names_to_snake_case(item["compareAtPrice"])
            # remove leftovers
            item.pop("compareAtPrice", None)

        return entity

    def _unnest_and_resolve_id(self, record: MutableMapping[str, Any], from_property: str, id_field: str) -> int:
        entity = record.get(from_property, {})
        return self.tools.resolve_str_id(entity.get(id_field)) if entity else None

    def record_process_components(self, record: MutableMapping[str, Any]) -> Iterable[MutableMapping[str, Any]]:
        """
        Defines how to process collected components.
        """

        # get the joined record components collected for the record
        record_components = record.get("record_components", {})
        # process record components
        if record_components:
            record["presentment_prices"] = self._process_presentment_prices(record_components.get("ProductVariantPricePair", []))
            record.pop("record_components")

        # unnest mandatory fields from their placeholders
        record["product_id"] = self._unnest_and_resolve_id(record, "product", "product_id")
        record["inventory_item_id"] = self._unnest_and_resolve_id(record, "inventoryItem", "inventory_item_id")
        record["image_id"] = self._unnest_and_resolve_id(record, "image", "image_id")
        # unnest `fulfillment_service` from `fulfillmentService`
        record["fulfillment_service"] = record.get("fulfillmentService", {}).get("fulfillment_service")
        # cast the `price` to number, could be literally `None`
        price = record.get("price")
        record["price"] = float(price) if price else None
        # cast the `grams` to integer
        record["grams"] = int(record.get("grams", 0))
        # convert date-time cursors
        record["createdAt"] = self.tools.from_iso8601_to_rfc3339(record, "createdAt")
        record["updatedAt"] = self.tools.from_iso8601_to_rfc3339(record, "updatedAt")
        # clean up the leftovers
        record.pop("image", None)
        record.pop("product", None)
        record.pop("inventoryItem", None)

        yield record


class OrderRisk(ShopifyBulkQuery):
    """
    {
        orders(query: "updated_at:>='2021-04-13T00:00:00+00:00' AND updated_at:<='2024-05-20T13:50:06.882235+00:00'" sortKey: UPDATED_AT) {
            edges {
                node {
                    __typename
                    updatedAt
                    order_id: id
                    risk {
                        recommendation
                        assessments {
                            risk_level: riskLevel
                            facts {
                                description
                                sentiment
                            }
                            provider {
                                features
                                description
                                handle
                                embedded
                                title
                                published
                                developer_name: developerName
                                developer_type: developerType
                                app_store_app_url: appStoreAppUrl
                                install_url: installUrl
                                app_store_developer_url: appStoreDeveloperUrl
                                is_post_purchase_app_in_use: isPostPurchaseAppInUse
                                previously_installed: previouslyInstalled
                                pricing_details_summary: pricingDetailsSummary
                                pricing_details: pricingDetails
                                privacy_policy_url: privacyPolicyUrl
                                public_category: publicCategory
                                uninstall_message: uninstallMessage
                                webhook_api_version: webhookApiVersion
                                shopify_developed: shopifyDeveloped
                                provider_id: id
                                failed_requirements: failedRequirements {
                                    message
                                    action {
                                        title
                                        url
                                        action_id: id
                                    }
                                }
                                feedback {
                                    link {
                                        label
                                        url
                                    }
                                    messages {
                                        field
                                        message
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

    query_name = "orders"
    sort_key = "UPDATED_AT"

    action_fields: List[Field] = [
        "title",
        "url",
        Field(name="id", alias="action_id"),
    ]

    failed_reqirements_fields: List[Field] = ["message", Field(name="action", fields=action_fields)]

    feedback_fields: List[Field] = [
        Field(name="link", fields=["label", "url"]),
        Field(name="messages", fields=["field", "message"]),
    ]

    provider_fields: List[Field] = [
        "features",
        "description",
        "handle",
        "embedded",
        "title",
        "published",
        Field(name="developerName", alias="developer_name"),
        Field(name="developerType", alias="developer_type"),
        Field(name="appStoreAppUrl", alias="app_store_app_url"),
        Field(name="installUrl", alias="install_url"),
        Field(name="appStoreDeveloperUrl", alias="app_store_developer_url"),
        Field(name="isPostPurchaseAppInUse", alias="is_post_purchase_app_in_use"),
        Field(name="previouslyInstalled", alias="previously_installed"),
        Field(name="pricingDetailsSummary", alias="pricing_details_summary"),
        Field(name="pricingDetails", alias="pricing_details"),
        Field(name="privacyPolicyUrl", alias="privacy_policy_url"),
        Field(name="publicCategory", alias="public_category"),
        Field(name="uninstallMessage", alias="uninstall_message"),
        Field(name="webhookApiVersion", alias="webhook_api_version"),
        Field(name="shopifyDeveloped", alias="shopify_developed"),
        Field(name="id", alias="provider_id"),
        Field(name="failedRequirements", alias="failed_requirements", fields=failed_reqirements_fields),
        Field(name="feedback", fields=feedback_fields),
    ]

    assessments_fields: List[Field] = [
        Field(name="riskLevel", alias="risk_level"),
        Field(name="facts", fields=["description", "sentiment"]),
        Field(name="provider", fields=provider_fields),
    ]

    risk_fields: List[Field] = [
        "recommendation",
        Field(name="assessments", fields=assessments_fields),
    ]

    # main query
    query_nodes: List[Field] = [
        "__typename",
        "updatedAt",
        Field(name="id", alias="order_id"),
        Field(name="risk", fields=risk_fields),
    ]

    record_composition = {
        "new_record": "Order",
        # there are no record components provided for this stream.
    }

    def _process_assessments(self, assessments: Iterable[MutableMapping[str, Any]]) -> Iterable[MutableMapping[str, Any]]:
        for assessment in assessments:
            provider = assessment.get("provider", {})
            if provider:
                # save and resolve provider id
                provider["admin_graphql_api_id"] = provider.get("provider_id")
                provider["provider_id"] = self.tools.resolve_str_id(provider.get("provider_id"))
        return assessments

    def _has_risk_recommendation(self, recommendation: Optional[str]) -> bool:
        # if there are no risk recommendation, the value is literally "NONE",
        # we should skip such record, because there is no risk info for it.
        no_risk_pattern = "NONE"
        return recommendation != no_risk_pattern if recommendation else False

    def record_process_components(self, record: MutableMapping[str, Any]) -> Optional[Iterable[MutableMapping[str, Any]]]:
        """
        Defines how to process collected components.
        """
        # unnest mandatory fields from their placeholders
        risk = record.get("risk", {})
        recommendation = risk.get("recommendation") if risk else None
        # process records which has some risk recommendation
        if self._has_risk_recommendation(recommendation):
            # save and resolve id
            record["admin_graphql_api_id"] = record.get("order_id")
            record["order_id"] = self.tools.resolve_str_id(record.get("order_id"))
            # add old pk
            record["id"] = record.get("order_id")
            # add the `recommendation` field to the root lvl
            record["recommendation"] = recommendation
            assessments = risk.get("assessments", []) if risk else None
            record["assessments"] = self._process_assessments(assessments) if assessments else None
            # convert date-time cursors
            record["updatedAt"] = self.tools.from_iso8601_to_rfc3339(record, "updatedAt")
            # clean up the leftovers
            record.pop("risk", None)

            yield record
