# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for ComfyUI Cloud stream implementations."""

from unittest.mock import MagicMock, patch

import pytest
import requests
from source_comfyui.streams import (
    AssetsStream,
    JobDetailsStream,
    JobsStream,
    ModelsStream,
    NodesStream,
    SystemStatsStream,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def api_key():
    return "test-api-key-123"


@pytest.fixture
def base_url():
    return "https://cloud.comfy.org"


@pytest.fixture
def stream_kwargs(api_key, base_url):
    return {"api_key": api_key, "base_url": base_url}


def _mock_response(json_data, status_code=200):
    """Create a mock requests.Response with the given JSON body."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    return resp


# ═══════════════════════════════════════════════════════════════════════════════
# JobsStream
# ═══════════════════════════════════════════════════════════════════════════════


class TestJobsStream:
    def test_path(self, stream_kwargs):
        stream = JobsStream(**stream_kwargs)
        assert stream.path() == "/api/jobs"

    def test_cursor_field(self, stream_kwargs):
        stream = JobsStream(**stream_kwargs)
        assert stream.cursor_field == "create_time"

    def test_primary_key(self, stream_kwargs):
        stream = JobsStream(**stream_kwargs)
        assert stream.primary_key == "id"

    def test_parse_response(self, stream_kwargs):
        stream = JobsStream(**stream_kwargs)
        response = _mock_response(
            {
                "jobs": [
                    {"id": "abc", "status": "completed", "create_time": 1700000000},
                    {"id": "def", "status": "running", "create_time": 1700000100},
                ],
                "pagination": {"has_more": False},
            }
        )

        records = list(stream.parse_response(response))

        assert len(records) == 2
        assert records[0]["id"] == "abc"
        assert records[0]["status"] == "completed"
        assert records[0]["create_time"] == 1700000000
        assert records[1]["id"] == "def"

    def test_parse_response_empty_jobs(self, stream_kwargs):
        stream = JobsStream(**stream_kwargs)
        response = _mock_response({"jobs": [], "pagination": {"has_more": False}})

        records = list(stream.parse_response(response))
        assert records == []

    def test_next_page_token_has_more(self, stream_kwargs):
        stream = JobsStream(**stream_kwargs)
        response = _mock_response(
            {
                "jobs": [{"id": "a"}],
                "pagination": {"has_more": True, "offset": 0, "limit": 100},
            }
        )

        token = stream.next_page_token(response)

        assert token == {"offset": 100}

    def test_next_page_token_has_more_mid_page(self, stream_kwargs):
        """Offset advances from a non-zero starting point."""
        stream = JobsStream(**stream_kwargs)
        response = _mock_response(
            {
                "jobs": [{"id": "b"}],
                "pagination": {"has_more": True, "offset": 200, "limit": 100},
            }
        )

        token = stream.next_page_token(response)
        assert token == {"offset": 300}

    def test_next_page_token_no_more(self, stream_kwargs):
        stream = JobsStream(**stream_kwargs)
        response = _mock_response(
            {
                "jobs": [],
                "pagination": {"has_more": False, "offset": 0, "limit": 100},
            }
        )

        token = stream.next_page_token(response)
        assert token is None

    def test_request_params_default(self, stream_kwargs):
        stream = JobsStream(**stream_kwargs)
        params = stream.request_params()

        assert params["limit"] == 100
        assert params["offset"] == 0
        assert params["sort_by"] == "create_time"
        assert params["sort_order"] == "asc"

    def test_request_params_with_next_page_token(self, stream_kwargs):
        stream = JobsStream(**stream_kwargs)
        params = stream.request_params(next_page_token={"offset": 200})

        assert params["offset"] == 200
        assert params["limit"] == 100

    def test_request_headers(self, stream_kwargs, api_key):
        stream = JobsStream(**stream_kwargs)
        headers = stream.request_headers()

        assert headers == {"X-API-Key": api_key}


# ═══════════════════════════════════════════════════════════════════════════════
# AssetsStream
# ═══════════════════════════════════════════════════════════════════════════════


class TestAssetsStream:
    def test_path(self, stream_kwargs):
        stream = AssetsStream(**stream_kwargs)
        assert stream.path() == "/api/assets"

    def test_cursor_field(self, stream_kwargs):
        stream = AssetsStream(**stream_kwargs)
        assert stream.cursor_field == "created_at"

    def test_primary_key(self, stream_kwargs):
        stream = AssetsStream(**stream_kwargs)
        assert stream.primary_key == "id"

    def test_parse_response(self, stream_kwargs):
        stream = AssetsStream(**stream_kwargs)
        response = _mock_response(
            {
                "assets": [
                    {
                        "id": "asset-1",
                        "url": "https://cdn.example.com/a.png",
                        "created_at": "2024-01-01T00:00:00Z",
                    },
                    {
                        "id": "asset-2",
                        "url": "https://cdn.example.com/b.png",
                        "created_at": "2024-01-02T00:00:00Z",
                    },
                ],
                "has_more": False,
            }
        )

        records = list(stream.parse_response(response))

        assert len(records) == 2
        assert records[0]["id"] == "asset-1"
        assert records[1]["created_at"] == "2024-01-02T00:00:00Z"

    def test_parse_response_empty(self, stream_kwargs):
        stream = AssetsStream(**stream_kwargs)
        response = _mock_response({"assets": [], "has_more": False})

        records = list(stream.parse_response(response))
        assert records == []

    def test_pagination_has_more(self, stream_kwargs):
        stream = AssetsStream(**stream_kwargs)
        response = _mock_response(
            {
                "assets": [{"id": "a"}],
                "has_more": True,
                "offset": 0,
                "limit": 100,
            }
        )

        token = stream.next_page_token(response)
        assert token == {"offset": 100}

    def test_pagination_no_more(self, stream_kwargs):
        stream = AssetsStream(**stream_kwargs)
        response = _mock_response(
            {
                "assets": [],
                "has_more": False,
                "offset": 0,
                "limit": 100,
            }
        )

        token = stream.next_page_token(response)
        assert token is None

    def test_request_params_default(self, stream_kwargs):
        stream = AssetsStream(**stream_kwargs)
        params = stream.request_params()

        assert params["limit"] == 100
        assert params["offset"] == 0
        assert params["sort"] == "created_at"
        assert params["order"] == "asc"

    def test_request_params_with_token(self, stream_kwargs):
        stream = AssetsStream(**stream_kwargs)
        params = stream.request_params(next_page_token={"offset": 300})

        assert params["offset"] == 300

    def test_request_headers(self, stream_kwargs, api_key):
        stream = AssetsStream(**stream_kwargs)
        headers = stream.request_headers()
        assert headers == {"X-API-Key": api_key}


# ═══════════════════════════════════════════════════════════════════════════════
# NodesStream
# ═══════════════════════════════════════════════════════════════════════════════


class TestNodesStream:
    def test_path(self, stream_kwargs):
        stream = NodesStream(**stream_kwargs)
        assert stream.path() == "/api/object_info"

    def test_primary_key(self, stream_kwargs):
        stream = NodesStream(**stream_kwargs)
        assert stream.primary_key == "name"

    def test_parse_response(self, stream_kwargs):
        stream = NodesStream(**stream_kwargs)
        response = _mock_response(
            {
                "KSampler": {
                    "input": {"required": {"seed": ["INT"]}},
                    "output": ["LATENT"],
                    "category": "sampling",
                },
                "CLIPTextEncode": {
                    "input": {"required": {"text": ["STRING"]}},
                    "output": ["CONDITIONING"],
                    "category": "conditioning",
                },
            }
        )

        records = list(stream.parse_response(response))

        assert len(records) == 2
        names = {r["name"] for r in records}
        assert names == {"KSampler", "CLIPTextEncode"}

        ksampler = next(r for r in records if r["name"] == "KSampler")
        assert ksampler["category"] == "sampling"
        assert ksampler["output"] == ["LATENT"]

    def test_parse_response_non_dict_node_info(self, stream_kwargs):
        """When a node's info is not a dict, it gets wrapped in a 'data' field."""
        stream = NodesStream(**stream_kwargs)
        response = _mock_response(
            {
                "SimpleNode": "just-a-string",
            }
        )

        records = list(stream.parse_response(response))

        assert len(records) == 1
        assert records[0]["name"] == "SimpleNode"
        assert records[0]["data"] == "just-a-string"

    def test_parse_response_empty(self, stream_kwargs):
        stream = NodesStream(**stream_kwargs)
        response = _mock_response({})

        records = list(stream.parse_response(response))
        assert records == []

    def test_request_headers(self, stream_kwargs, api_key):
        stream = NodesStream(**stream_kwargs)
        headers = stream.request_headers()
        assert headers == {"X-API-Key": api_key}


# ═══════════════════════════════════════════════════════════════════════════════
# SystemStatsStream
# ═══════════════════════════════════════════════════════════════════════════════


class TestSystemStatsStream:
    def test_path(self, stream_kwargs):
        stream = SystemStatsStream(**stream_kwargs)
        assert stream.path() == "/api/system_stats"

    def test_primary_key(self, stream_kwargs):
        stream = SystemStatsStream(**stream_kwargs)
        assert stream.primary_key is None

    def test_parse_response(self, stream_kwargs):
        stats_data = {
            "system": {
                "os": "linux",
                "python_version": "3.11.5",
                "embedded_python": False,
            },
            "devices": [
                {"name": "cuda:0", "type": "cuda", "vram_total": 25769803776},
            ],
        }
        stream = SystemStatsStream(**stream_kwargs)
        response = _mock_response(stats_data)

        records = list(stream.parse_response(response))

        assert len(records) == 1
        assert records[0]["system"]["os"] == "linux"
        assert records[0]["devices"][0]["type"] == "cuda"

    def test_request_headers(self, stream_kwargs, api_key):
        stream = SystemStatsStream(**stream_kwargs)
        headers = stream.request_headers()
        assert headers == {"X-API-Key": api_key}


# ═══════════════════════════════════════════════════════════════════════════════
# ModelsStream
# ═══════════════════════════════════════════════════════════════════════════════


class TestModelsStream:
    def test_path_with_slice(self, stream_kwargs):
        stream = ModelsStream(**stream_kwargs)
        path = stream.path(stream_slice={"folder": "checkpoints"})
        assert path == "/api/models/checkpoints"

    def test_path_without_slice(self, stream_kwargs):
        stream = ModelsStream(**stream_kwargs)
        path = stream.path(stream_slice=None)
        assert path == "/api/models/"

    def test_primary_key(self, stream_kwargs):
        stream = ModelsStream(**stream_kwargs)
        assert stream.primary_key == ["folder", "name"]

    def test_stream_slices(self, stream_kwargs):
        """stream_slices fetches folder names from GET /api/models."""
        stream = ModelsStream(**stream_kwargs)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = ["checkpoints", "loras", "vae"]
        mock_response.raise_for_status = MagicMock()

        with patch("source_comfyui.streams.requests.get", return_value=mock_response):
            slices = list(stream.stream_slices(sync_mode=None))

        assert slices == [
            {"folder": "checkpoints"},
            {"folder": "loras"},
            {"folder": "vae"},
        ]

    def test_stream_slices_request_error(self, stream_kwargs):
        """stream_slices raises RuntimeError on request failure."""
        stream = ModelsStream(**stream_kwargs)

        import requests as req

        with patch(
            "source_comfyui.streams.requests.get",
            side_effect=req.exceptions.ConnectionError("fail"),
        ):
            with pytest.raises(RuntimeError, match="Failed to fetch model folders"):
                list(stream.stream_slices(sync_mode=None))

    def test_parse_response_string_models(self, stream_kwargs):
        """When models are returned as string filenames."""
        stream = ModelsStream(**stream_kwargs)
        response = _mock_response(["model_v1.safetensors", "model_v2.safetensors"])

        records = list(
            stream.parse_response(
                response,
                stream_slice={"folder": "checkpoints"},
            )
        )

        assert len(records) == 2
        assert records[0] == {"folder": "checkpoints", "name": "model_v1.safetensors"}
        assert records[1] == {"folder": "checkpoints", "name": "model_v2.safetensors"}

    def test_parse_response_dict_models(self, stream_kwargs):
        """When models are returned as dicts with metadata."""
        stream = ModelsStream(**stream_kwargs)
        response = _mock_response(
            {
                "models": [
                    {"name": "sd_xl.safetensors", "size": 6938000000},
                    {"name": "sd_15.safetensors", "size": 4270000000},
                ],
            }
        )

        records = list(
            stream.parse_response(
                response,
                stream_slice={"folder": "checkpoints"},
            )
        )

        assert len(records) == 2
        assert records[0]["folder"] == "checkpoints"
        assert records[0]["name"] == "sd_xl.safetensors"
        assert records[0]["size"] == 6938000000

    def test_request_headers(self, stream_kwargs, api_key):
        stream = ModelsStream(**stream_kwargs)
        headers = stream.request_headers()
        assert headers == {"X-API-Key": api_key}


# ═══════════════════════════════════════════════════════════════════════════════
# JobDetailsStream
# ═══════════════════════════════════════════════════════════════════════════════


class TestJobDetailsStream:
    @pytest.fixture
    def parent_stream(self, stream_kwargs):
        return JobsStream(**stream_kwargs)

    def test_path_with_slice(self, stream_kwargs, parent_stream):
        stream = JobDetailsStream(parent=parent_stream, **stream_kwargs)
        path = stream.path(stream_slice={"job_id": "job-abc-123"})
        assert path == "/api/jobs/job-abc-123"

    def test_path_without_slice(self, stream_kwargs, parent_stream):
        stream = JobDetailsStream(parent=parent_stream, **stream_kwargs)
        path = stream.path(stream_slice=None)
        assert path == "/api/jobs/"

    def test_cursor_field(self, stream_kwargs, parent_stream):
        stream = JobDetailsStream(parent=parent_stream, **stream_kwargs)
        assert stream.cursor_field == "create_time"

    def test_primary_key(self, stream_kwargs, parent_stream):
        stream = JobDetailsStream(parent=parent_stream, **stream_kwargs)
        assert stream.primary_key == "id"

    def test_parse_response(self, stream_kwargs, parent_stream):
        stream = JobDetailsStream(parent=parent_stream, **stream_kwargs)
        job_detail = {
            "id": "job-abc-123",
            "status": "completed",
            "create_time": 1700000000,
            "workflow": {"nodes": [{"id": 1, "type": "KSampler"}]},
            "outputs": [{"url": "https://cdn.example.com/out.png"}],
        }
        response = _mock_response(job_detail)

        records = list(stream.parse_response(response))

        assert len(records) == 1
        assert records[0]["id"] == "job-abc-123"
        assert records[0]["status"] == "completed"
        assert records[0]["workflow"]["nodes"][0]["type"] == "KSampler"

    def test_request_headers(self, stream_kwargs, parent_stream, api_key):
        stream = JobDetailsStream(parent=parent_stream, **stream_kwargs)
        headers = stream.request_headers()
        assert headers == {"X-API-Key": api_key}


# ═══════════════════════════════════════════════════════════════════════════════
# Incremental State
# ═══════════════════════════════════════════════════════════════════════════════


class TestIncrementalState:
    """Tests for ComfyUIIncrementalStream cursor comparison and state management."""

    @pytest.fixture
    def jobs_stream(self, stream_kwargs):
        return JobsStream(**stream_kwargs)

    def test_compare_cursor_values_numeric(self, jobs_stream):
        assert jobs_stream._compare_cursor_values("1700000000", "1700000100") == "1700000100"
        assert jobs_stream._compare_cursor_values("1700000100", "1700000000") == "1700000100"

    def test_compare_cursor_values_iso(self, jobs_stream):
        assert jobs_stream._compare_cursor_values("2024-01-01T00:00:00Z", "2024-06-15T12:00:00Z") == "2024-06-15T12:00:00Z"

    def test_compare_cursor_values_equal(self, jobs_stream):
        assert jobs_stream._compare_cursor_values("100", "100") == "100"

    def test_cursor_value_extracts_field(self, jobs_stream):
        assert jobs_stream._cursor_value({"create_time": 1700000000}) == "1700000000"

    def test_cursor_value_none(self, jobs_stream):
        assert jobs_stream._cursor_value({"other_field": 123}) is None

    def test_is_record_newer_no_prior_state(self, jobs_stream):
        assert jobs_stream._is_record_newer({"create_time": 100}, None) is True

    def test_is_record_newer_strictly_greater(self, jobs_stream):
        assert jobs_stream._is_record_newer({"create_time": 200}, "100") is True

    def test_is_record_newer_equal_returns_false(self, jobs_stream):
        # Strict > comparison prevents duplicates on incremental sync
        assert jobs_stream._is_record_newer({"create_time": 100}, "100") is False

    def test_is_record_newer_older_returns_false(self, jobs_stream):
        assert jobs_stream._is_record_newer({"create_time": 50}, "100") is False

    def test_is_record_newer_none_cursor_in_record(self, jobs_stream):
        assert jobs_stream._is_record_newer({"other": "data"}, "100") is True

    def test_update_state_from_empty(self, jobs_stream):
        jobs_stream._update_state({"create_time": 1700000000})
        assert jobs_stream.state == {"create_time": "1700000000"}

    def test_update_state_advances(self, jobs_stream):
        jobs_stream._state = {"create_time": "1700000000"}
        jobs_stream._update_state({"create_time": 1700000100})
        assert jobs_stream.state["create_time"] == "1700000100"

    def test_update_state_does_not_regress(self, jobs_stream):
        jobs_stream._state = {"create_time": "1700000100"}
        jobs_stream._update_state({"create_time": 1700000000})
        assert jobs_stream.state["create_time"] == "1700000100"

    def test_update_state_skips_none_cursor(self, jobs_stream):
        jobs_stream._update_state({"other": "data"})
        assert jobs_stream.state == {}


# ═══════════════════════════════════════════════════════════════════════════════
# JobDetailsStream Slices
# ═══════════════════════════════════════════════════════════════════════════════


class TestJobDetailsStreamSlices:
    """Tests for JobDetailsStream parent-child slice generation."""

    @pytest.fixture
    def parent_stream(self, stream_kwargs):
        return JobsStream(**stream_kwargs)

    @pytest.fixture
    def details_stream(self, parent_stream, stream_kwargs):
        return JobDetailsStream(parent=parent_stream, **stream_kwargs)

    def test_stream_slices_yields_job_ids(self, details_stream):
        parent_records = [
            {"id": "job-1", "create_time": 100, "status": "completed"},
            {"id": "job-2", "create_time": 200, "status": "completed"},
        ]
        with patch.object(details_stream.parent, "read_records", return_value=iter(parent_records)):
            slices = list(details_stream.stream_slices(sync_mode="full_refresh"))
        assert len(slices) == 2
        assert slices[0]["job_id"] == "job-1"
        assert slices[1]["job_id"] == "job-2"

    def test_stream_slices_empty_parent(self, details_stream):
        with patch.object(details_stream.parent, "read_records", return_value=iter([])):
            slices = list(details_stream.stream_slices(sync_mode="full_refresh"))
        assert slices == []


# ═══════════════════════════════════════════════════════════════════════════════
# ModelsStream Edge Cases
# ═══════════════════════════════════════════════════════════════════════════════


class TestModelsStreamEdgeCases:
    def test_stream_slices_empty_list(self, stream_kwargs):
        stream = ModelsStream(**stream_kwargs)
        with patch("source_comfyui.streams.requests.get") as mock_get:
            mock_get.return_value = _mock_response([])
            slices = list(stream.stream_slices(sync_mode="full_refresh"))
        assert slices == []

    def test_stream_slices_error_raises(self, stream_kwargs):
        stream = ModelsStream(**stream_kwargs)
        with patch("source_comfyui.streams.requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException("connection failed")
            with pytest.raises(RuntimeError, match="Failed to fetch model folders"):
                list(stream.stream_slices(sync_mode="full_refresh"))
