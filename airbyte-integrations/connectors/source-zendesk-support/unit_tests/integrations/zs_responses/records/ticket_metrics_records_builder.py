# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath

from .records_builder import ZendeskSupportRecordBuilder


class TicketMetricsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def stateful_ticket_metrics_record(cls) -> "TicketMetricsRecordBuilder":
        record_template = cls.extract_record("stateful_ticket_metrics", __file__, FieldPath("ticket_metric"))
        return cls(record_template, FieldPath("id"), FieldPath("generated_timestamp"))

    @classmethod
    def stateless_ticket_metrics_record(cls) -> "TicketMetricsRecordBuilder":
        record_template = cls.extract_record("stateless_ticket_metrics", __file__, NestedPath(["ticket_metrics", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))
