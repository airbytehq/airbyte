#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from requests import codes as status_codes

@staticmethod
def error_handler(error):
    return error.resp.status != status_codes.TOO_MANY_REQUESTS
