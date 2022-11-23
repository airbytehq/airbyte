import sgqlc.operation

from . import shopify_schema
from typing import Optional

_schema = shopify_schema
_schema_root = _schema.shopify_schema


def get_query_products(first: int, filter_field: str, filter_value: str, next_page_token: Optional[str]):
    op = sgqlc.operation.Operation(_schema_root.query_type)
    if next_page_token:
        products = op.products(first=first, query=f"{filter_field}:>'{filter_value}'", after=next_page_token)
    else:
        products = op.products(first=first, query=f"{filter_field}:>'{filter_value}'")
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
