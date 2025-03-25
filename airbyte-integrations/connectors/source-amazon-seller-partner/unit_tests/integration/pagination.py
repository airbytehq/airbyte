#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict

from airbyte_cdk.test.mock_http.response_builder import PaginationStrategy


NEXT_TOKEN_STRING = "MDAwMDAwMDAwMQ=="


class VendorFulfillmentPaginationStrategy(PaginationStrategy):
    def update(self, response: Dict[str, Any]) -> None:
        response["payload"]["pagination"] = {}
        response["payload"]["pagination"]["nextToken"] = NEXT_TOKEN_STRING
