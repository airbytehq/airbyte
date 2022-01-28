#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional, Tuple

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from requests.exceptions import HTTPError

from .exceptions import TypeSalesforceException
from .rate_limiting import default_backoff_handler
from .utils import filter_streams

STRING_TYPES = [
    "byte",
    "combobox",
    "complexvalue",
    "datacategorygroupreference",
    "email",
    "encryptedstring",
    "id",
    "json",
    "masterrecord",
    "multipicklist",
    "phone",
    "picklist",
    "reference",
    "string",
    "textarea",
    "time",
    "url",
]
NUMBER_TYPES = ["currency", "double", "long", "percent"]
DATE_TYPES = ["date", "datetime"]
LOOSE_TYPES = [
    "anyType",
    # A calculated field's type can be any of the supported
    # formula data types (see https://developer.salesforce.com/docs/#i1435527)
    "calculated",
]

# The following objects have certain WHERE clause restrictions so we exclude them.
QUERY_RESTRICTED_SALESFORCE_OBJECTS = [
    "Announcement",
    "AppTabMember",
    "CollaborationGroupRecord",
    "ColorDefinition",
    "ContentDocumentLink",
    "ContentFolderItem",
    "ContentFolderMember",
    "DataStatistics",
    "DatacloudDandBCompany",
    "EntityParticle",
    "FieldDefinition",
    "FieldHistoryArchive",
    "FlexQueueItem",
    "FlowVariableView",
    "FlowVersionView",
    "IconDefinition",
    "IdeaComment",
    "NetworkUserHistoryRecent",
    "OwnerChangeOptionInfo",
    "PicklistValueInfo",
    "PlatformAction",
    "RelationshipDomain",
    "RelationshipInfo",
    "SearchLayout",
    "SiteDetail",
    "UserEntityAccess",
    "UserFieldAccess",
    "Vote",
]

# The following objects are not supported by the query method being used.
QUERY_INCOMPATIBLE_SALESFORCE_OBJECTS = [
    "AIPredictionEvent",
    "ActivityHistory",
    "AggregateResult",
    "ApiAnomalyEvent",
    "ApiEventStream",
    "AssetTokenEvent",
    "AsyncOperationEvent",
    "AsyncOperationStatus",
    "AttachedContentDocument",
    "AttachedContentNote",
    "BatchApexErrorEvent",
    "BulkApiResultEvent",
    "CombinedAttachment",
    "ConcurLongRunApexErrEvent",
    "ContentBody",
    "CredentialStuffingEvent",
    "DataType",
    "DatacloudAddress",
    "EmailStatus",
    "FeedLike",
    "FeedSignal",
    "FeedTrackedChange",
    "FlowExecutionErrorEvent",
    "FolderedContentDocument",
    "LightningUriEventStream",
    "ListViewChartInstance",
    "ListViewEventStream",
    "LoginAsEventStream",
    "LoginEventStream",
    "LogoutEventStream",
    "LookedUpFromActivity",
    "Name",
    "NoteAndAttachment",
    "OpenActivity",
    "OrgLifecycleNotification",
    "OutgoingEmail",
    "OutgoingEmailRelation",
    "OwnedContentDocument",
    "PlatformStatusAlertEvent",
    "ProcessExceptionEvent",
    "ProcessInstanceHistory",
    "QuoteTemplateRichTextData",
    "RemoteKeyCalloutEvent",
    "ReportAnomalyEvent",
    "ReportEventStream",
    "SessionHijackingEvent",
    "UriEventStream",
    "UserRecordAccess",
]

UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS = [
    "AcceptedEventRelation",
    "AssetTokenEvent",
    "AttachedContentNote",
    "Attachment",
    "CaseStatus",
    "ContractStatus",
    "DeclinedEventRelation",
    "EventWhoRelation",
    "FieldSecurityClassification",
    "OrderStatus",
    "PartnerRole",
    "QuoteTemplateRichTextData",
    "RecentlyViewed",
    "ServiceAppointmentStatus",
    "SolutionStatus",
    "TaskPriority",
    "TaskStatus",
    "TaskWhoRelation",
    "UndecidedEventRelation",
]

UNSUPPORTED_FILTERING_STREAMS = [
    "ApiEvent",
    "BulkApiResultEventStore",
    "EmbeddedServiceDetail",
    "EmbeddedServiceLabel",
    "FormulaFunction",
    "FormulaFunctionAllowedType",
    "FormulaFunctionCategory",
    "IdentityProviderEventStore",
    "IdentityVerificationEvent",
    "LightningUriEvent",
    "ListViewEvent",
    "LoginAsEvent",
    "LoginEvent",
    "LogoutEvent",
    "Publisher",
    "RecordActionHistory",
    "ReportEvent",
    "TabDefinition",
    "UriEvent",
]


class Salesforce:
    logger = AirbyteLogger()
    version = "v52.0"

    def __init__(
        self,
        refresh_token: str = None,
        token: str = None,
        client_id: str = None,
        client_secret: str = None,
        is_sandbox: bool = None,
        start_date: str = None,
        **kwargs,
    ):
        self.refresh_token = refresh_token
        self.token = token
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.instance_url = None
        self.session = requests.Session()
        self.is_sandbox = is_sandbox is True or (isinstance(is_sandbox, str) and is_sandbox.lower() == "true")
        self.start_date = start_date

    def _get_standard_headers(self):
        return {"Authorization": "Bearer {}".format(self.access_token)}

    def get_streams_black_list(self) -> List[str]:
        return QUERY_RESTRICTED_SALESFORCE_OBJECTS + QUERY_INCOMPATIBLE_SALESFORCE_OBJECTS

    def filter_streams(self, stream_name: str) -> bool:
        # REST and BULK API do not support all entities that end with `ChangeEvent`.
        if stream_name.endswith("ChangeEvent") or stream_name in self.get_streams_black_list():
            return False
        return True

    def get_validated_streams(self, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog = None):
        salesforce_objects = self.describe()["sobjects"]
        stream_objects = []
        for stream_object in salesforce_objects:
            if stream_object["queryable"]:
                stream_objects.append(stream_object)
            else:
                self.logger.warn(f"Stream {stream_object['name']} is not queryable and will be ignored.")

        stream_names = [stream_object["name"] for stream_object in stream_objects]
        if catalog:
            return [configured_stream.stream.name for configured_stream in catalog.streams], stream_objects

        if config.get("streams_criteria"):
            filtered_stream_list = []
            for stream_criteria in config["streams_criteria"]:
                filtered_stream_list += filter_streams(
                    streams_list=stream_names, search_word=stream_criteria["value"], search_criteria=stream_criteria["criteria"]
                )
            stream_names = list(set(filtered_stream_list))

        validated_streams = [stream_name for stream_name in stream_names if self.filter_streams(stream_name)]
        validated_stream_objects = [stream_object for stream_object in stream_objects if stream_object["name"] in validated_streams]
        return validated_streams, validated_stream_objects

    @default_backoff_handler(max_tries=5, factor=15)
    def _make_request(
        self, http_method: str, url: str, headers: dict = None, body: dict = None, stream: bool = False, params: dict = None
    ) -> requests.models.Response:
        try:
            if http_method == "GET":
                resp = self.session.get(url, headers=headers, stream=stream, params=params)
            elif http_method == "POST":
                resp = self.session.post(url, headers=headers, data=body)
            resp.raise_for_status()
        except HTTPError as err:
            self.logger.warn(f"http error body: {err.response.text}")
            raise
        return resp

    def login(self):
        login_url = f"https://{'test' if self.is_sandbox else 'login'}.salesforce.com/services/oauth2/token"
        login_body = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
        }

        resp = self._make_request("POST", login_url, body=login_body, headers={"Content-Type": "application/x-www-form-urlencoded"})

        auth = resp.json()
        self.access_token = auth["access_token"]
        self.instance_url = auth["instance_url"]

    def describe(self, sobject: str = None, stream_objects: List = None) -> Mapping[str, Any]:
        """Describes all objects or a specific object"""
        headers = self._get_standard_headers()

        endpoint = "sobjects" if not sobject else f"sobjects/{sobject}/describe"

        url = f"{self.instance_url}/services/data/{self.version}/{endpoint}"
        resp = self._make_request("GET", url, headers=headers)
        if resp.status_code == 404:
            self.logger.error(f"Filtered stream objects: {stream_objects}")
        return resp.json()

    def generate_schema(self, stream_name: str = None, stream_objects: List = None) -> Mapping[str, Any]:
        response = self.describe(stream_name, stream_objects)
        schema = {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "additionalProperties": True, "properties": {}}
        for field in response["fields"]:
            schema["properties"][field["name"]] = self.field_to_property_schema(field)
        return schema

    @staticmethod
    def get_pk_and_replication_key(json_schema: Mapping[str, Any]) -> Tuple[Optional[str], Optional[str]]:
        fields_list = json_schema.get("properties", {}).keys()

        pk = "Id" if "Id" in fields_list else None
        replication_key = None
        if "SystemModstamp" in fields_list:
            replication_key = "SystemModstamp"
        elif "LastModifiedDate" in fields_list:
            replication_key = "LastModifiedDate"
        elif "CreatedDate" in fields_list:
            replication_key = "CreatedDate"
        elif "LoginTime" in fields_list:
            replication_key = "LoginTime"

        return pk, replication_key

    @staticmethod
    def field_to_property_schema(field_params: Mapping[str, Any]) -> Mapping[str, Any]:
        sf_type = field_params["type"]
        property_schema = {}

        if sf_type in STRING_TYPES:
            property_schema["type"] = ["string", "null"]
        elif sf_type in DATE_TYPES:
            property_schema = {"type": ["string", "null"], "format": "date-time" if sf_type == "datetime" else "date"}
        elif sf_type in NUMBER_TYPES:
            property_schema["type"] = ["number", "null"]
        elif sf_type == "address":
            property_schema = {
                "type": ["object", "null"],
                "properties": {
                    "street": {"type": ["null", "string"]},
                    "state": {"type": ["null", "string"]},
                    "postalCode": {"type": ["null", "string"]},
                    "city": {"type": ["null", "string"]},
                    "country": {"type": ["null", "string"]},
                    "longitude": {"type": ["null", "number"]},
                    "latitude": {"type": ["null", "number"]},
                    "geocodeAccuracy": {"type": ["null", "string"]},
                },
            }
        elif sf_type == "base64":
            property_schema = {"type": ["string", "null"], "format": "base64"}
        elif sf_type == "int":
            property_schema["type"] = ["integer", "null"]
        elif sf_type == "boolean":
            property_schema["type"] = ["boolean", "null"]
        elif sf_type in LOOSE_TYPES:
            """
            LOOSE_TYPES can return data of completely different types (more than 99% of them are `strings`),
            and in order to avoid conflicts in schemas and destinations, we cast this data to the `string` type.
            """
            property_schema["type"] = ["string", "null"]
        elif sf_type == "location":
            property_schema = {
                "type": ["object", "null"],
                "properties": {"longitude": {"type": ["null", "number"]}, "latitude": {"type": ["null", "number"]}},
            }
        else:
            raise TypeSalesforceException("Found unsupported type: {}".format(sf_type))

        return property_schema
