#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Dict, Optional

from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from requests import HTTPError, codes


class KlaviyoAvailabilityStrategy(HttpAvailabilityStrategy):
    def reasons_for_unavailable_status_codes(
        self, stream: Stream, logger: logging.Logger, source: Optional[Source], error: HTTPError
    ) -> Dict[int, str]:
        reasons_for_codes: Dict[int, str] = super().reasons_for_unavailable_status_codes(stream, logger, source, error)
        reasons_for_codes[codes.UNAUTHORIZED] = (
            "This is most likely due to insufficient permissions on the credentials in use. "
            f"Try to create and use an API key with read permission for the '{stream.name}' stream granted"
        )

        return reasons_for_codes
