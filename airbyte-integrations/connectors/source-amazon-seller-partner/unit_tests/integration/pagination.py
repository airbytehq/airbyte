#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict

from airbyte_cdk.test.mock_http.response_builder import PaginationStrategy

from .config import NEXT_TOKEN_STRING


class VendorDirectFulfillmentShippingPaginationStrategy(PaginationStrategy):
    def update(self, response: Dict[str, Any]) -> None:
        # TODO: review how pagination works for this stream
        # response["payload"]["pagination"] = {}
        # response["payload"]["pagination"]["nextToken"] = NEXT_TOKEN_STRING
        response["payload"]["nextToken"] = NEXT_TOKEN_STRING
