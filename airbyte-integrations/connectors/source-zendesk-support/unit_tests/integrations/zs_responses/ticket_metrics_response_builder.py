# Copyright (c) 202 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponse,
    HttpResponseBuilder,
    NestedPath,
    RecordBuilder,
    find_template,
)

from .pagination_strategies import CursorBasedPaginationStrategy


class TicketMetricsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def stateful_ticket_metrics_response(cls) -> "TicketMetricsResponseBuilder":
        return cls(find_template("stateful_ticket_metrics", __file__), FieldPath("ticket_metric"), CursorBasedPaginationStrategy())

    @classmethod
    def stateless_ticket_metrics_response(cls) -> "TicketMetricsResponseBuilder":
        return cls(find_template("stateless_ticket_metrics", __file__), NestedPath(["ticket_metrics", 0]), CursorBasedPaginationStrategy())

    def build(self) -> HttpResponse:
        for record in self._records:
            self._records_path.update(self._response, record.build())
        return HttpResponse(json.dumps(self._response), self._status_code)
