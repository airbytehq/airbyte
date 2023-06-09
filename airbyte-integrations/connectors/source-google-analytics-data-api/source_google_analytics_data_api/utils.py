#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import calendar
import datetime
from typing import Dict

import jsonschema
from airbyte_cdk.sources.streams.http import auth
from source_google_analytics_data_api.authenticator import GoogleServiceKeyAuthenticator

DATE_FORMAT = "%Y-%m-%d"

metrics_data_native_types_map: Dict = {
    "METRIC_TYPE_UNSPECIFIED": str,
    "TYPE_INTEGER": int,
    "TYPE_FLOAT": float,
    "TYPE_SECONDS": float,
    "TYPE_MILLISECONDS": float,
    "TYPE_MINUTES": float,
    "TYPE_HOURS": float,
    "TYPE_STANDARD": float,
    "TYPE_CURRENCY": float,
    "TYPE_FEET": float,
    "TYPE_MILES": float,
    "TYPE_METERS": float,
    "TYPE_KILOMETERS": float,
}

metrics_data_types_map: Dict = {
    "METRIC_TYPE_UNSPECIFIED": "string",
    "TYPE_INTEGER": "integer",
    "TYPE_FLOAT": "number",
    "TYPE_SECONDS": "number",
    "TYPE_MILLISECONDS": "number",
    "TYPE_MINUTES": "number",
    "TYPE_HOURS": "number",
    "TYPE_STANDARD": "number",
    "TYPE_CURRENCY": "number",
    "TYPE_FEET": "number",
    "TYPE_MILES": "number",
    "TYPE_METERS": "number",
    "TYPE_KILOMETERS": "number",
}

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

WRONG_JSON_SYNTAX = "The custom report entered is not in a JSON array format. Check the entered format follows the syntax in our docs: https://docs.airbyte.com/integrations/sources/google-analytics-data-api/"
NO_NAME = "The custom report entered does not contain a name, which is required. Check the entered format follows the syntax in our docs: https://docs.airbyte.com/integrations/sources/google-analytics-data-api/"
NO_DIMENSIONS = "The custom report entered does not contain dimensions, which is required. Check the entered format follows the syntax in our docs (https://docs.airbyte.com/integrations/sources/google-analytics-data-api/) and validate your custom query with the GA 4 Query Explorer (https://ga-dev-tools.google/ga4/query-explorer/)."
NO_METRICS = "The custom report entered does not contain metrics, which is required. Check the entered format follows the syntax in our docs (https://docs.airbyte.com/integrations/sources/google-analytics-data-api/) and validate your custom query with the GA 4 Query Explorer (https://ga-dev-tools.google/ga4/query-explorer/)."
WRONG_DIMENSIONS = "The custom report {report_name} entered contains invalid dimensions: {fields}. Validate your custom query with the GA 4 Query Explorer (https://ga-dev-tools.google/ga4/query-explorer/)."
WRONG_METRICS = "The custom report {report_name} entered contains invalid metrics: {fields}. Validate your custom query with the GA 4 Query Explorer (https://ga-dev-tools.google/ga4/query-explorer/)."
WRONG_PIVOTS = "The custom report {report_name} entered contains invalid pivots: {fields}. Ensure the pivot follow the syntax described in the docs (https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/Pivot)."


def datetime_to_secs(dt: datetime.datetime) -> int:
    return calendar.timegm(dt.utctimetuple())


def string_to_date(d: str, f: str = DATE_FORMAT, old_format=None) -> datetime.date:
    # To convert the old STATE date format "YYYY-MM-DD" to the new format "YYYYMMDD" we need this `old_format` additional param.
    # As soon as all current cloud sync will be converted to the new format we can remove this double format support.
    if old_format:
        try:
            return datetime.datetime.strptime(d, old_format).date()
        except ValueError:
            pass
    return datetime.datetime.strptime(d, f).date()


def date_to_string(d: datetime.date, f: str = DATE_FORMAT) -> str:
    return d.strftime(f)


def get_metrics_type(t: str) -> str:
    return metrics_data_types_map.get(t, "number")


def metrics_type_to_python(t: str) -> type:
    return metrics_data_native_types_map.get(t, str)


def get_dimensions_type(d: str) -> str:
    return "string"


def check_no_property_error(exc: jsonschema.ValidationError) -> str:
    mapper = {
        "'name' is a required property": NO_NAME,
        "'dimensions' is a required property": NO_DIMENSIONS,
        "'metrics' is a required property": NO_METRICS,
    }
    return mapper.get(exc.message)


def check_invalid_property_error(exc: jsonschema.ValidationError) -> str:
    mapper = {"dimensions": WRONG_DIMENSIONS, "metrics": WRONG_METRICS, "pivots": WRONG_PIVOTS}
    for property in mapper:
        if property in exc.schema_path:
            return mapper[property]
