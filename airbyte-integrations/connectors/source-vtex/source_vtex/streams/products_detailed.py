import requests
from typing import Any, Mapping, Iterable, Optional, MutableMapping
from source_vtex.base_streams import VtexStream
from airbyte_cdk.sources.streams.http.http import HttpSubStream


class ProductsDetailed(HttpSubStream, VtexStream):
    """
    This stream brings the product data. It's mandatory to pass a product id,
    so it has to be a SubStream, therefore in this case a stream that brings
    product id should be set as parent for this Products stream.
    """

    primary_key = "productId"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "/api/catalog_system/pub/products/search/"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        productId = stream_slice["parent"][self.primary_key]
        return {"fq": f"productId:{productId}"}

    def next_page_token(
        self, response: requests.Response
    ) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(
        self, response: requests.Response, **kwargs
    ) -> Iterable[Mapping]:
        response_json = response.json()
        for product in response_json:
            clusterHighlights = product["clusterHighlights"]
            productClusters = product["productClusters"]
            searchableClusters = product["searchableClusters"]

            product["clusterHighlights"] = []
            product["productClusters"] = []
            product["searchableClusters"] = []

            for cluster in clusterHighlights:
                product["clusterHighlights"].append(
                    {
                        "clusterId": cluster,
                        "description": clusterHighlights[cluster],
                    }
                )

            for cluster in productClusters:
                product["productClusters"].append(
                    {
                        "clusterId": cluster,
                        "description": productClusters[cluster],
                    }
                )

            for cluster in searchableClusters:
                product["searchableClusters"].append(
                    {
                        "clusterId": cluster,
                        "description": searchableClusters[cluster],
                    }
                )

            del product["items"]

            yield product
