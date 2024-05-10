#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Optional

import sgqlc.operation

from . import schema

_schema = schema
_schema_root = _schema.shopify_schema


# the graphql api requires the query filter to be snake case even though the column returned is camel case
def _camel_to_snake(camel_case: str):
    snake_case = []
    for char in camel_case:
        if char.isupper():
            snake_case.append("_" + char.lower())
        else:
            snake_case.append(char)
    return "".join(snake_case).lstrip("_")


def get_query_products(first: int, filter_field: str, filter_value: str, next_page_token: Optional[str]):
    op = sgqlc.operation.Operation(_schema_root.query_type)
    snake_case_filter_field = _camel_to_snake(filter_field)
    products_args = {
        "first": first,
        "query": f"{snake_case_filter_field}:>'{filter_value}'" if filter_value else None,
        "after": next_page_token,
    }
    products = op.products(**products_args)
    products.nodes.id()
    products.nodes.title()
    products.nodes.updated_at()
    products.nodes.created_at()
    products.nodes.published_at()
    products.nodes.status()
    products.nodes.vendor()
    products.nodes.product_type()
    products.nodes.tags()
    products.nodes.options()
    products.nodes.options().id()
    products.nodes.options().name()
    products.nodes.options().position()
    products.nodes.options().values()
    products.nodes.handle()
    products.nodes.description()
    products.nodes.tracks_inventory()
    products.nodes.total_inventory()
    products.nodes.total_variants()
    products.nodes.online_store_url()
    products.nodes.online_store_preview_url()
    products.nodes.description_html()
    products.nodes.is_gift_card()
    products.nodes.legacy_resource_id()
    products.nodes.media_count()
    products.page_info()
    products.page_info.has_next_page()
    products.page_info.end_cursor()
    return str(op)
