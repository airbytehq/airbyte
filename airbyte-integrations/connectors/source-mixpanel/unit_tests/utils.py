#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import urllib.parse


def setup_response(status, body):
    return [{"json": body, "status_code": status}]


def get_url_to_mock(stream):
    return urllib.parse.urljoin(stream.url_base, stream.path())
