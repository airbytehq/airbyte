#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


def rate_limit_handling(error):
    retried_cases = [
        (403, "quotaExceeded"),
        (429, "rateLimitExceeded"),
    ]

    return (error.resp.status, error.resp.reason) not in retried_cases
