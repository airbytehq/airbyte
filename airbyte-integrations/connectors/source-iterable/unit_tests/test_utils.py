#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pendulum
from source_iterable.utils import dateutil_parse


def test_dateutil_parse():
    assert pendulum.parse("2021-04-08 14:23:30 +00:00", strict=False) == dateutil_parse("2021-04-08 14:23:30 +00:00")
    assert pendulum.parse("2021-04-14T16:51:23+00:00", strict=False) == dateutil_parse("2021-04-14T16:51:23+00:00")
    assert pendulum.parse("2021-04-14T16:23:30.700000+00:00", strict=False) == dateutil_parse("2021-04-14T16:23:30.700000+00:00")
