#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime
from typing import Any, List, Mapping, MutableMapping, Optional, Tuple, Type

import pendulum
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
from pydantic import BaseModel, Field
from source_facebook_marketing.api import API
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


class InsightConfig(BaseModel):

    name: str = Field(description="The name value of insight")

    fields: Optional[List[str]] = Field(description="A list of chosen fields for fields parameter", default=[])

    breakdowns: Optional[List[str]] = Field(description="A list of chosen breakdowns for breakdowns", default=[])

    action_breakdowns: Optional[List[str]] = Field(description="A list of chosen action_breakdowns for action_breakdowns", default=[])


class ConnectorConfig(BaseModel):
    class Config:
        title = "Source Facebook Marketing"

    account_id: str = Field(description="The Facebook Ad account ID to use when pulling data from the Facebook Marketing API.")

    access_token: str = Field(
        description='The value of the access token generated. See the <a href="https://docs.airbyte.io/integrations/sources/facebook-marketing">docs</a> for more information',
        airbyte_secret=True,
    )

    start_date: datetime = Field(
        description="The date from which you'd like to replicate data for AdCreatives and AdInsights APIs, in the format YYYY-MM-DDT00:00:00Z. All data generated after this date will be replicated.",
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        examples=["2017-01-25T00:00:00Z"],
    )

    end_date: Optional[datetime] = Field(
        description="The date until which you'd like to replicate data for AdCreatives and AdInsights APIs, in the format YYYY-MM-DDT00:00:00Z. All data generated between start_date and this date will be replicated. Not setting this option will result in always syncing the latest data.",
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        examples=["2017-01-26T00:00:00Z"],
        default_factory=pendulum.now,
    )

    include_deleted: bool = Field(default=False, description="Include data from deleted campaigns, ads, and adsets.")

    insights_lookback_window: int = Field(
        default=28,
        description="The attribution window for the actions",
        minimum=0,
        maximum=28,
    )

    insights_days_per_job: int = Field(
        default=7,
        description="Number of days to sync in one job. The more data you have - the smaller you want this parameter to be.",
        minimum=1,
        maximum=30,
    )
    custom_insights: Optional[List[InsightConfig]] = Field(
        description="A list wich contains insights entries, each entry must have a name and can contains fields, breakdowns or action_breakdowns)"
    )


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
            config = ConnectorConfig.parse_obj(config)  # FIXME: this will be not need after we fix CDK
            api = API(account_id=config.account_id, access_token=config.access_token)
            logger.info(f"Select account {api.account}")
            ok = True
        except Exception as exc:
            error_msg = repr(exc)

        return ok, error_msg

    def streams(self, config: Mapping[str, Any]) -> List[Type[Stream]]:
        """Discovery method, returns available streams

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        config: ConnectorConfig = ConnectorConfig.parse_obj(config)  # FIXME: this will be not need after we fix CDK
        api = API(account_id=config.account_id, access_token=config.access_token)

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
            AdCreatives(api=api),
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

        default_fields = list(
            ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("ads_insights").get("properties", {}).keys()
        )
        default_breakdowns = list(
            ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("ads_insights_breakdowns").get("properties", {}).keys()
        )
        default_actions_breakdowns = [e for e in default_breakdowns if "action_" in e]

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
                value_checked, value = self._check_values(default_actions_breakdowns, insight.get("action_breakdowns"))
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
