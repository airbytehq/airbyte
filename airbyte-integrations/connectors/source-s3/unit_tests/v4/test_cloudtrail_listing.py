import logging
from datetime import datetime, date, timedelta
from unittest.mock import MagicMock, patch

import pytest
import pytz

from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from source_s3.v4.stream_reader import SourceS3StreamReader


class TestGenerateCloudTrailPrefixes:
    def test_generates_daily_prefixes_for_each_region(self):
        reader = SourceS3StreamReader()
        prefixes = reader._generate_cloudtrail_prefixes(
            base_prefix="AWSLogs/123/CloudTrail/",
            regions=["us-east-1", "eu-west-1"],
            start_date=date(2026, 3, 20),
            end_date=date(2026, 3, 22),
        )
        expected = [
            "AWSLogs/123/CloudTrail/us-east-1/2026/03/20/",
            "AWSLogs/123/CloudTrail/us-east-1/2026/03/21/",
            "AWSLogs/123/CloudTrail/us-east-1/2026/03/22/",
            "AWSLogs/123/CloudTrail/eu-west-1/2026/03/20/",
            "AWSLogs/123/CloudTrail/eu-west-1/2026/03/21/",
            "AWSLogs/123/CloudTrail/eu-west-1/2026/03/22/",
        ]
        assert sorted(prefixes) == sorted(expected)

    def test_single_day(self):
        reader = SourceS3StreamReader()
        prefixes = reader._generate_cloudtrail_prefixes(
            base_prefix="AWSLogs/123/CloudTrail/",
            regions=["us-east-1"],
            start_date=date(2026, 3, 22),
            end_date=date(2026, 3, 22),
        )
        assert prefixes == ["AWSLogs/123/CloudTrail/us-east-1/2026/03/22/"]

    def test_cross_month_boundary(self):
        reader = SourceS3StreamReader()
        prefixes = reader._generate_cloudtrail_prefixes(
            base_prefix="AWSLogs/123/CloudTrail/",
            regions=["us-east-1"],
            start_date=date(2026, 2, 28),
            end_date=date(2026, 3, 1),
        )
        assert len(prefixes) == 2
        assert "AWSLogs/123/CloudTrail/us-east-1/2026/02/28/" in prefixes
        assert "AWSLogs/123/CloudTrail/us-east-1/2026/03/01/" in prefixes


class TestExtractCloudTrailBasePrefix:
    def test_extracts_from_globs(self):
        reader = SourceS3StreamReader()
        prefix = reader._extract_cloudtrail_base_prefix(
            ["AWSLogs/174522763890/CloudTrail/**/*.json.gz"]
        )
        assert prefix == "AWSLogs/174522763890/CloudTrail/"

    def test_extracts_from_prefix_with_trailing_slash(self):
        reader = SourceS3StreamReader()
        prefix = reader._extract_cloudtrail_base_prefix(
            ["AWSLogs/174522763890/CloudTrail/us-east-1/**"]
        )
        assert prefix == "AWSLogs/174522763890/CloudTrail/"

    def test_returns_none_if_no_cloudtrail(self):
        reader = SourceS3StreamReader()
        prefix = reader._extract_cloudtrail_base_prefix(["data/**/*.csv"])
        assert prefix is None


class TestDiscoverCloudTrailRegions:
    def test_discovers_regions_from_s3(self):
        reader = SourceS3StreamReader()
        mock_s3 = MagicMock()
        mock_s3.list_objects_v2.return_value = {
            "CommonPrefixes": [
                {"Prefix": "AWSLogs/123/CloudTrail/us-east-1/"},
                {"Prefix": "AWSLogs/123/CloudTrail/eu-west-1/"},
                {"Prefix": "AWSLogs/123/CloudTrail/ap-northeast-1/"},
            ]
        }
        regions = reader._discover_cloudtrail_regions(mock_s3, "bucket", "AWSLogs/123/CloudTrail/")
        assert regions == ["us-east-1", "eu-west-1", "ap-northeast-1"]

    def test_empty_bucket_returns_empty(self):
        reader = SourceS3StreamReader()
        mock_s3 = MagicMock()
        mock_s3.list_objects_v2.return_value = {}
        regions = reader._discover_cloudtrail_regions(mock_s3, "bucket", "AWSLogs/123/CloudTrail/")
        assert regions == []
