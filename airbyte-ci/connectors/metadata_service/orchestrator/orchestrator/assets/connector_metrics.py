#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from collections import defaultdict
from typing import Optional

import sentry_sdk
from dagster import OpExecutionContext, asset
from google.cloud import storage
from orchestrator.logging import sentry

GROUP_NAME = "connector_metrics"


class StringNullJsonDecoder(json.JSONDecoder):
    """A JSON decoder that converts "null" strings to None."""

    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        return {k: (None if v == "null" else v) for k, v in obj.items()}


@sentry_sdk.trace
def _safe_read_gcs_file(gcs_blob: storage.Blob) -> Optional[str]:
    """Read the connector metrics jsonl blob.

    Args:
        gcs_blob (storage.Blob): The blob.

    Returns:
        dict: The metrics.
    """
    if not gcs_blob.exists():
        return None

    return gcs_blob.download_as_string().decode("utf-8")


def _convert_json_to_metrics_dict(jsonl_string: str) -> dict:
    """Convert the jsonl string to a metrics dict."""
    metrics_dict = defaultdict(dict)
    jsonl_lines = jsonl_string.splitlines()
    for line in jsonl_lines:
        data = json.loads(line, cls=StringNullJsonDecoder)
        connector_data = data["_airbyte_data"]
        connector_definition_id = connector_data["connector_definition_id"]
        airbyte_platform = connector_data["airbyte_platform"]
        metrics_dict[connector_definition_id][airbyte_platform] = connector_data

    return metrics_dict


# ASSETS


@asset(required_resource_keys={"latest_metrics_gcs_blob"}, group_name=GROUP_NAME)
@sentry.instrument_asset_op
def latest_connnector_metrics(context: OpExecutionContext) -> dict:
    latest_metrics_gcs_blob = context.resources.latest_metrics_gcs_blob

    latest_metrics_jsonl = _safe_read_gcs_file(latest_metrics_gcs_blob)
    if latest_metrics_jsonl is None:
        context.log.warn(f"No metrics found for {latest_metrics_gcs_blob.name}")
        return {}

    try:
        latest_metrics_dict = _convert_json_to_metrics_dict(latest_metrics_jsonl)
    except Exception as e:
        context.log.error(f"Error converting json to metrics dict: {str(e)}")
        return {}

    return latest_metrics_dict
