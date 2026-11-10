# Copyright (c) 2026 Airbyte, Inc., all rights reserved.


class ConfigBuilder:
    def build(self) -> dict:
        return {
            "api_key": "test-api-key",
            "search_query": "airbyte",
            "search_in": ["title", "description"],
            "sources": [],
            "domains": ["example.com"],
            "exclude_domains": ["excluded.example.com"],
            "start_date": "2025-01-01",
            "end_date": "2025-01-02",
            "language": "en",
            "sort_by": "publishedAt",
            "country": "us",
            "category": "technology",
        }
