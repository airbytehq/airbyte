from datetime import datetime
from typing import Any, Mapping, Tuple, List
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from .authenticator import GoogleAdManagerAuthenticator
from .streams import AdUnitPerHourReportStream, AdUnitPerReferrerReportStream
from .utils import convert_time_to_dict

APPLICATION_NAME = 'spiny'


class SourceGoogleAdManager(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        this check if the connector can connect to the google ad manager api with the credentials provided by the user
        """
        try:
            config.pop("customer_name")
            google_ad_manager_authenticator = self._get_authenticator(config=config)
            networks = google_ad_manager_authenticator.get_networks()
            for network in networks:
                logger.info(f"Network with network code {network['networkCode']} and display name {network['displayName']} was found. at the following timezone {network['timeZone']}")
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        customer_name = config.pop("customer_name")
        start_date = config.pop("start_date")
        timezone = config.pop("timezone")
        google_ad_manager_authenticator = self._get_authenticator(config=config)
        google_ad_manager_client = google_ad_manager_authenticator.get_client()
        ad_unit_per_hour_report_stream = AdUnitPerHourReportStream(google_ad_manager_client=google_ad_manager_client,
                                                                   customer_name=customer_name,
                                                                   start_date=start_date,
                                                                   timezone=timezone)
        ad_unit_per_referrer_report_stream = AdUnitPerReferrerReportStream(google_ad_manager_client=google_ad_manager_client,
                                                                           customer_name=customer_name,
                                                                           start_date=start_date,
                                                                           timezone=timezone)
        return [ad_unit_per_hour_report_stream, ad_unit_per_referrer_report_stream]

    def _get_authenticator(self, config: Mapping[str, Any]) -> GoogleAdManagerAuthenticator:
        """Returns an authenticator based on the input config"""
        google_ad_manager_authenticator = GoogleAdManagerAuthenticator(config=config,
                                                                       application_name=APPLICATION_NAME)
        networks = google_ad_manager_authenticator.get_networks()
        google_ad_manager_authenticator.set_network(networks[0])
        return google_ad_manager_authenticator
