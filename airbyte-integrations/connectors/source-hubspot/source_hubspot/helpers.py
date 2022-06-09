#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import abc
from typing import MutableMapping


class IRecordPostProcessor(abc.ABC):
    """
    The interface is designed to post process records (like group them by ID and update) after the API response is parsed and
    before they are emitted up the stack.
    """

    @abc.abstractmethod
    def add_record(self, record: MutableMapping):
        """"""

    @property
    @abc.abstractmethod
    def flat(self):
        """"""


class GroupByKey(IRecordPostProcessor):
    def __init__(self, primary_key: str = None):
        self._storage = {}
        self._primary_key = primary_key

    def add_record(self, record: MutableMapping):
        record_pk = record[self._primary_key]
        if record_pk not in self._storage:
            self._storage[record_pk] = record
        stored_props = self._storage[record_pk].get("properties")
        if stored_props:
            stored_props.update(record.get("properties", {}))
            self._storage[record_pk]["properties"] = stored_props

    @property
    def flat(self):
        return list(self._storage.values())


class StoreAsIs(IRecordPostProcessor):
    def __init__(self):
        self._storage = []

    def add_record(self, record: MutableMapping):
        self._storage.append(record)

    @property
    def flat(self):
        return self._storage
