#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import abc
import urllib.parse
from typing import Iterator, List, MutableMapping


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


class IURLPropertyRepresentation(abc.ABC):
    # The value is obtained experimentally, HubSpot allows the URL length up to ~16300 symbols,
    # so it was decided to limit the length of the `properties` parameter to 15000 characters.
    PROPERTIES_PARAM_MAX_LENGTH = 15000

    def __init__(self, properties: List[str]):
        self.properties = properties

    def __bool__(self):
        return bool(self.properties)

    @property
    @abc.abstractmethod
    def as_url_param(self):
        """"""

    @property
    @abc.abstractmethod
    def _term_representation(self):
        """"""

    def split(self) -> Iterator["IURLPropertyRepresentation"]:
        summary_length = 0
        local_properties = []
        for property_ in self.properties:
            current_property_length = len(urllib.parse.quote(self._term_representation.format(property=property_)))
            if current_property_length + summary_length >= self.PROPERTIES_PARAM_MAX_LENGTH:
                yield type(self)(local_properties)
                local_properties = []
                summary_length = 0

            local_properties.append(property_)
            summary_length += current_property_length

        if local_properties:
            yield type(self)(local_properties)

    @property
    def too_many_properties(self) -> bool:
        # Do not iterate over the generator until the end. Here we need to know if it produces more than one record
        generator = self.split()
        _ = next(generator)
        return next(generator, None) is not None


class APIv1Property(IURLPropertyRepresentation):
    _term_representation = "property={property}&"

    def as_url_param(self):
        return {"property": self.properties}


class APIv3Property(IURLPropertyRepresentation):
    _term_representation = "{property},"

    def as_url_param(self):
        return {"properties": ",".join(self.properties)}
