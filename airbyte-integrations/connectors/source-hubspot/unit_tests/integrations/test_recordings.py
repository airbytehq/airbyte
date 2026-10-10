# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import http
import json
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import freezegun
import mock
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse

from . import HubspotTestCase


SEARCH_URL = "https://api.hubapi.com/crm/v3/objects/{entity}/search"
HUBSPOT_RECORDING_URL = "https://api.hubapi.com/engagements/v1/engagements/recordings/{id}"
UPDATED_AT = "2024-03-02T10:00:00.000Z"


@pytest.fixture(autouse=True)
def files_directory(tmp_path):
    with mock.patch(
        "airbyte_cdk.sources.declarative.retrievers.file_uploader.default_file_uploader.get_files_directory",
        return_value=str(tmp_path),
    ):
        yield tmp_path


@freezegun.freeze_time("2024-03-03T14:42:00Z")
class RecordingsStreamTestCase(HubspotTestCase):
    STREAM_NAME: str
    ENTITY: str
    RECORDING_PROPERTIES: List[str]

    @classmethod
    def start_date(cls):
        # Keep the sync within a single 30-day slice.
        return cls.now() - timedelta(days=5)

    def _ms(self, dt) -> int:
        return int(dt.timestamp() * 1000)

    def _filters(self, recording_property: str, id_floor: int) -> List[Dict[str, Any]]:
        return [
            {"propertyName": recording_property, "operator": "HAS_PROPERTY"},
            {"propertyName": "hs_lastmodifieddate", "operator": "GTE", "value": self._ms(self.start_date())},
            {"propertyName": "hs_lastmodifieddate", "operator": "LTE", "value": self._ms(self.now())},
            {"propertyName": "hs_object_id", "operator": "GTE", "value": id_floor},
        ]

    def search_request(self, after: int = 0, id_floor: int = 0) -> HttpRequest:
        body = {
            "limit": 200,
            "sorts": [{"propertyName": "hs_object_id", "direction": "ASCENDING"}],
            "filterGroups": [{"filters": self._filters(p, id_floor)} for p in self.RECORDING_PROPERTIES],
            "properties": self.RECORDING_PROPERTIES + ["hs_createdate", "hs_lastmodifieddate"],
            "after": after,
        }
        return HttpRequest(url=SEARCH_URL.format(entity=self.ENTITY), body=json.dumps(body))

    @staticmethod
    def search_result(record_id: str, properties: Dict[str, Optional[str]]) -> Dict[str, Any]:
        return {
            "id": record_id,
            "properties": {
                "hs_createdate": "2024-03-01T10:00:00.000Z",
                "hs_lastmodifieddate": UPDATED_AT,
                "hs_object_id": record_id,
                **properties,
            },
            "createdAt": "2024-03-01T10:00:00.000Z",
            "updatedAt": UPDATED_AT,
            "archived": False,
        }

    @staticmethod
    def search_response(results: List[Dict[str, Any]], next_after: Optional[str] = None) -> HttpResponse:
        body: Dict[str, Any] = {"total": len(results), "results": results}
        if next_after:
            body["paging"] = {"next": {"after": next_after}}
        return HttpResponse(json.dumps(body), 200)

    @staticmethod
    def mock_download(http_mocker: HttpMocker, url: str, response: HttpResponse) -> None:
        http_mocker.get(HttpRequest(url=url), response)

    def read(self, http_mocker: HttpMocker, sync_mode: SyncMode = SyncMode.incremental, expecting_exception: bool = False):
        self.mock_custom_objects_streams(http_mocker)
        return self.read_from_stream(
            self.private_token_config(self.ACCESS_TOKEN), self.STREAM_NAME, sync_mode, expecting_exception=expecting_exception
        )


class TestMeetingRecordingsStream(RecordingsStreamTestCase):
    STREAM_NAME = "meeting_recordings"
    ENTITY = "meetings"
    RECORDING_PROPERTIES = ["hs_meeting_recording_url"]

    def test_given_recordings_when_read_then_download_files_and_emit_join_keys(self, files_directory: Path):
        mp4_url = HUBSPOT_RECORDING_URL.format(id="101")
        m4a_url = "https://app.hubspot.com/recordings/102/audio.M4A?token=abc"
        with HttpMocker() as http_mocker:
            http_mocker.post(
                self.search_request(),
                self.search_response(
                    [
                        self.search_result("101", {"hs_meeting_recording_url": mp4_url}),
                        self.search_result("102", {"hs_meeting_recording_url": m4a_url}),
                    ]
                ),
            )
            self.mock_download(http_mocker, mp4_url, HttpResponse("mp4-bytes", 200))
            self.mock_download(http_mocker, m4a_url, HttpResponse("m4a-bytes", 200))

            output = self.read(http_mocker)

        records = [message.record for message in output.records]
        assert [record.data for record in records] == [
            {
                "meeting_id": "101",
                "archived": False,
                "object_type": "meeting",
                "recording_url": mp4_url,
                "hs_createdate": "2024-03-01T10:00:00.000Z",
                "hs_lastmodifieddate": UPDATED_AT,
                "file_name": "101.mp4",
            },
            {
                "meeting_id": "102",
                "archived": False,
                "object_type": "meeting",
                "recording_url": m4a_url,
                "hs_createdate": "2024-03-01T10:00:00.000Z",
                "hs_lastmodifieddate": UPDATED_AT,
                "file_name": "102.m4a",
            },
        ]
        assert [record.file_reference.source_file_relative_path for record in records] == [
            "meeting_recordings/101.mp4",
            "meeting_recordings/102.m4a",
        ]
        assert (files_directory / "meeting_recordings" / "101.mp4").read_text() == "mp4-bytes"
        assert (files_directory / "meeting_recordings" / "102.m4a").read_text() == "m4a-bytes"

    def test_given_non_hubspot_recording_url_when_read_then_skip_record_without_sending_token(self):
        hubspot_url = HUBSPOT_RECORDING_URL.format(id="101")
        with HttpMocker() as http_mocker:
            http_mocker.post(
                self.search_request(),
                self.search_response(
                    [
                        self.search_result("101", {"hs_meeting_recording_url": hubspot_url}),
                        # Third-party hosts never receive the HubSpot token, so no download is mocked for them.
                        self.search_result("102", {"hs_meeting_recording_url": "https://zoom.us/rec/share/102.mp4"}),
                        self.search_result("103", {"hs_meeting_recording_url": "https://hubspot.com.evil.example/103.mp4"}),
                        self.search_result("104", {"hs_meeting_recording_url": "http://api.hubapi.com/104.mp4"}),
                    ]
                ),
            )
            self.mock_download(http_mocker, hubspot_url, HttpResponse("mp4-bytes", 200))

            output = self.read(http_mocker)

        assert [message.record.data["meeting_id"] for message in output.records] == ["101"]

    def test_given_filtered_full_page_when_read_then_continue_to_next_page(self):
        """A page that the host filter shrinks below page_size must not end pagination."""
        third_party_results = [
            self.search_result(str(1000 + i), {"hs_meeting_recording_url": f"https://zoom.us/rec/{i}.mp4"}) for i in range(199)
        ]
        first_url = HUBSPOT_RECORDING_URL.format(id="1199")
        second_url = HUBSPOT_RECORDING_URL.format(id="2000")
        with HttpMocker() as http_mocker:
            http_mocker.post(
                self.search_request(),
                self.search_response(
                    third_party_results + [self.search_result("1199", {"hs_meeting_recording_url": first_url})],
                    next_after="200",
                ),
            )
            http_mocker.post(
                self.search_request(after=200),
                self.search_response([self.search_result("2000", {"hs_meeting_recording_url": second_url})]),
            )
            self.mock_download(http_mocker, first_url, HttpResponse("first", 200))
            self.mock_download(http_mocker, second_url, HttpResponse("second", 200))

            output = self.read(http_mocker)

        assert [message.record.data["meeting_id"] for message in output.records] == ["1199", "2000"]

    def test_given_recording_not_found_when_read_then_emit_record_and_continue(self):
        missing_url = HUBSPOT_RECORDING_URL.format(id="101")
        present_url = HUBSPOT_RECORDING_URL.format(id="102")
        with HttpMocker() as http_mocker:
            http_mocker.post(
                self.search_request(),
                self.search_response(
                    [
                        self.search_result("101", {"hs_meeting_recording_url": missing_url}),
                        self.search_result("102", {"hs_meeting_recording_url": present_url}),
                    ]
                ),
            )
            self.mock_download(http_mocker, missing_url, HttpResponse(json.dumps({"message": "not found"}), http.HTTPStatus.NOT_FOUND))
            self.mock_download(http_mocker, present_url, HttpResponse("mp4-bytes", 200))

            output = self.read(http_mocker)

        assert [message.record.data["meeting_id"] for message in output.records] == ["101", "102"]
        assert not output.errors

    def test_given_incremental_sync_when_read_then_state_is_latest_hs_lastmodifieddate(self):
        url = HUBSPOT_RECORDING_URL.format(id="101")
        with HttpMocker() as http_mocker:
            http_mocker.post(
                self.search_request(),
                self.search_response([self.search_result("101", {"hs_meeting_recording_url": url})]),
            )
            self.mock_download(http_mocker, url, HttpResponse("mp4-bytes", 200))

            output = self.read(http_mocker)

        assert output.most_recent_state.stream_state.__dict__["hs_lastmodifieddate"] == "2024-03-02T10:00:00.000000Z"

    def test_given_missing_scopes_when_read_then_fail_with_scope_message(self):
        with HttpMocker() as http_mocker:
            http_mocker.post(self.search_request(), HttpResponse(json.dumps({"message": "forbidden"}), http.HTTPStatus.FORBIDDEN))

            output = self.read(http_mocker, expecting_exception=True)

        assert not output.records
        assert any("crm.objects.contacts.read" in error.trace.error.message for error in output.errors)


class TestCallRecordingsStream(RecordingsStreamTestCase):
    STREAM_NAME = "call_recordings"
    ENTITY = "calls"
    RECORDING_PROPERTIES = ["hs_call_recording_url", "hs_call_video_recording_url"]

    def test_given_audio_and_video_recordings_when_read_then_prefer_audio(self, files_directory: Path):
        audio_url = "https://api.hubapi.com/calling/v1/recordings/201.mp3"
        video_url = HUBSPOT_RECORDING_URL.format(id="202")
        with HttpMocker() as http_mocker:
            http_mocker.post(
                self.search_request(),
                self.search_response(
                    [
                        self.search_result(
                            "201",
                            {"hs_call_recording_url": audio_url, "hs_call_video_recording_url": "https://api.hubapi.com/unused.mp4"},
                        ),
                        self.search_result("202", {"hs_call_recording_url": None, "hs_call_video_recording_url": video_url}),
                    ]
                ),
            )
            self.mock_download(http_mocker, audio_url, HttpResponse("mp3-bytes", 200))
            self.mock_download(http_mocker, video_url, HttpResponse("mp4-bytes", 200))

            output = self.read(http_mocker)

        records = [message.record.data for message in output.records]
        assert [(r["call_id"], r["object_type"], r["recording_url"], r["file_name"]) for r in records] == [
            ("201", "call", audio_url, "201.mp3"),
            ("202", "call", video_url, "202.mp4"),
        ]
        assert (files_directory / "call_recordings" / "201.mp3").read_text() == "mp3-bytes"
        assert (files_directory / "call_recordings" / "202.mp4").read_text() == "mp4-bytes"
