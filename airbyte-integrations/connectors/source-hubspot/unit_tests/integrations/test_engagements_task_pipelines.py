# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import copy
import json

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template

from . import HubspotTestCase
from .request_builders.streams import EngagementsTaskPipelinesStreamRequestBuilder


@freezegun.freeze_time("2024-03-03T14:42:00Z")
class TestEngagementsTaskPipelinesStream(HubspotTestCase):
    """The stream exists so `engagements_tasks.properties.hs_pipeline_stage` can be resolved to a
    stage label and an open/closed state, so the tests pin the shape of that join key.
    """

    SCOPES = ["crm.objects.contacts.read"]
    CURSOR_FIELD = "updatedAt"
    STREAM_NAME = "engagements_task_pipelines"

    def request(self):
        return EngagementsTaskPipelinesStreamRequestBuilder()

    def response(self) -> HttpResponse:
        # The stream is client-side incremental, so the pipeline has to be newer than the
        # config's start date or the cursor filters it out before it reaches the output.
        body = copy.deepcopy(find_template(self.STREAM_NAME, __file__))
        body["results"][0][self.CURSOR_FIELD] = self.dt_str(self.updated_at())
        return HttpResponse(json.dumps(body), 200)

    @HttpMocker()
    def test_when_read_stream_oauth_then_return_records(self, http_mocker: HttpMocker):
        self.mock_oauth(http_mocker, self.ACCESS_TOKEN)
        self.mock_custom_objects(http_mocker)
        self.mock_response(http_mocker, self.request().build(), self.response())

        output = self.read_from_stream(self.oauth_config(), self.STREAM_NAME, SyncMode.full_refresh)

        assert len(output.records) == 1
        assert output.records[0].record.data["label"] == "Task Pipeline"

    @HttpMocker()
    def test_when_read_stream_private_token_then_stages_are_nested_with_string_ids(self, http_mocker: HttpMocker):
        """HubSpot's default task stages use UUIDs while stages added later in the UI get numeric
        ids. Both must stay strings: `hs_pipeline_stage` on a task is always a string, so a numeric
        stage id coerced to an integer here would silently break the join.
        """
        self.mock_custom_objects(http_mocker)
        self.mock_response(http_mocker, self.request().build(), self.response())

        output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), self.STREAM_NAME, SyncMode.full_refresh)

        stages = output.records[0].record.data["stages"]
        assert [stage["id"] for stage in stages] == [
            "af0e6a5c-2ea3-4c72-b69f-7c6cb3fdb591",
            "5996831934",
            "dd5826e4-c976-4654-a527-b59ada542e52",
            "61bafb31-e7fa-46ed-aaa9-1322438d6e67",
            "fc8148fb-3a2d-4b59-834e-69b7859347cb",
            "6049725638",
        ]
        assert all(isinstance(stage["id"], str) for stage in stages)

    @HttpMocker()
    def test_when_read_stream_then_stage_metadata_is_preserved(self, http_mocker: HttpMocker):
        """The open/closed flag lives on the stage definition, not on the task record, and HubSpot
        returns it as a string rather than a native boolean.
        """
        self.mock_custom_objects(http_mocker)
        self.mock_response(http_mocker, self.request().build(), self.response())

        output = self.read_from_stream(self.private_token_config(self.ACCESS_TOKEN), self.STREAM_NAME, SyncMode.full_refresh)

        stages = output.records[0].record.data["stages"]
        by_label = {stage["label"]: stage["metadata"] for stage in stages}
        assert by_label["Not Started"] == {"isClosed": "false", "state": "OPEN"}
        assert by_label["Completed"] == {"isClosed": "true", "state": "CLOSED"}
