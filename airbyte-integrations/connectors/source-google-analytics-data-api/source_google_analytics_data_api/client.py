#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from collections import Mapping
from typing import Any, Dict, List

from google.analytics.data_v1beta import BetaAnalyticsDataClient, DateRange, Dimension, Metric, OrderBy, RunReportRequest, RunReportResponse
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
                        dimension_name=DEFAULT_CURSOR_FIELD, order_type=OrderBy.DimensionOrderBy.OrderType.ALPHANUMERIC
                    )
                )
            ],
        )

        return client.run_report(request)

    @staticmethod
    def response_to_list(response: RunReportResponse) -> List[Dict[str, Any]]:
        """
        Returns the report response as a list of dictionaries

        :param response: The run report response

        :return: A list of dictionaries, the key is either dimension name or metric name and the value is the dimension or the metric value
        """
        dimensions = list(map(lambda h: h.name, response.dimension_headers))
        metrics = list(map(lambda h: h.name, response.metric_headers))

        rows = []

        for row in response.rows:
            data = dict(zip(dimensions, list(map(lambda v: v.value, row.dimension_values))))
            data.update(dict(zip(metrics, list(map(lambda v: float(v.value), row.metric_values)))))
            rows.append(data)

        return rows
