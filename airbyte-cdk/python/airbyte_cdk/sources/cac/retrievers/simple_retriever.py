#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.cac.iterators.iterator import Iterator
from airbyte_cdk.sources.cac.retrievers.retriever import Retriever
from airbyte_cdk.sources.cac.states.state import State
from airbyte_cdk.sources.streams.http import HttpStream


class SimpleRetriever(Retriever, HttpStream):
    def __init__(self, requester, extractor, iterator, state, vars=None, config=None):
        if vars is None:
            vars = dict()
        if config is None:
            config = dict()
        # print(f"retriever with config: {requester} and {extractor} and {vars} and {config}")

        # FIXME: we should probably share the factory?
        self._requester = requester  # LowCodeComponentFactory().create_component(requester, vars, config)
        self._extractor = extractor  # LowCodeComponentFactory().create_component(extractor, vars, config)
        super().__init__(self._requester.get_authenticator())
        self._iterator: Iterator = iterator  # LowCodeComponentFactory().create_component(iterator, vars, config)
        self._state: State = state  # LowCodeComponentFactory().create_component(state, vars, config)
        self._last_response = None
        self._last_record = None

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
        # FIXME: I think we want the decoded version here
        self._last_response = response
        records = self._extractor.extract_records(response)
        return records

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        # FIXME: TODO
        return "id"

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

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        records = [r for r in HttpStream.read_records(self, sync_mode, cursor_field, stream_slice, stream_state)]
        for r in records:
            self._state.update_state(stream_slice, stream_state, self._last_response, r)
        if not records:
            # FIXME?
            self._state.update_state(stream_slice, stream_state, self._last_response, None)
            yield from []
        else:
            yield from records

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Override to define the slices for this stream. See the stream slicing section of the docs for more information.

        :param sync_mode:
        :param cursor_field:
        :param stream_state:
        :return:
        """
        # FIXME: this is not passing the cursor field because i think it should be known at init time. Is this always true?
        return self._iterator.stream_slices(sync_mode, stream_state)
