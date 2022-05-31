#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


class SourceSendgrid(YamlDeclarativeSource):
    """
    This is a sample low-code connector.
    It still uses the existing spec.yaml file
    """

    def __init__(self):
        super().__init__(**{"path_to_yaml": "./source_sendgrid/sg.yaml"})


"""
class SourceSendgrid(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            authenticator = TokenAuthenticator(config["apikey"])
            scopes_gen = Scopes(authenticator=authenticator).read_records(sync_mode=SyncMode.full_refresh)
            next(scopes_gen)
            return True, None
        except Exception as error:
            return False, f"Unable to connect to Sendgrid API with the provided credentials - {error}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = TokenAuthenticator(config["apikey"])

        streams = [
            Lists(authenticator=authenticator),
            Campaigns(authenticator=authenticator),
            Contacts(authenticator=authenticator),
            StatsAutomations(authenticator=authenticator),
            Segments(authenticator=authenticator),
            SingleSends(authenticator=authenticator),
            Templates(authenticator=authenticator),
            GlobalSuppressions(authenticator=authenticator, start_time=config["start_time"]),
            SuppressionGroups(authenticator=authenticator),
            SuppressionGroupMembers(authenticator=authenticator),
            Blocks(authenticator=authenticator, start_time=config["start_time"]),
            Bounces(authenticator=authenticator, start_time=config["start_time"]),
            InvalidEmails(authenticator=authenticator, start_time=config["start_time"]),
            SpamReports(authenticator=authenticator, start_time=config["start_time"]),
        ]

        return streams
"""
