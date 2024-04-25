# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from urllib.parse import parse_qs, urlencode, urlparse

from mitmproxy import http


class SortQueryParams:
    """This addon sorts query parameters in the request URL.
    It is useful for testing purposes, as it makes it easier to compare requests and get cache hits.
    """

    def request(self, flow: http.HTTPFlow) -> None:
        if url := flow.request.url:
            parsed_url = urlparse(url)
            # Get query parameters as dictionary
            query_params = parse_qs(parsed_url.query)
            # Sort query parameters alphabetically
            sorted_params = {key: query_params[key] for key in sorted(query_params.keys())}
            # Reconstruct the URL with sorted query parameters
            sorted_url = parsed_url._replace(query=urlencode(sorted_params, doseq=True)).geturl()

            # Update the request URL
            flow.request.url = sorted_url


addons = [SortQueryParams()]
