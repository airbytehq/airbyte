#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import requests
from airbyte_cdk.sources.cac.factory import LowCodeComponentFactory
from airbyte_cdk.sources.streams.http import HttpStream


class SimpleRetriever(HttpStream):
    def __init__(self, object_config, parent_vars, config):
        print(f"retriever with config: {object_config}")

        self._requester = LowCodeComponentFactory().build(
            object_config["requester"], self.merge_dicts(object_config.get("vars", {}), parent_vars), config
        )
        self._extractor = LowCodeComponentFactory().build(
            object_config["extractor"], self.merge_dicts(object_config.get("vars", {}), parent_vars), config
        )
        super().__init__(self._requester.get_authenticator())

    @property
    def url_base(self) -> str:
        return self._requester.get_url_base()

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        pass

    def path(
        self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return self._requester.get_path()

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        print(f"received response: {response}")
        return self._extractor.extract_records(response)

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        pass

    def merge_dicts(self, d1, d2):
        return {**d1, **d2}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        """
        Override this method to define the query parameters that should be set on an outgoing HTTP request given the inputs.

        E.g: you might want to define query parameters for paging if next_page_token is not None.
        """
        return {}

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """
        Override to return any non-auth headers. Authentication headers will overwrite any overlapping headers returned from this method.
        """
        return {}
