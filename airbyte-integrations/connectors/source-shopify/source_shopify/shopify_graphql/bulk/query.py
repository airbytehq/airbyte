#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from string import Template
from typing import Any, List, Mapping, MutableMapping, Optional, Union

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

    def record_process_components(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
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

    def record_process_components(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
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

    def record_process_components(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
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
        Field(name="productsCount"),
    ]

    record_composition = {
        "new_record": "Collection",
        # each collection has `publications`
        "record_components": ["CollectionPublication"],
    }

    def record_process_components(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
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

    def set_default_address(self, record: MutableMapping[str, Any], address_record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        if address_record.get("id") == record.get("defaultAddress", {}).get("id"):
            address_record["default"] = True
        return address_record

    def record_process_components(self, record: MutableMapping[str, Any]) -> Optional[MutableMapping[str, Any]]:
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

    def record_process_components(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
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

    inventory_levels_fields: List[Field] = [
        "__typename",
        "id",
        Field(name="available"),
        Field(name="item", fields=[Field(name="id", alias="inventory_item_id")]),
        Field(name="updatedAt"),
    ]

    def query(self, filter_query: Optional[str] = None) -> Query:
        # build the nested query first with `filter_query` to have the incremental syncs
        inventory_levels: List[Query] = [self.build("inventoryLevels", self.inventory_levels_fields, filter_query)]
        # build the main query around previous
        # return the constructed query operation
        return self.build(
            name=self.query_name,
            edges=self.query_nodes + inventory_levels,
            # passing more query args for `locations` query
            additional_query_args=self.locations_query_args,
        )

    def record_process_components(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        Defines how to process collected components.
        """

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

    def record_process_components(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
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

    def record_process_components(self, record: MutableMapping[str, Any]) -> Optional[MutableMapping[str, Any]]:
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
