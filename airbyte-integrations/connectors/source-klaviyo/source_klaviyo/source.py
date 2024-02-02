#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re
from http import HTTPStatus
from typing import Any, List, Mapping, Tuple

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from requests.exceptions import HTTPError
from source_klaviyo.streams import Campaigns, EmailTemplates, Events, Flows, GlobalExclusions, Lists, Metrics, Profiles


class SourceKlaviyo(AbstractSource):
    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """Connection check to validate that the user-provided config can be used to connect to the underlying API
        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, Any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            # we use metrics endpoint because it never returns an error
            _ = list(Metrics(api_key=config["api_key"]).read_records(sync_mode=SyncMode.full_refresh))
        except HTTPError as e:
            if e.response.status_code in (HTTPStatus.FORBIDDEN, HTTPStatus.UNAUTHORIZED):
                message = "Please provide a valid API key and make sure it has permissions to read specified streams."
            else:
                message = "Unable to connect to Klaviyo API with provided credentials."
            return False, message
        except Exception as e:
            original_error_message = repr(e)

            # Regular expression pattern to match the API key
            pattern = r"api_key=\b\w+\b"

            # Remove the API key from the error message
            error_message = re.sub(pattern, "api_key=***", original_error_message)

            return False, error_message
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Discovery method, returns available streams
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        api_key = config["api_key"]
        start_date = config.get("start_date")
        return [
            Campaigns(api_key=api_key, start_date=start_date),
            Events(api_key=api_key, start_date=start_date),
            GlobalExclusions(api_key=api_key, start_date=start_date),
            Lists(api_key=api_key, start_date=start_date),
            Metrics(api_key=api_key, start_date=start_date),
            Flows(api_key=api_key, start_date=start_date),
            EmailTemplates(api_key=api_key, start_date=start_date),
            Profiles(api_key=api_key, start_date=start_date),
        ]
