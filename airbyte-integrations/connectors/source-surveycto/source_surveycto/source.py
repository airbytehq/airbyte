#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import base64
from abc import ABC
from ast import arg
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from source_surveycto.streams import FormData, FormDataset, FormDefinitionData, FormRepeatGroupData, Mediafiles

from .helpers import Helpers


class SourceSurveycto(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Checks the connection to the SurveyCTO data source.

        Args:
            logger: The logger object for logging messages.
            config: The configuration object containing the necessary connection details.

        Returns:
            A tuple containing a boolean indicating the connection status and any error message.
        """

        try:
            response = Helpers.login(config)

            return response, None
        except Exception as error:
            return False, f"Unable to connect - {(error)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Returns a list of Stream objects based on the provided configuration.

        Args:
            config (Mapping[str, Any]): The configuration parameters for the streams.

        Returns:
            List[Stream]: A list of Stream objects.
        """
        auth = None

        forms = config.get("form_id", [])
        datasets = config.get("dataset_id", [])
        form_streams = []  # These are the forms that require form id. We will create a stream for each form
        dataset_streams = []  # These are the forms that require dataset id. We will create a stream for each dataset
        for form in forms:
            args = {"authenticator": auth, "config": config}
            config["form_id"] = form
            stream_data = FormData(**args)
            stream_definition = FormDefinitionData(**args)
            stream_repeat_group = FormRepeatGroupData(**args)
            form_streams.extend([stream_data, stream_definition, stream_repeat_group])

        for dataset in datasets:
            args = {"authenticator": auth, "config": config}
            config["dataset_id"] = dataset
            dataset_streams.append(FormDataset(**args))
        args = {"authenticator": auth, "config": config}
        return [*form_streams, *dataset_streams, Mediafiles(**args)]
