#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_emarsys.streams import (
    Contacts,
    ContactListMemberships,
    ContactLists,
    EmarsysAuthenticator,
    Fields,
    Segments,
)


class SourceEmarsys(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Check connection by listing all Emarsys fields.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        auth = EmarsysAuthenticator(config["username"], config["password"])
        url = "https://api.emarsys.net/api/v2/field"
        try:
            response = requests.get(
                url, auth=auth, headers={"Content-Type": "application/json", "Accept": "application/json"}
            )
            fields = response.json()["data"]
            if not fields:
                logger.error("Got no Emarsys fields")
                return False, None

            field_dict = set(field["string_id"] for field in fields)
            logger.info("Fetched available fields")
            for required_field in config["contact_fields"]:
                if required_field not in field_dict:
                    raise ValueError(f"Required field `{required_field}` does not exist in Emarsys")

            return True, None
        except Exception as exc:
            logger.exception(exc)
            return False, exc

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Emarsys streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = EmarsysAuthenticator(config["username"], config["password"])
        contact_lists_stream = ContactLists(authenticator=auth)
        return [
            Fields(authenticator=auth),
            Segments(authenticator=auth),
            contact_lists_stream,
            ContactListMemberships(authenticator=auth, parent=contact_lists_stream, limit=config["limit"]),
            Contacts(
                authenticator=auth,
                parent=contact_lists_stream,
                fields=config["contact_fields"],
                limit=config["limit"],
                recur_list_patterns=config["recurring_contact_lists"],
            ),
        ]
