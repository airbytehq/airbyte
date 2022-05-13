#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import json
from abc import abstractmethod
from typing import Tuple

from airbyte_cdk.sources.abstract_source import AbstractSource


class ConfigurableSource(AbstractSource):
    @abstractmethod
    def connection_checker(self):
        pass

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return self.connection_checker().check_connection(logger, config)

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
