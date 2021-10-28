from typing import Any, Mapping
from source_vtex.base_streams import VtexSubtStream


class OrderDetails(VtexSubtStream):
    """
    TODO: Change class name to match the table/data source this stream
        corresponds to.
    """

    primary_key = "orderId"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        order_id = stream_slice["parent"][self.primary_key]
        return f"/api/oms/pvt/orders/{order_id}"
