from pprint import pprint
from typing import Dict

from airbyte_cdk.sources.streams.http import auth
from source_google_analytics_arcane.authenticator import GoogleServiceKeyAuthenticator

authenticator_class_map: Dict = {
    "Service": (GoogleServiceKeyAuthenticator, lambda credentials: {"credentials": credentials["credentials_json"]}),
    "Client": (
        auth.Oauth2Authenticator,
        lambda credentials: {
            "token_refresh_endpoint": "https://oauth2.googleapis.com/token",
            "scopes": ["https://www.googleapis.com/auth/analytics.readonly"],
            "client_secret": credentials["client_secret"],
            "client_id": credentials["client_id"],
            "refresh_token": credentials["refresh_token"],
        },
    ),
}

page_performance_request_body = {
    "metrics": [
        "activeUsers",
        "conversions",
        "engagedSessions",
        "eventCount",
        "screenPageViews",
        "sessions",
        "userEngagementDuration",
    ],
    "dimensions": [
        "date",
        "fullPageUrl",
        "pageTitle",
    ],
    "orderBys": [
        {
            "desc": True,
            "dimension": {
                "orderType": "NUMERIC",
                "dimensionName": "date"
            }
        }
    ]

}


def flatten_report_pages_performance_data(input_data):
    flattened_data = []

    for entry in input_data:
        dimension_headers = [header["name"] for header in entry["dimensionHeaders"]]
        metric_headers = [header["name"] for header in entry["metricHeaders"]]

        if entry.get("rows"):
            for row in entry.get("rows"):
                flattened_row = {}
                dimension_values = row["dimensionValues"]
                metric_values = row["metricValues"]

                for i, dimension_value in enumerate(dimension_values):
                    flattened_row[dimension_headers[i]] = dimension_value.get("value", None)

                for i, metric_value in enumerate(metric_values):
                    flattened_row[metric_headers[i]] = metric_value.get("value", None)

                flattened_data.append(flattened_row)

    return flattened_data
