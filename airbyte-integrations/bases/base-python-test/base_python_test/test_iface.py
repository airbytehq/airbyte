#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
import pkgutil
from typing import List

from airbyte_protocol import ConfiguredAirbyteCatalog, ConnectorSpecification


class StandardSourceTestIface:
    def __init__(self):
        pass

    def get_spec(self) -> ConnectorSpecification:
        raise NotImplementedError

    def get_config(self) -> object:
        raise NotImplementedError

    def get_catalog(self) -> ConfiguredAirbyteCatalog:
        raise NotImplementedError

    def get_regex_tests(self) -> List[str]:
        return []

    def get_state(self) -> object:
        return {}

    def setup(self) -> None:
        pass

    def teardown(self) -> None:
        pass


class DefaultStandardSourceTest(StandardSourceTestIface):
    SPEC_FILENAME = "spec.json"
    CONFIG_FILENAME = "config.json"
    CONFIGURED_CATALOG_FILENAME = "configured_catalog.json"

    def get_spec(self) -> ConnectorSpecification:
        raw_spec = pkgutil.get_data(self.__class__.__module__.split(".")[0], self.SPEC_FILENAME)
        return ConnectorSpecification.parse_obj(json.loads(raw_spec))

    def get_config(self) -> object:
        return json.loads(pkgutil.get_data(self.__class__.__module__.split(".")[0], self.CONFIG_FILENAME))

    def get_catalog(self) -> ConfiguredAirbyteCatalog:
        raw_catalog = pkgutil.get_data(self.__class__.__module__.split(".")[0], self.CONFIGURED_CATALOG_FILENAME)
        return ConfiguredAirbyteCatalog.parse_obj(json.loads(raw_catalog))
