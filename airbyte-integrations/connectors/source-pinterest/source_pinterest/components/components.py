#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import time
from typing import Any, Dict, Iterable, List, Mapping

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.requesters.request_options.request_options_provider import RequestOptionsProvider
from airbyte_cdk.sources.declarative.retrievers.retriever import Retriever
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
    
    def __init__(self, level: str = "CAMPAIGN", config: Config = None, **kwargs):
        # RecordTransformation.__init__() takes no arguments in CDK v4
        super().__init__()
        self.level = level
        self.config = config
    
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


class PinterestReportRetriever(Retriever):
    """
    Custom retriever for Pinterest Analytics Reports that handles async report generation.
    
    This retriever implements the async flow:
    1. POST to create a report
    2. Poll for report status 
    3. Download the completed report data
    """
    
    def __init__(self, report_level: str = "CAMPAIGN", config: Config = None, **kwargs):
        # Retriever.__init__() may not take config in CDK v4
        super().__init__()
        self.report_level = report_level
        self.base_url = "https://api.pinterest.com/v5/"
        self.config = config
        
    def read_records(
        self, sync_mode, cursor_field, stream_slice, stream_state
    ) -> Iterable[Record]:
        """Read records by creating and downloading async reports."""
        ad_account_id = stream_slice.get("id") or stream_slice.get("parent_slice", {}).get("id")
        if not ad_account_id:
            return []
            
        # Step 1: Create report
        creation_response = self._create_report(ad_account_id, stream_slice)
        if not creation_response or "token" not in creation_response:
            return []
            
        # Step 2: Poll for report completion
        download_url = self._poll_for_completion(ad_account_id, creation_response["token"])
        if not download_url:
            return []
            
        # Step 3: Download and extract records
        return self._download_and_extract_records(download_url, stream_slice)
        
    def _create_report(self, ad_account_id: str, stream_slice: StreamSlice) -> Dict[str, Any]:
        """Create an analytics report via POST request."""
        url = f"{self.base_url}ad_accounts/{ad_account_id}/reports"
        
        payload = {
            "start_date": stream_slice["start_date"],
            "end_date": stream_slice["end_date"], 
            "granularity": "DAY",
            "level": self.report_level,
            "columns": get_analytics_columns().split(",")
        }
        
        # Use authenticator from config
        headers = {}
        if self.config and isinstance(self.config, dict) and "authenticator" in self.config:
            auth_headers = self.config["authenticator"].get_auth_header()
            headers.update(auth_headers)
            
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        return {}
        
    def _poll_for_completion(
        self, ad_account_id: str, token: str, max_attempts: int = 30
    ) -> str:
        """Poll for report completion and return download URL."""
        url = f"{self.base_url}ad_accounts/{ad_account_id}/reports"
        
        # Use authenticator from config
        headers = {}
        if self.config and isinstance(self.config, dict) and "authenticator" in self.config:
            auth_headers = self.config["authenticator"].get_auth_header()
            headers.update(auth_headers)
        
        for _ in range(max_attempts):
            response = requests.get(url, params={"token": token}, headers=headers)
            if response.status_code == 200:
                data = response.json()
                status = data.get("report_status")
                
                if status == "FINISHED":
                    return data.get("url")
                elif status in ["FAILED", "CANCELLED", "EXPIRED"]:
                    break
                    
            time.sleep(10)  # Wait 10 seconds between polls
            
        return None
        
    def _download_and_extract_records(
        self, download_url: str, stream_slice: StreamSlice
    ) -> Iterable[Record]:
        """Download report data and extract records."""
        response = requests.get(download_url)
        if response.status_code != 200:
            return []
            
        data = response.json()
        if not data or not isinstance(data, dict):
            return []
            
        records = []
        # Pinterest report downloads contain metrics grouped by campaign_id
        for campaign_id, campaign_records in data.items():
            if isinstance(campaign_records, list):
                for record in campaign_records:
                    if isinstance(record, dict):
                        # Add campaign_id and metadata to each record
                        record["campaign_id"] = campaign_id
                        record["report_level"] = self.report_level
                        record["slice_start_date"] = stream_slice.get("start_date")
                        record["slice_end_date"] = stream_slice.get("end_date")
                        records.append(record)
        
        return records