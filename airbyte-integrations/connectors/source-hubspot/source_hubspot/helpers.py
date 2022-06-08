#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import abc
from typing import MutableMapping


class IRecordPostProcessor(abc.ABC):
    @abc.abstractmethod
    def add_record(self, record: MutableMapping, primary_key: str = None):
        """"""

    @property
    @abc.abstractmethod
    def flat(self):
        """"""


class GroupByKey(IRecordPostProcessor):
    def __init__(self):
        self._storage = {}

    def add_record(self, record: MutableMapping, primary_key: str = None):
        record_pk = record[primary_key]
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

    def add_record(self, record: MutableMapping, primary_key: str = None):
        self._storage.append(record)

    @property
    def flat(self):
        return self._storage
