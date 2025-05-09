#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import urllib.parse as urlparse


def remove_params_from_url(url, params):
    parsed = urlparse.urlparse(url)
    query = urlparse.parse_qs(parsed.query, keep_blank_values=True)
    filtered = dict((k, v) for k, v in query.items() if k not in params)
    return urlparse.urlunparse(
        [parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlparse.urlencode(filtered, doseq=True), parsed.fragment]
    )
