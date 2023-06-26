#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy


class ZendeskSupportAvailabilityStrategy(HttpAvailabilityStrategy):
    def check_availability(self, stream, logger, source):
        try:
            stream.get_api_records_count()
        except requests.HTTPError as error:
            return self.handle_http_error(stream, logger, source, error)
        return True, None
