#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

from pendulum import parse, today

from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams import Stream

from .google_ads import GoogleAds
from .models import CustomerModel
from .streams import (
    CustomerClient,
)


class SourceGoogleAds(YamlDeclarativeSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})

    # Raise exceptions on missing streams
    raise_exception_on_missing_stream = True

    @staticmethod
    def _validate_and_transform(config: Mapping[str, Any]):
        if config.get("end_date") == "":
            config.pop("end_date")
        if "customer_id" in config:
            config["customer_ids"] = [cid.strip() for cid in config["customer_id"].split(",") if cid.strip()]
            config.pop("customer_id")

        return config

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self._validate_and_transform(config)
        streams = super().streams(config=config)
        return streams
