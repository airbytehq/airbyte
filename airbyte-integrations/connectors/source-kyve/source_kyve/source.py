#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from copy import deepcopy
from typing import Any, List, Mapping, Tuple

import requests

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .stream import KYVEStream


class SourceKyve(AbstractSource):
    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        # check that pools and bundles are the same length
        pools = config.get("pool_ids").split(",")
        start_ids = config.get("start_ids").split(",")

        if not len(pools) == len(start_ids):
            return False, "Please add a start_id for every pool"

        for pool_id in pools:
            try:
                # check if endpoint is available and returns valid data
                response = requests.get(f"{config['url_base']}/kyve/query/v1beta1/pool/{pool_id}")
                if not response.ok:
                    # todo improve error handling for cases like pool not found
                    return False, response.json()
            except Exception as e:
                return False, e

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        streams: List[Stream] = []

        pools = config.get("pool_ids").split(",")
        start_ids = config.get("start_ids").split(",")

        for pool_id, start_id in zip(pools, start_ids):
            response = requests.get(f"{config['url_base']}/kyve/query/v1beta1/pool/{pool_id}")
            pool_data = response.json().get("pool").get("data")

            config_copy = dict(deepcopy(config))
            config_copy["start_ids"] = int(start_id)
            # add a new stream based on the pool_data
            streams.append(KYVEStream(config=config_copy, pool_data=pool_data))

        return streams
