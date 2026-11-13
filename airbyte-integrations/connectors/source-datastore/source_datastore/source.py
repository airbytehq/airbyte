#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import json
import logging
from typing import Any, List, Mapping, Optional, Tuple

from google.cloud import datastore
from google.oauth2 import service_account

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_datastore.streams import DatastoreStream


def _build_client(config: Mapping[str, Any]) -> datastore.Client:
    credentials_info = json.loads(config["credentials_json"])
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=["https://www.googleapis.com/auth/datastore"],
    )
    namespace = config.get("namespace") or None
    return datastore.Client(
        project=config["project_id"],
        credentials=credentials,
        namespace=namespace,
    )


class SourceDatastore(AbstractSource):
    logger = logging.getLogger("airbyte")

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        try:
            client = _build_client(config)
            kinds = config.get("kinds", [])
            if not kinds:
                return False, "At least one Kind must be specified."
            # Run a lightweight query (limit=1) on the first Kind to confirm access
            query = client.query(kind=kinds[0], namespace=config.get("namespace") or None)
            list(query.fetch(limit=1))
            return True, None
        except Exception as e:
            return False, repr(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        client = _build_client(config)
        namespace = config.get("namespace") or None
        return [DatastoreStream(client=client, kind=kind, namespace=namespace) for kind in config["kinds"]]
