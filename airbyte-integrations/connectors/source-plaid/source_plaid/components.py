from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping

import requests

from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor


@dataclass
class PlaidTransactionExtractor(RecordExtractor):
    """
    Record extractor that searches a decoded response over multiple paths. Each field is
    a separate path that points to an array (unless it doesn't exist at all).

    If the field path points to an array, that array is returned.
    If the field path points to a non-existing path, an empty array is returned.

    Examples of instantiating this transform:
    ```
      extractor:
        type: CustomRecordExtractor
        class_name: source_plaid.components.PlaidTransactionExtractor
        field_path:
          - "added"
          - "modified"
    ```

    Attributes:
        field_path (list[str]): Path to the fields that should be extracted
        decoder (Decoder): The decoder responsible to transfom the response in a Mapping
    """

    field_path: list[str]
    decoder: Decoder = field(default_factory=lambda: JsonDecoder(parameters={}))

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        body = self.decoder.decode(response)
        for path in self.field_path:
            extracted = body.get(path, [])
            yield from extracted
