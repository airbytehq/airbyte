from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from deepset_cloud_sdk.workflows.sync_client.files import upload_bytes

from airbyte_cdk.models import AirbyteMessage
from destination_deepset.models import DeepsetCloudFileBytes, DeepsetConfig


class Writer:
    def __init__(self, config: Mapping[str, Any]) -> None:
        self.config: DeepsetConfig = DeepsetConfig.parse_obj(config)

    def write(self, messages: Iterable[AirbyteMessage]) -> Iterable[AirbyteMessage]:
        files = [DeepsetCloudFileBytes.from_message(message) for message in messages]
        upload_bytes(
            files=files,
            api_key=self.config.api_key,
            api_url=self.config.base_url,
            workspace_name=self.config.workspace,
            write_mode=self.config.write_mode.value,
            blocking=self.config.sync,
        )
        # @todo[abraham]: report which files failed giving airbyte a chance to retry them
        return []
