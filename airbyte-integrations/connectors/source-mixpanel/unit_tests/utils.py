#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
def setup_response(status, body):
    return [{"json": body, "status_code": status}]
