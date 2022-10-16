#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from googleapiclient.errors import HttpError


def rate_limit_handling(error):
    retried_cases = [
        (503,),
    ]

    if error.__class__ == HttpError:
        return (error.resp.status,) not in retried_cases
    return False
