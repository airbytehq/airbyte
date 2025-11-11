#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import anyascii

from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.types import Config, StreamSlice, StreamState


@dataclass
class KeysToSnakeCaseTransformation(RecordTransformation):
    token_pattern: re.Pattern[str] = re.compile(
        r"[A-Z]+[a-z]*|[a-z]+|\d+|(?P<NoToken>[^a-zA-Z\d]+)"
    )

    def transform(
        self,
        record: Dict[str, Any],
        config: Optional[Config] = None,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
    ) -> None:
        transformed_record = self._transform_record(record)
        record.clear()
        record.update(transformed_record)

    def _transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        transformed_record = {}
        for key, value in record.items():
            transformed_key = self.process_key(key)
            transformed_value = value

            if isinstance(value, dict):
                transformed_value = self._transform_record(value)

            transformed_record[transformed_key] = transformed_value
        return transformed_record

    def process_key(self, key: str) -> str:
        key = self.normalize_key(key)
        tokens = self.tokenize_key(key)
        tokens = self.filter_tokens(tokens)
        return self.tokens_to_snake_case(tokens)

    def normalize_key(self, key: str) -> str:
        return str(anyascii.anyascii(key))

    def tokenize_key(self, key: str) -> List[str]:
        tokens = []
        for match in self.token_pattern.finditer(key):
            token = match.group(0) if match.group("NoToken") is None else ""
            tokens.append(token)
        return tokens

    def filter_tokens(self, tokens: List[str]) -> List[str]:
        if len(tokens) >= 3:
            tokens = tokens[:1] + [t for t in tokens[1:-1] if t] + tokens[-1:]
        if tokens and tokens[0].isdigit():
            tokens.insert(0, "")
        return tokens

    def tokens_to_snake_case(self, tokens: List[str]) -> str:
        return "_".join(token.lower() for token in tokens)
