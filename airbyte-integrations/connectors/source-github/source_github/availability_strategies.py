#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Dict, Optional

import requests
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams.core import Stream
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from airbyte_cdk.sources.utils.stream_helpers import StreamHelper
from requests import HTTPError


class OrganizationBasedAvailabilityStrategy(HttpAvailabilityStrategy):
    """
    Availability Strategy for organization-based streams.
    """

    def reasons_for_unavailable_status_codes(
        self, stream: Stream, logger: logging.Logger, source: Optional["Source"], error: HTTPError
    ) -> Dict[int, str]:
        stream_slice = StreamHelper().get_stream_slice(stream)
        organization = stream_slice["organization"]
        response_error_msg = str(error.response.json().get("message"))

        reasons_for_codes = {
            requests.codes.NOT_FOUND: f"`{stream.__class__.__name__}` stream isn't available for organization `{organization}`.",
            # When `403` for the stream, that has no access to the organization's teams, based on OAuth Apps Restrictions:
            # https://docs.github.com/en/organizations/restricting-access-to-your-organizations-data/enabling-oauth-app-access-restrictions-for-your-organization
            requests.codes.FORBIDDEN: f"`{stream.name}` stream isn't available for organization `{organization}`. Full error message: {response_error_msg}",
        }
        return reasons_for_codes


class RepositoryBasedAvailabilityStrategy(HttpAvailabilityStrategy):
    """
    Availability Strategy for repository-based streams.
    """

    def reasons_for_unavailable_status_codes(
        self, stream: Stream, logger: logging.Logger, source: Optional["Source"], error: HTTPError
    ) -> Dict[int, str]:
        stream_slice = StreamHelper().get_stream_slice(stream)
        repository = stream_slice["repository"]
        error_msg = str(error.response.json().get("message"))

        reasons_for_codes = {
            requests.codes.NOT_FOUND: f"`{stream.name}` stream isn't available for repository `{repository}`.",
            requests.codes.FORBIDDEN: f"`{stream.name}` stream isn't available for repository `{repository}`. Full error message: {error_msg}",
            requests.codes.CONFLICT: f"`{stream.name}` stream isn't available for repository `{repository}`, it seems like this repository is empty.",
        }
        return reasons_for_codes


class WorkflowRunsAvailabilityStrategy(RepositoryBasedAvailabilityStrategy):
    """
    AvailabilityStrategy for the 'WorkflowRuns' stream.
    """

    def reasons_for_unavailable_status_codes(
        self, stream: Stream, logger: logging.Logger, source: Optional["Source"], error: HTTPError
    ) -> Dict[int, str]:
        stream_slice = StreamHelper().get_stream_slice(stream)
        repository = stream_slice["repository"]
        reasons_for_codes = super().reasons_for_unavailable_status_codes(stream, logger, source, error).copy()
        server_error_msg = f"Syncing `{stream.name}` stream isn't available for repository `{repository}`."
        reasons_for_codes[requests.codes.SERVER_ERROR] = server_error_msg
        return reasons_for_codes


class ProjectsAvailabilityStrategy(RepositoryBasedAvailabilityStrategy):
    """
    AvailabilityStrategy for the 'Projects' stream.
    """

    def reasons_for_unavailable_status_codes(
        self, stream: Stream, logger: logging.Logger, source: Optional["Source"], error: HTTPError
    ) -> Dict[int, str]:
        stream_slice = StreamHelper().get_stream_slice(stream)
        repository = stream_slice["repository"]
        reasons_for_codes = super().reasons_for_unavailable_status_codes(stream, logger, source, error).copy()

        # Some repos don't have projects enabled and we we get "410 Client Error: Gone for
        # url: https://api.github.com/repos/xyz/projects?per_page=100" error.
        gone_error_msg = f"`Projects` stream isn't available for repository `{repository}`."
        reasons_for_codes[requests.codes.GONE] = gone_error_msg

        return reasons_for_codes
