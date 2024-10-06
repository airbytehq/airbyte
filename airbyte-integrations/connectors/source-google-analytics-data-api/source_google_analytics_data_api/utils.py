#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import argparse
import calendar
import datetime
import json
import sys
from typing import Dict

import jsonschema
import pandas as pd
from airbyte_cdk.sources.streams.http import requests_native_auth as auth
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
API_LIMIT_PER_HOUR = "Your API key has reached its limit for the hour. Wait until the quota refreshes in an hour to retry."
WRONG_CUSTOM_REPORT_CONFIG = "Please check configuration for custom report {report}."


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


def get_source_defined_primary_key(stream):
    """
    https://github.com/airbytehq/airbyte/pull/26283
    It's not a very elegant way to get source_defined_primary_key inside the stream.
    It's used only for a smooth transition to the new primary key.
    As soon as the transition will complete we can remove this function.
    """
    if len(sys.argv) > 1 and "read" == sys.argv[1]:
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        read_subparser = subparsers.add_parser("read")
        read_subparser.add_argument("--catalog", type=str, required=True)
        args, unknown = parser.parse_known_args()
        catalog = json.loads(open(args.catalog).read())
        res = {s["stream"]["name"]: s["stream"].get("source_defined_primary_key") for s in catalog["streams"]}
        return res.get(stream)


def transform_string_filter(filter):
    string_filter = {"value": filter.get("value")}
    if "matchType" in filter:
        string_filter["matchType"] = filter.get("matchType")[0]
    if "caseSensitive" in filter:
        string_filter["caseSensitive"] = filter.get("caseSensitive")
    return {"stringFilter": string_filter}


def transform_in_list_filter(filter):
    in_list_filter = {"values": filter.get("values")}
    if "caseSensitive" in filter:
        in_list_filter["caseSensitive"] = filter.get("caseSensitive")
    return {"inListFilter": in_list_filter}


def transform_numeric_filter(filter):
    numeric_filter = {
        "value": {filter.get("value").get("value_type"): filter.get("value").get("value")},
    }
    if "operation" in filter:
        numeric_filter["operation"] = filter.get("operation")[0]
    return {"numericFilter": numeric_filter}


def transform_between_filter(filter):
    from_value = filter.get("fromValue")
    to_value = filter.get("toValue")

    from_value_type = from_value.get("value_type")
    to_value_type = to_value.get("value_type")

    if from_value_type == "doubleValue" and isinstance(from_value.get("value"), str):
        from_value["value"] = float(from_value.get("value"))
    if to_value_type == "doubleValue" and isinstance(to_value.get("value"), str):
        to_value["value"] = float(to_value.get("value"))

    return {
        "betweenFilter": {
            "fromValue": {from_value_type: from_value.get("value")},
            "toValue": {to_value_type: to_value.get("value")},
        }
    }


def transform_expression(expression):
    transformed_expression = {"fieldName": expression.get("field_name")}
    filter = expression.get("filter")
    filter_name = filter.get("filter_name")

    if filter_name == "stringFilter":
        transformed_expression.update(transform_string_filter(filter))
    elif filter_name == "inListFilter":
        transformed_expression.update(transform_in_list_filter(filter))
    elif filter_name == "numericFilter":
        transformed_expression.update(transform_numeric_filter(filter))
    elif filter_name == "betweenFilter":
        transformed_expression.update(transform_between_filter(filter))

    return {"filter": transformed_expression}


def transform_json(original_json):
    transformed_json = {}
    filter_type = original_json.get("filter_type")

    if filter_type in ["andGroup", "orGroup"]:
        expressions = original_json.get("expressions", [])
        transformed_expressions = [transform_expression(exp) for exp in expressions]
        transformed_json = {filter_type: {"expressions": transformed_expressions}} if transformed_expressions else {}

    elif filter_type == "notExpression":
        expression = original_json.get("expression")
        transformed_expression = transform_expression(expression)
        transformed_json = {filter_type: transformed_expression}

    elif filter_type == "filter":
        transformed_json = transform_expression(original_json)

    return transformed_json


def serialize_to_date_string(date: str, date_format: str, date_type: str) -> str:
    """
    Serialize a date string to a different date format based on the date_type.

    Parameters:
    - date (str): The input date string.
    - date_format (str): The desired output format for the date string.
    - date_type (str): The type of the date string ('yearWeek', 'yearMonth', or 'year').

    Returns:
    str: The date string formatted according to date_format.

    Examples:
    '202245' -> '2022-11-07'
    '202210' -> '2022-10-01'
    '2022' -> '2022-01-01'
    """
    if date_type == "yearWeek":
        return pd.to_datetime(f"{date}1", format="%Y%W%w").strftime(date_format)
    elif date_type == "yearMonth":
        year = int(date[:-2])
        month = int(date[-2:])
        return datetime.datetime(year, month, 1).strftime(date_format)
    return datetime.datetime(int(date), 1, 1).strftime(date_format)
