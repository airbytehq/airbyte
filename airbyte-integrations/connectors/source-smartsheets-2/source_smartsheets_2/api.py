# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json

import smartsheet


def get_client(config: json) -> smartsheet.Smartsheet:
    """
    Initializes a Smartsheet client object from the config. The returned client
    has the option set to raise exceptions from API errors, which is not the
    default behavior.

    :param config: Dictionary that contains credentials information.

    :return: A Smartsheet client.
    """
    kwargs = {"access_token": config["api-access-token"]}
    client = smartsheet.Smartsheet(**kwargs)
    client.errors_as_exceptions(True)
    return client
