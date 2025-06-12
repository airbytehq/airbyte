#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from dataclasses import dataclass

import backoff
import requests

from airbyte_cdk.sources.declarative.auth import DeclarativeOauth2Authenticator
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException


logger = logging.getLogger("airbyte")


class CommerceToolsOauth2Authenticator(DeclarativeOauth2Authenticator):
    @backoff.on_exception(
        backoff.expo,
        DefaultBackoffException,
        on_backoff=lambda details: logger.info(
            f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
        ),
        max_time=300,
    )
    def _get_refresh_access_token_response(self):
        region = self.config["region"]
        project_key = self.config["project_key"]
        host = self.config["host"]
        url = f"https://auth.{region}.{host}.commercetools.com/oauth/token?grant_type=client_credentials&scope=manage_project:{project_key}"
        try:
            response = requests.post(url, auth=(self.config["client_id"], self.config["client_secret"]))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if e.response.status_code == 429 or e.response.status_code >= 500:
                raise DefaultBackoffException(request=e.response.request, response=e.response)
            raise
        except Exception as e:
            raise Exception(f"Error while refreshing access token: {e}") from e
