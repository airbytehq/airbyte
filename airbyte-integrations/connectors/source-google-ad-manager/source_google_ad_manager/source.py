from typing import Any, Mapping, Tuple, List
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from .authenticator import GoogleAdManagerAuthenticator
from .streams import AdUnitPerHourReportStream, logger


class SourceGoogleAdManager(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        this check if the connector can connect to the google ad manager api with the credentials provided by the user
        """
        try:
            google_ad_manager_authenticator = self._get_authenticator(credentials=config)
            networks = google_ad_manager_authenticator.get_networks()
            for network in networks:
                logger.info('Network with network code "{}" and display name "{}" was found. at the following timezone "{}"'.format(network['networkCode'], network['displayName'], network["timeZone"]))
            return True, None
        except Exception as e:
            return False, e

    def streams(self, credentials: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # TODO remove the authenticator if not required.
        google_ad_manager_authenticator = self._get_authenticator(credentials=credentials)
        google_ad_manager_client = google_ad_manager_authenticator.get_client()
        ad_unit_per_hour_report_stream = AdUnitPerHourReportStream(google_ad_manager_client=google_ad_manager_client)
        return [ad_unit_per_hour_report_stream, ]

    def _get_authenticator(self, credentials: Mapping[str, Any]) -> GoogleAdManagerAuthenticator:
        """Returns an authenticator based on the input config"""
        google_ad_manager_authenticator = GoogleAdManagerAuthenticator(credentials=credentials)
        networks = google_ad_manager_authenticator.get_networks()
        google_ad_manager_authenticator.set_network(networks[0])
        return google_ad_manager_authenticator
