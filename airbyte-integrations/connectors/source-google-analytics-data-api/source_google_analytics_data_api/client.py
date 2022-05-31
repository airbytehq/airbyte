#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from collections import Mapping
from typing import List

from google.analytics.data_v1beta import Dimension, Metric, RunReportRequest, OrderBy, DateRange, \
    BetaAnalyticsDataClient, RunReportResponse
from google.oauth2 import service_account

DEFAULT_CURSOR_FIELD = "date"


class Client:
    def __init__(self, json_credentials: Mapping[str, str]):
        self.json_credentials = json_credentials

    def run_report(self, property_id: str, dimensions: List[str], metrics: List[str], start_date: str, end_date: str) -> RunReportResponse:
        dimensions = [Dimension(name=dim) for dim in dimensions if dim != DEFAULT_CURSOR_FIELD]
        dimensions.append(Dimension(name=DEFAULT_CURSOR_FIELD))

        metrics = [Metric(name=metric) for metric in metrics]

        credentials = service_account.Credentials.from_service_account_info(self.json_credentials)
        client = BetaAnalyticsDataClient(credentials=credentials)

        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=dimensions,
            metrics=metrics,
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            order_bys=[
                OrderBy(
                    dimension=OrderBy.DimensionOrderBy(
                        dimension_name=DEFAULT_CURSOR_FIELD,
                        order_type=OrderBy.DimensionOrderBy.OrderType.ALPHANUMERIC
                    )
                )
            ]
        )
        return client.run_report(request)
