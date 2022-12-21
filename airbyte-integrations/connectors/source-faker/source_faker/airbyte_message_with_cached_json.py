#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.models import AirbyteMessage


class AirbyteMessageWithCachedJSON(AirbyteMessage):
    """I a monkeypatch to AirbyteMessage which pre-renders the JSON-representation of the object upon initialization.  This allows the JSON to be calculated in the thread/process that builds the object rather than the main thread."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._json = self.json(exclude_unset=True)
        self.json = self.get_json

    def get_json(self, **kwargs):
        return self._json
