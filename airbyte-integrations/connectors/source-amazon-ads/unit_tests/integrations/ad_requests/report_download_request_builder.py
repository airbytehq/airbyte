# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from .base_request_builder import AmazonAdsRequestBuilder


class ReportDownloadRequestBuilder(AmazonAdsRequestBuilder):
    @classmethod
    def download_endpoint(cls, report_id: str) -> "ReportDownloadRequestBuilder":
        return cls(report_id)

    def __init__(self, report_id: str) -> None:
        self._report_id: str = report_id

    @property
    def url(self):
        return (
            f"https://offline-report-storage-us-east-1-prod.s3.amazonaws.com"
            f"/{self._report_id}/{self._report_id}.json"
        )

    @property
    def headers(self):
        return None

    @property
    def query_params(self):
        return None

    @property
    def request_body(self):
        return None
