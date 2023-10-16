#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import os

import source_file

# some integration tests doesn't setup dependences from
# requirements.txt file and Python can return a exception.
# Thus we should to import this parent module manually
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import ConnectorSpecification

LOCAL_STORAGE_NAME = "local"


class URLFileSecure(source_file.client.URLFile):
    """Updating of default logic:
    This connector shouldn't work with local files.
    """

    def __init__(self, url: str, provider: dict, binary=None, encoding=None):
        storage_name = provider["storage"].lower()
        if url.startswith("file://") or storage_name == LOCAL_STORAGE_NAME:
            raise RuntimeError("the local file storage is not supported by this connector.")
        super().__init__(url, provider, binary, encoding)


class SourceFileSecure(source_file.SourceFile):
    """Updating of default source logic
    This connector shouldn't work with local files.
    The base logic of this connector are implemented in the "source-file" connector.
    """

    @property
    def client_class(self):
        # replace a standard class variable to the new one
        class ClientSecure(source_file.client.Client):
            reader_class = URLFileSecure

        return ClientSecure

    def spec(self, logger: AirbyteLogger) -> ConnectorSpecification:
        """Tries to find and remove a spec data about local storage settings"""

        parent_code_dir = os.path.dirname(source_file.source.__file__)
        parent_spec_file = os.path.join(parent_code_dir, "spec.json")
        with open(parent_spec_file, "r") as f:
            spec = ConnectorSpecification.parse_obj(json.load(f))

        # correction of  the "storage" property to const type
        for provider in spec.connectionSpecification["properties"]["provider"]["oneOf"]:
            storage = provider["properties"]["storage"]

            if "enum" in storage:
                storage.pop("enum")
                storage["const"] = storage.pop("default")

        for i in range(len(spec.connectionSpecification["properties"]["provider"]["oneOf"])):
            provider = spec.connectionSpecification["properties"]["provider"]["oneOf"][i]
            if provider["properties"]["storage"]["const"] == LOCAL_STORAGE_NAME:
                spec.connectionSpecification["properties"]["provider"]["oneOf"].pop(i)
        return spec
