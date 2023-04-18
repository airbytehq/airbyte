#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy


class FreshdeskAvailabilityStrategy(HttpAvailabilityStrategy):
    def reasons_for_unavailable_status_codes(self, stream, logger, source, error):
        unauthorized_error_message = f"The endpoint to access stream '{stream.name}' returned 401: Unauthorized. "
        unauthorized_error_message += "This is most likely due to wrong credentials. "
        unauthorized_error_message += self._visit_docs_message(logger, source)

        reasons = super(FreshdeskAvailabilityStrategy, self).reasons_for_unavailable_status_codes(stream, logger, source, error)
        reasons[requests.codes.UNAUTHORIZED] = unauthorized_error_message

        return reasons
