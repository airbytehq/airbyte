#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import json
from abc import ABC

from airbyte_cdk.sources.abstract_source import AbstractSource


class ConfigurableConnector(AbstractSource, ABC):
    def _load_config(self):
        # TODO is it better to do package loading?
        with open(self._path_to_spec, "r") as f:
            return json.loads(f.read())

    def get_spec_obj(self):
        try:
            with open("/airbyte/integration_code/source_sendgrid/spec.json", "r") as f:
                return json.loads(f.read())
        except FileNotFoundError:
            with open("./source_sendgrid/spec.json", "r") as f:
                return json.loads(f.read())
