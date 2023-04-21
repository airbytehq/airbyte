#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

from .streams import AlertLogs, AlertRecipients, Alerts, Incidents, Integrations, Services, Teams, Users, UserTeams


# Source
class SourceOpsgenie(AbstractSource):
    @staticmethod
    def get_authenticator(config: Mapping[str, Any]):
        return TokenAuthenticator(config["api_token"], auth_method="GenieKey")

    def check_connection(self, logger, config) -> Tuple[bool, any]:

        try:
            auth = self.get_authenticator(config)
            api_endpoint = f"https://{config['endpoint']}/v2/account"

            response = requests.get(
                api_endpoint,
                headers=auth.get_auth_header(),
            )

            return response.status_code == requests.codes.ok, None

        except Exception as error:
            return False, f"Unable to connect to Opsgenie API with the provided credentials - {repr(error)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self.get_authenticator(config)
        args = {"authenticator": auth, "endpoint": config["endpoint"]}
        incremental_args = {**args, "start_date": config.get("start_date", "")}

        users = Users(**args)
        alerts = Alerts(**incremental_args)
        return [
            alerts,
            AlertRecipients(parent_stream=alerts, **args),
            AlertLogs(parent_stream=alerts, **args),
            Incidents(**incremental_args),
            Integrations(**args),
            Services(**args),
            Teams(**args),
            users,
            UserTeams(parent_stream=users, **args),
        ]
