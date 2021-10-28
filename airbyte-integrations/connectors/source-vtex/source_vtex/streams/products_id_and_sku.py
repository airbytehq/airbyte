import requests
from typing import Any, Mapping, Iterable, Optional, MutableMapping
from source_vtex.base_streams import VtexStream


class ProductsIdAndSku(VtexStream):
    """
    TODO: Change class name to match the table/data source this stream
        corresponds to.
    """

    primary_key = "productId"

    @property
    def cursor_field(self) -> str:
        return "productId"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:

        return "/api/catalog_system/pvt/products/GetProductAndSkuIds"

    def next_page_token(
        self, response: requests.Response
    ) -> Optional[Mapping[str, Any]]:
        batch_size = 50  # It has to be 50. The API limits to this value.
        response_json = response.json()
        _to = response_json["range"]["to"]
        total = response_json["range"]["total"]

        if _to <= total:
            return {"_from": _to + 1, "_to": _to + batch_size}

        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # It is required to skip first product, because it's id is zero and
        # that breaks the endpoint where the product details are retrieved
        _from = next_page_token["_from"] if next_page_token else 2
        _to = next_page_token["_to"] if next_page_token else 50

        return {"_from": _from, "_to": _to}

    def parse_response(
        self, response: requests.Response, **kwargs
    ) -> Iterable[Mapping]:
        response_json = response.json()["data"]

        for productId in response_json:
            yield {"productId": productId, "skuIds": response_json[productId]}
