#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.models import AirbyteMessage


class AirbyteMessageWithCachedJSON(AirbyteMessage):
    """
    I a monkeypatch to AirbyteMessage which pre-renders the JSON-representation of the object upon initialization.
    This allows the JSON to be calculated in the process that builds the object rather than the main process.

    Note: We can't use @cache here because the LRU cache is not serializable when passed to child workers.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._json = self.json(exclude_unset=True)
        self.json = self.get_json

    def get_json(self, **kwargs):
        return self._json
