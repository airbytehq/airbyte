#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from airbyte_protocol import ConnectorSpecification
from base_python.logger import AirbyteLogger
from source_file import SourceFile as ParentSourceFile
from source_file.client import Client
from source_file.client import URLFile as ParentURLFile

LOCAL_STORAGE_NAME = "local"


class URLFileSecure(ParentURLFile):
    """Updating of default logic:
    This connector shouldn't work with local files.
    """

    def __init__(self, url: str, provider: dict):
        storage_name = provider["storage"].lower()
        if url.startswith("file://") or storage_name == LOCAL_STORAGE_NAME:
            raise RuntimeError("the local file storage is not supported by this connector.")
        super().__init__(url, provider)


# replace a standard class variable to the new one
Client.reader_class = URLFileSecure


class SourceFileSecure(ParentSourceFile):
    """Updating of default source logic
    This connector shouldn't work with local files.
    The base logic of this connector are implemented in the "source-file" connector.
    """

    # replace a standard class variable to the new one
    client_class = Client

    def spec(self, logger: AirbyteLogger) -> ConnectorSpecification:
        """Tries to find and remove a spec data about local storage settings"""
        spec = super().spec(logger=logger)
        for i in range(len(spec.connectionSpecification["properties"]["provider"]["oneOf"])):
            provider = spec.connectionSpecification["properties"]["provider"]["oneOf"][i]
            if (
                LOCAL_STORAGE_NAME in provider["properties"]["storage"]["enum"]
                or provider["properties"]["storage"]["default"] == provider["properties"]["storage"]
            ):
                spec.connectionSpecification["properties"]["provider"]["oneOf"].pop(i)
        return spec
