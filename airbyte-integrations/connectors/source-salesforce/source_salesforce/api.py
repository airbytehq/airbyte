#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import concurrent.futures
import logging
from typing import Any, List, Mapping, Optional, Tuple

import requests  # type: ignore[import]
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.streams.http import HttpClient
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_protocol.models import FailureType, StreamDescriptor
from requests import adapters as request_adapters
from requests.exceptions import RequestException  # type: ignore[import]

from .exceptions import TypeSalesforceException
from .rate_limiting import SalesforceErrorHandler, default_backoff_handler
from .utils import filter_streams_by_criteria

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

PARENT_SALESFORCE_OBJECTS = {
    # parent_name - name of parent stream
    # field - in each parent record, which is needed for stream slice
    # schema_minimal - required for getting proper class name full_refresh/incremental, rest/bulk for parent stream
    "ContentDocumentLink": {
        "parent_name": "ContentDocument",
        "field": "Id",
        "schema_minimal": {
            "properties": {"Id": {"type": ["string", "null"]}, "SystemModstamp": {"type": ["string", "null"], "format": "date-time"}}
        },
    }
}

# The following objects are not supported by the Bulk API. Listed objects are version specific.
UNSUPPORTED_BULK_API_SALESFORCE_OBJECTS = [
    "AcceptedEventRelation",
    "AssetTokenEvent",
    "Attachment",
    "AttachedContentNote",
    "CaseStatus",
    "ContractStatus",
    "DeclinedEventRelation",
    "EventWhoRelation",
    "FieldSecurityClassification",
    "KnowledgeArticle",
    "KnowledgeArticleVersion",
    "KnowledgeArticleVersionHistory",
    "KnowledgeArticleViewStat",
    "KnowledgeArticleVoteStat",
    "OrderStatus",
    "PartnerRole",
    "QuoteTemplateRichTextData",
    "RecentlyViewed",
    "ServiceAppointmentStatus",
    "ShiftStatus",
    "SolutionStatus",
    "TaskPriority",
    "TaskStatus",
    "TaskWhoRelation",
    "UndecidedEventRelation",
    "WorkOrderLineItemStatus",
    "WorkOrderStatus",
    "UserRecordAccess",
    "OwnedContentDocument",
    "OpenActivity",
    "NoteAndAttachment",
    "Name",
    "LookedUpFromActivity",
    "FolderedContentDocument",
    "ContractStatus",
    "ContentFolderItem",
    "CombinedAttachment",
    "CaseTeamTemplateRecord",
    "CaseTeamTemplateMember",
    "CaseTeamTemplate",
    "CaseTeamRole",
    "CaseTeamMember",
    "AttachedContentDocument",
    "AggregateResult",
    "ChannelProgramLevelShare",
    "AccountBrandShare",
    "AccountFeed",
    "AssetFeed",
]

UNSUPPORTED_FILTERING_STREAMS = [
    "ApiEvent",
    "BulkApiResultEventStore",
    "ContentDocumentLink",
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

UNSUPPORTED_STREAMS = ["ActivityMetric", "ActivityMetricRollup"]


class Salesforce:
    logger = logging.getLogger("airbyte")
    version = "v57.0"
    parallel_tasks_size = 100
    # https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/salesforce_app_limits_platform_api.htm
    # Request Size Limits
    REQUEST_SIZE_LIMITS = 16_384

    def __init__(
        self,
        refresh_token: str = None,
        token: str = None,
        client_id: str = None,
        client_secret: str = None,
        is_sandbox: bool = None,
        start_date: str = None,
        **kwargs: Any,
    ) -> None:
        self.refresh_token = refresh_token
        self.token = token
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.instance_url = ""
        self.session = requests.Session()
        # Change the connection pool size. Default value is not enough for parallel tasks
        adapter = request_adapters.HTTPAdapter(pool_connections=self.parallel_tasks_size, pool_maxsize=self.parallel_tasks_size)
        self.session.mount("https://", adapter)
        self._http_client = HttpClient("sf_api", self.logger, session=self.session, error_handler=SalesforceErrorHandler())

        self.is_sandbox = is_sandbox in [True, "true"]
        if self.is_sandbox:
            self.logger.info("using SANDBOX of Salesforce")
        self.start_date = start_date

    def _get_standard_headers(self) -> Mapping[str, str]:
        return {"Authorization": "Bearer {}".format(self.access_token)}

    def get_streams_black_list(self) -> List[str]:
        return QUERY_RESTRICTED_SALESFORCE_OBJECTS + QUERY_INCOMPATIBLE_SALESFORCE_OBJECTS

    def filter_streams(self, stream_name: str) -> bool:
        # REST and BULK API do not support all entities that end with `ChangeEvent`.
        if stream_name.endswith("ChangeEvent") or stream_name in self.get_streams_black_list():
            return False
        return True

    def get_validated_streams(self, config: Mapping[str, Any], catalog: ConfiguredAirbyteCatalog = None) -> Mapping[str, Any]:
        """Selects all validated streams with additional filtering:
        1) skip all sobjects with negative value of the flag "queryable"
        2) user can set search criterias of necessary streams
        3) selection by catalog settings
        """
        stream_objects = {}
        for stream_object in self.describe()["sobjects"]:
            if stream_object["name"] in UNSUPPORTED_STREAMS:
                self.logger.warning(f"Stream {stream_object['name']} can not be used without object ID therefore will be ignored.")
                continue
            if stream_object["queryable"]:
                stream_objects[stream_object.pop("name")] = stream_object
            else:
                self.logger.warning(f"Stream {stream_object['name']} is not queryable and will be ignored.")

        if catalog:
            return {
                configured_stream.stream.name: stream_objects[configured_stream.stream.name]
                for configured_stream in catalog.streams
                if configured_stream.stream.name in stream_objects
            }

        stream_names = list(stream_objects.keys())
        if config.get("streams_criteria"):
            filtered_stream_list = []
            for stream_criteria in config["streams_criteria"]:
                filtered_stream_list += filter_streams_by_criteria(
                    streams_list=stream_names, search_word=stream_criteria["value"], search_criteria=stream_criteria["criteria"]
                )
            stream_names = list(set(filtered_stream_list))

        validated_streams = [stream_name for stream_name in stream_names if self.filter_streams(stream_name)]
        return {stream_name: sobject_options for stream_name, sobject_options in stream_objects.items() if stream_name in validated_streams}

    def _make_request(self, http_method: str, url: str, headers: dict = None, body: dict = None) -> requests.models.Response:
        _, resp = self._http_client.send_request(http_method, url, headers=headers, data=body, request_kwargs={})
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

    def describe(self, sobject: str = None, sobject_options: Mapping[str, Any] = None) -> Mapping[str, Any]:
        """Describes all objects or a specific object"""
        headers = self._get_standard_headers()

        endpoint = "sobjects" if not sobject else f"sobjects/{sobject}/describe"

        url = f"{self.instance_url}/services/data/{self.version}/{endpoint}"
        resp = self._make_request("GET", url, headers=headers)
        if resp.status_code == 404 and sobject:
            self.logger.error(f"not found a description for the sobject '{sobject}'. Sobject options: {sobject_options}")
        resp_json: Mapping[str, Any] = resp.json()
        return resp_json

    def generate_schema(self, stream_name: str = None, stream_options: Mapping[str, Any] = None) -> Mapping[str, Any]:
        response = self.describe(stream_name, stream_options)
        schema = {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "additionalProperties": True, "properties": {}}
        for field in response["fields"]:
            schema["properties"][field["name"]] = self.field_to_property_schema(field)  # type: ignore[index]
        return schema

    def generate_schemas(self, stream_objects: Mapping[str, Any]) -> Mapping[str, Any]:
        def load_schema(name: str, stream_options: Mapping[str, Any]) -> Tuple[str, Optional[Mapping[str, Any]], Optional[str]]:
            try:
                result = self.generate_schema(stream_name=name, stream_options=stream_options)
            except RequestException as e:
                return name, None, str(e)
            return name, result, None

        stream_names = list(stream_objects.keys())
        # try to split all requests by chunks
        stream_schemas = {}
        for i in range(0, len(stream_names), self.parallel_tasks_size):
            chunk_stream_names = stream_names[i : i + self.parallel_tasks_size]
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for stream_name, schema, err in executor.map(
                    lambda args: load_schema(*args), [(stream_name, stream_objects[stream_name]) for stream_name in chunk_stream_names]
                ):
                    if err:
                        self.logger.error(f"Loading error of the {stream_name} schema: {err}")
                        # Without schema information, the source can't determine the type of stream to instantiate and there might be issues
                        # related to property chunking
                        raise AirbyteTracedException(
                            message=f"Schema could not be extracted for stream {stream_name}. Please retry later.",
                            internal_message=str(err),
                            failure_type=FailureType.system_error,
                            stream_descriptor=StreamDescriptor(name=stream_name),
                        )
                    stream_schemas[stream_name] = schema
        return stream_schemas

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
            property_schema = {
                "type": ["string", "null"],
                "format": "date-time" if sf_type == "datetime" else "date",  # type: ignore[dict-item]
            }
        elif sf_type in NUMBER_TYPES:
            property_schema["type"] = ["number", "null"]
        elif sf_type == "address":
            property_schema = {
                "type": ["object", "null"],
                "properties": {  # type: ignore[dict-item]
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
            property_schema = {"type": ["string", "null"], "format": "base64"}  # type: ignore[dict-item]
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
                "properties": {  # type: ignore[dict-item]
                    "longitude": {"type": ["null", "number"]},
                    "latitude": {"type": ["null", "number"]},
                },
            }
        else:
            raise TypeSalesforceException("Found unsupported type: {}".format(sf_type))

        return property_schema
