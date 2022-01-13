#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping, MutableMapping, Tuple, Type

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AuthSpecification,
    ConnectorSpecification,
    DestinationSyncMode,
    OAuth2Specification,
    Status,
)
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from jsonschema import RefResolver
from source_facebook_marketing.api import API
from source_facebook_marketing.common import ConnectorConfig
from source_facebook_marketing.streams import (
    AdCreatives,
    Ads,
    AdSets,
    AdsInsights,
    AdsInsightsActionType,
    AdsInsightsAgeAndGender,
    AdsInsightsCountry,
    AdsInsightsDma,
    AdsInsightsPlatformAndDevice,
    AdsInsightsRegion,
    Campaigns,
    Videos,
)

logger = logging.getLogger("airbyte")

class SourceFacebookMarketing(AbstractSource):
    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """Connection check to validate that the user-provided config can be used to connect to the underlying API

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, Any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        ok = False
        error_msg = None

        try:
            config = ConnectorConfig(**config)
            api = API(config)
            account_ids = {str(account["account_id"]) for account in api.accounts}

            if config.account_selection_strategy_is_subset:
                config_account_ids = set(config.accounts.ids)
                if not config_account_ids.issubset(account_ids):
                    raise Exception(f"Account Ids: {config_account_ids.difference(account_ids)} not found on this user.")
            elif config.account_selection_strategy_is_all:
                if not account_ids:
                    raise Exception("You don't have accounts assigned to this user.")
            else:
                raise Exception("Incorrect account selection strategy.")

            ok = True
        except Exception as exc:
            error_msg = repr(exc)

        return ok, error_msg

    def streams(self, config: Mapping[str, Any]) -> List[Type[Stream]]:
        """Discovery method, returns available streams

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        config = ConnectorConfig(**config)
        api = API(config)

        insights_args = dict(
            api=api,
            start_date=config.start_date,
            end_date=config.end_date,
            buffer_days=config.insights_lookback_window,
            days_per_job=config.insights_days_per_job,
        )

        streams = [
            Campaigns(api=api, start_date=config.start_date, end_date=config.end_date, include_deleted=config.include_deleted),
            AdSets(api=api, start_date=config.start_date, end_date=config.end_date, include_deleted=config.include_deleted),
            Ads(api=api, start_date=config.start_date, end_date=config.end_date, include_deleted=config.include_deleted),
            AdCreatives(api=api, fetch_thumbnail_images=config.fetch_thumbnail_images),
            AdsInsights(**insights_args),
            AdsInsightsAgeAndGender(**insights_args),
            AdsInsightsCountry(**insights_args),
            AdsInsightsRegion(**insights_args),
            AdsInsightsDma(**insights_args),
            AdsInsightsPlatformAndDevice(**insights_args),
            AdsInsightsActionType(**insights_args),
            Videos(api=api, start_date=config.start_date, end_date=config.end_date, include_deleted=config.include_deleted),
        ]

        return self._update_insights_streams(insights=config.custom_insights, args=insights_args, streams=streams)

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """Implements the Check Connection operation from the Airbyte Specification. See https://docs.airbyte.io/architecture/airbyte-specification."""
        try:
            check_succeeded, error = self.check_connection(logger, config)
            if not check_succeeded:
                return AirbyteConnectionStatus(status=Status.FAILED, message=repr(error))
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=repr(e))

        self._check_custom_insights_entries(config.get("custom_insights", []))

        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def spec(self, *args, **kwargs) -> ConnectorSpecification:
        """
        Returns the spec for this integration. The spec is a JSON-Schema object describing the required configurations (e.g: username and password)
        required to run this integration.
        """
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.io/integrations/sources/facebook-marketing",
            changelogUrl="https://docs.airbyte.io/integrations/sources/facebook-marketing",
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.append],
            connectionSpecification=expand_local_ref(ConnectorConfig.schema()),
            authSpecification=AuthSpecification(
                auth_type="oauth2.0",
                oauth2Specification=OAuth2Specification(
                    rootObject=[], oauthFlowInitParameters=[], oauthFlowOutputParameters=[["access_token"]]
                ),
            ),
        )

    def _update_insights_streams(self, insights, args, streams) -> List[Type[Stream]]:
        """Update method, if insights have values returns streams replacing the
        default insights streams else returns streams

        """
        if not insights:
            return streams

        insights_custom_streams = list()

        for insight in insights:
            args["name"] = f"Custom{insight.name}"
            args["fields"] = list(set(insight.fields))
            args["breakdowns"] = list(set(insight.breakdowns))
            args["action_breakdowns"] = list(set(insight.action_breakdowns))
            insight_stream = AdsInsights(**args)
            insights_custom_streams.append(insight_stream)

        return streams + insights_custom_streams

    def _check_custom_insights_entries(self, insights: List[Mapping[str, Any]]):

        loader = ResourceSchemaLoader(package_name_from_class(self.__class__))
        default_fields = list(loader.get_schema("ads_insights").get("properties", {}).keys())
        default_breakdowns = list(loader.get_schema("ads_insights_breakdowns").get("properties", {}).keys())
        default_action_breakdowns = list(loader.get_schema("ads_insights_action_breakdowns").get("properties", {}).keys())

        for insight in insights:
            if insight.get("fields"):
                value_checked, value = self._check_values(default_fields, insight.get("fields"))
                if not value_checked:
                    message = f"{value} is not a valid field name"
                    raise Exception("Config validation error: " + message) from None
            if insight.get("breakdowns"):
                value_checked, value = self._check_values(default_breakdowns, insight.get("breakdowns"))
                if not value_checked:
                    message = f"{value} is not a valid breakdown name"
                    raise Exception("Config validation error: " + message) from None
            if insight.get("action_breakdowns"):
                value_checked, value = self._check_values(default_action_breakdowns, insight.get("action_breakdowns"))
                if not value_checked:
                    message = f"{value} is not a valid action_breakdown name"
                    raise Exception("Config validation error: " + message) from None

        return True

    def _check_values(self, default_value: List[str], custom_value: List[str]) -> Tuple[bool, Any]:
        for e in custom_value:
            if e not in default_value:
                logger.error(f"{e} does not appear in {default_value}")
                return False, e

        return True, None


def expand_local_ref(schema, resolver=None, **kwargs):
    resolver = resolver or RefResolver("", schema)
    if isinstance(schema, MutableMapping):
        if "$ref" in schema:
            ref_url = schema.pop("$ref")
            url, resolved_schema = resolver.resolve(ref_url)
            schema.update(resolved_schema)
        for key, value in schema.items():
            schema[key] = expand_local_ref(value, resolver=resolver)
        return schema
    elif isinstance(schema, List):
        return [expand_local_ref(item, resolver=resolver) for item in schema]

    return schema
