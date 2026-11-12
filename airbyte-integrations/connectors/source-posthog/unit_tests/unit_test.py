#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

from source_posthog import SourcePosthog

from airbyte_cdk.models import Status


def test_client_wrong_credentials(requests_mock):
    config = {"api_key": "blahblah", "start_date": "2021-01-01T00:00:00Z"}
    requests_mock.get("https://app.posthog.com/api/projects", status_code=401, json={"detail": "Invalid personal API key."})

    status = SourcePosthog(config=config).check(logger=logging.getLogger("airbyte"), config=config)

    assert status.status == Status.FAILED
