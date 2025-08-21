#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, List, Mapping

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.requesters.request_options.request_options_provider import RequestOptionsProvider
from airbyte_cdk.sources.declarative.transformations.transformation import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from source_pinterest.utils import get_analytics_columns


class AdAccountRecordExtractor(RecordExtractor):
    """
    Custom extractor for handling different response formats from the Ad Accounts endpoint.

    This extractor is necessary to handle cases where an `account_id` is present in the request.
    - When querying all ad accounts, the response contains an "items" key with a list of accounts.
    - When querying a specific ad account, the response returns a single dictionary representing that account.
    """

    def extract_records(self, response: requests.Response) -> List[Record]:
        data = response.json()

        if not data:
            return []

        # Extract records from "items" if present
        if isinstance(data, dict) and "items" in data:
            return data["items"]

        # If the response is a single object, wrap it in a list
        if isinstance(data, dict):
            return [data]
        return []


class PinterestReportDownloadExtractor(RecordExtractor):
    """
    Custom extractor for Pinterest Analytics Report downloads that flattens metrics.
    
    Transforms the downloaded report data structure from:
    {campaign_id: [records]} to individual records with campaign_id added.
    """
    
    def extract_records(self, response: requests.Response) -> List[Record]:
        """Extract and flatten report records from downloaded data."""
        data = response.json()
        
        if not data or not isinstance(data, dict):
            return []
            
        records = []
        # Pinterest report downloads contain metrics grouped by campaign_id
        for campaign_id, campaign_records in data.items():
            if isinstance(campaign_records, list):
                for record in campaign_records:
                    if isinstance(record, dict):
                        # Add campaign_id to each record
                        record["campaign_id"] = campaign_id
                        records.append(record)
        
        return records


class PinterestReportRequestBodyProvider(RequestOptionsProvider):
    """
    Provides request body for Pinterest Analytics Report creation.
    
    Builds the JSON body required for POST requests to create analytics reports.
    """
    
    def __init__(self, config: Config, level: str, granularity: str = "DAY", **kwargs):
        super().__init__(config, **kwargs)
        self.level = level
        self.granularity = granularity
    
    def get_request_options(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: StreamSlice,
        next_page_token: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """Return the request body for report creation."""
        return {
            "json": {
                "start_date": stream_slice["start_date"],
                "end_date": stream_slice["end_date"],
                "granularity": self.granularity,
                "columns": get_analytics_columns().split(","),
                "level": self.level,
            }
        }


class PinterestReportTransformation(RecordTransformation):
    """
    Transforms Pinterest Analytics Report records to add metadata and normalize fields.
    """
    
    def __init__(self, config: Config, level: str, **kwargs):
        super().__init__(config, **kwargs)
        self.level = level
    
    def transform(
        self, record: Record, config: Config, stream_slice: StreamSlice, stream_state: StreamState
    ) -> Record:
        """Transform individual report records."""
        if not isinstance(record, dict):
            return record
            
        # Add report metadata
        transformed_record = record.copy()
        transformed_record["report_level"] = self.level
        transformed_record["slice_start_date"] = stream_slice.get("start_date")
        transformed_record["slice_end_date"] = stream_slice.get("end_date")
        
        # Ensure numeric fields are properly typed
        numeric_fields = ["impressions", "clicks", "spend", "ctr", "cpm", "cpc"]
        for field in numeric_fields:
            if field in transformed_record and transformed_record[field] is not None:
                try:
                    transformed_record[field] = float(transformed_record[field])
                except (ValueError, TypeError):
                    pass  # Keep original value if conversion fails

        return transformed_record
