from destination_palantir_foundry.foundry_api.service import FoundryService
from pydantic import RootModel, BaseModel
from foundry._core.auth_utils import Auth
from typing import Dict
from foundry.api_client import RequestInfo


STREAM_PROXY = "stream-proxy"


PutJsonRecordRequest = RootModel[Dict]


class OffsetAndPartitionId(BaseModel):
    offset: int
    partitionId: int


class StreamProxy:
    def __init__(self, foundry_host: str, api_auth: Auth) -> None:
        self.api_client = FoundryService(
            foundry_host, api_auth, STREAM_PROXY)

    def put_json_record(self, dataset_rid: str, record: Dict) -> None:
        put_json_record_request = RequestInfo(
            method="POST",
            resource_path="/streams/{datasetRid}/branches/master/jsonRecord",
            response_type=OffsetAndPartitionId,
            query_params={},
            path_params={
                "dataset_rid": dataset_rid
            },
            body_type=PutJsonRecordRequest,
            body=record
        )

        return self.api_client.call_api(put_json_record_request)
