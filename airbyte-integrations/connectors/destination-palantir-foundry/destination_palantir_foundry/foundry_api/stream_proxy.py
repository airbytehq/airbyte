from typing import Dict, List, Any

from foundry._core.auth_utils import Auth
from foundry.api_client import RequestInfo
from pydantic import RootModel, BaseModel

from destination_palantir_foundry.foundry_api.config import REQUEST_TIMEOUT
from destination_palantir_foundry.foundry_api.service import FoundryApiClient, FoundryService

STREAM_PROXY = "stream-proxy"


class PutJsonRecordRequest(BaseModel):
    value: List[Dict[str, Any]]


PutJsonRecordsRequest = RootModel[List[PutJsonRecordRequest]]


class OffsetAndPartitionId(BaseModel):
    offset: int
    partitionId: int


class BatchStreamProxyResponse(BaseModel):
    topic: str
    offsetAndPartitionIds: List[OffsetAndPartitionId]


class StreamProxy(FoundryService):
    def __init__(self, foundry_host: str, api_auth: Auth) -> None:
        self.api_client = FoundryApiClient(
            foundry_host, api_auth, STREAM_PROXY)

    def put_json_records(self, dataset_rid: str, view_rid: str, records: List[Dict[str, Any]]) -> BatchStreamProxyResponse:
        put_json_record_request = RequestInfo(
            method="POST",
            resource_path="/streams/{dataset_rid}/views/{view_rid}/jsonRecords",
            response_type=BatchStreamProxyResponse,
            query_params={},
            path_params={
                "dataset_rid": dataset_rid,
                "view_rid": view_rid
            },
            header_params={},
            body_type=PutJsonRecordsRequest,
            body=[PutJsonRecordRequest(value=record) for record in records],
            request_timeout=REQUEST_TIMEOUT,
        )

        return self.api_client.call_api(put_json_record_request)
