# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest
import yaml
from conftest import get_source
from freezegun import freeze_time
from jsonschema import Draft7Validator

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


API_URL = "https://api.twitch.tv/helix"
TOKEN_URL = "https://id.twitch.tv/oauth2/token"
UI_ONLY_SCHEMA_FIELDS = {"description", "order", "title"}


def _load_manifest():
    return yaml.safe_load((Path(__file__).parent.parent / "manifest.yaml").read_text())


def _get_auth_config():
    manifest = _load_manifest()
    return manifest["spec"]["advanced_auth"]["oauth_config_specification"]


def _mock_auth(http_mocker):
    response_body = {"access_token": "access_token", "refresh_token": "refresh_token", "expires_in": 3600, "token_type": "bearer"}
    if isinstance(http_mocker, HttpMocker):
        http_mocker.post(
            HttpRequest(
                TOKEN_URL,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                body="grant_type=refresh_token&client_id=client_id&client_secret=client_secret&refresh_token=refresh_token",
            ),
            HttpResponse(json.dumps(response_body)),
        )
    else:
        http_mocker.post(TOKEN_URL, json=response_body)


def _read_stream(config, stream_name, sync_mode):
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(get_source(config), config, catalog, None, False)


def _query_params(request):
    return parse_qs(urlparse(request.url).query)


def _requests_to(requests_mock, path):
    if isinstance(requests_mock, HttpMocker):
        requests_mock = requests_mock._mocker
    return [request for request in requests_mock.request_history if urlparse(request.url).path == path]


def _strip_ui_schema_fields(value):
    if isinstance(value, dict):
        return {key: _strip_ui_schema_fields(sub_value) for key, sub_value in value.items() if key not in UI_ONLY_SCHEMA_FIELDS}
    if isinstance(value, list):
        return [_strip_ui_schema_fields(item) for item in value]
    return value


def _custom_reports_normalization_schema(manifest):
    validations = manifest["spec"]["config_normalization_rules"]["validations"]
    return next(validation for validation in validations if validation["field_path"] == ["custom_reports"])["validation_strategy"][
        "base_schema"
    ]


def test_config_validations(config_gen):
    config_valid = config_gen()
    config_missing_name = config_gen(custom_reports={"clips": [{"game_name": "Fortnite"}], "videos": []})
    config_missing_game_name = config_gen(custom_reports={"clips": [], "videos": [{"name": "Top Videos"}]})
    config_empty_login = config_gen(login=[])
    config_blank_login = config_gen(login=[""])
    config_invalid_enum = config_gen(
        custom_reports={
            "clips": [],
            "videos": [{"name": "Top Videos", "game_name": "Fortnite", "sort": "popular"}],
        }
    )

    assert get_source(config_valid).streams(config=config_valid)

    with pytest.raises(ValueError) as excinfo_missing_name:
        get_source(config_missing_name).streams(config=config_missing_name)
    assert "JSON schema validation error: 'name' is a required property" in str(excinfo_missing_name.value)

    with pytest.raises(ValueError) as excinfo_missing_game_name:
        get_source(config_missing_game_name).streams(config=config_missing_game_name)
    assert "JSON schema validation error: 'game_name' is a required property" in str(excinfo_missing_game_name.value)

    with pytest.raises(ValueError) as excinfo_invalid_enum:
        get_source(config_invalid_enum).streams(config=config_invalid_enum)
    assert "JSON schema validation error: 'popular' is not one of ['time', 'trending', 'views']" in str(excinfo_invalid_enum.value)

    with pytest.raises(ValueError) as excinfo_empty_login:
        get_source(config_empty_login).streams(config=config_empty_login)
    assert "JSON schema validation error: [] should be non-empty" in str(excinfo_empty_login.value)

    with pytest.raises(ValueError) as excinfo_blank_login:
        get_source(config_blank_login).streams(config=config_blank_login)
    assert "JSON schema validation error: '' should be non-empty" in str(excinfo_blank_login.value)


def test_oauth_config_uses_hidden_refresh_token_and_no_authorization_scopes():
    manifest = _load_manifest()
    oauth_config = _get_auth_config()
    refresh_token_property = manifest["spec"]["connection_specification"]["properties"]["client_refresh_token"]
    consent_url = oauth_config["oauth_connector_input_specification"]["consent_url"]

    assert refresh_token_property["airbyte_hidden"] is True
    assert refresh_token_property["airbyte_secret"] is True
    assert oauth_config["complete_oauth_output_specification"]["properties"]["refresh_token"]["path_in_connector_config"] == [
        "client_refresh_token"
    ]
    assert "scope=" in consent_url
    assert "channel:" not in consent_url
    assert "analytics:" not in consent_url
    assert "moderator:" not in consent_url


def test_connection_spec_marks_credentials_as_secrets(config):
    manifest = _load_manifest()
    connection_specification = manifest["spec"]["connection_specification"]
    properties = connection_specification["properties"]

    assert properties["client_id"]["airbyte_secret"] is True
    assert properties["client_secret"]["airbyte_secret"] is True
    assert properties["client_refresh_token"]["airbyte_secret"] is True
    assert Draft7Validator(connection_specification).is_valid(config)
    assert Draft7Validator(connection_specification).is_valid({**config, "login": []}) is False
    assert Draft7Validator(connection_specification).is_valid({**config, "login": [""]}) is False


def test_oauth_token_exchange_posts_credentials_in_form_body():
    oauth_input = _get_auth_config()["oauth_connector_input_specification"]

    assert oauth_input["access_token_url"] == "https://id.twitch.tv/oauth2/token"
    assert oauth_input["access_token_headers"] == {"Content-Type": "application/x-www-form-urlencoded"}
    assert oauth_input["access_token_params"] == {
        "client_id": "{{ client_id_value }}",
        "client_secret": "{{ client_secret_value }}",
        "code": "{{ auth_code_value }}",
        "grant_type": "authorization_code",
        "redirect_uri": "{{ redirect_uri_value }}",
    }


def test_streams_with_custom_reports(config):
    source = get_source(config)
    streams = source.streams(config)
    stream_names = [stream.name for stream in streams]
    custom_clips_stream = next(stream for stream in source.discover(None, config).streams if stream.name == "custom_clips_top_clips")

    assert stream_names[:3] == ["users", "clips", "videos"]
    assert "custom_clips_top_clips" in stream_names
    assert "custom_videos_top_vods" in stream_names
    assert "custom_clips_template" not in stream_names
    assert "custom_videos_template" not in stream_names
    assert custom_clips_stream.source_defined_primary_key == [["id"]]
    assert len(stream_names) == 5


def test_streams_without_custom_reports(config_gen):
    config = config_gen(custom_reports=...)

    streams = get_source(config).streams(config)

    assert [stream.name for stream in streams] == ["users", "clips", "videos"]


@freeze_time("2026-05-05T02:30:00Z")
def test_clips_read_uses_incremental_time_slices(config_gen):
    config = config_gen(custom_reports={"clips": [], "videos": []})
    with HttpMocker() as http_mocker:
        _mock_auth(http_mocker)
        http_mocker.get(
            HttpRequest(f"{API_URL}/users", query_params={"login": "airbyte"}),
            HttpResponse(json.dumps({"data": [{"id": "u1", "login": "airbyte"}]})),
        )
        http_mocker.get(
            HttpRequest(f"{API_URL}/clips", query_params=ANY_QUERY_PARAMS),
            HttpResponse(json.dumps({"data": []})),
        )

        output = _read_stream(config, "clips", SyncMode.incremental)
        clip_queries = [_query_params(request) for request in _requests_to(http_mocker, "/helix/clips")]
    clip_request_params = _load_manifest()["streams"][1]["retriever"]["requester"]["request_parameters"]

    assert output.errors == []
    assert len(clip_queries) == 3
    assert clip_queries[0]["started_at"] != clip_queries[1]["started_at"]
    assert clip_queries[0]["ended_at"] != clip_queries[1]["ended_at"]
    assert clip_queries[0]["broadcaster_id"] == ["u1"]
    assert "stream_interval" in clip_request_params["started_at"]
    assert "stream_interval" in clip_request_params["ended_at"]
    assert "config['start_date']" not in clip_request_params["started_at"]
    assert "now_utc" not in clip_request_params["ended_at"]


@pytest.mark.parametrize(
    ("login_count", "expected_request_sizes"),
    [
        pytest.param(1, [1], id="single_login"),
        pytest.param(100, [100], id="one_full_batch"),
        pytest.param(101, [100, 1], id="two_batches"),
    ],
)
def test_users_read_batches_login_request_parameters(config_gen, requests_mock, login_count, expected_request_sizes):
    logins = [f"user_{index}" for index in range(login_count)]
    config = config_gen(login=logins, custom_reports={"clips": [], "videos": []})
    _mock_auth(requests_mock)

    def users_response(request, context):
        context.status_code = 200
        requested_logins = _query_params(request)["login"]
        return json.dumps({"data": [{"id": f"id_{login}", "login": login} for login in requested_logins]})

    requests_mock.get(f"{API_URL}/users", text=users_response)

    output = _read_stream(config, "users", SyncMode.full_refresh)
    user_queries = [_query_params(request) for request in _requests_to(requests_mock, "/helix/users")]

    assert output.errors == []
    assert len(output.records) == login_count
    assert sorted(len(query["login"]) for query in user_queries) == sorted(expected_request_sizes)


@freeze_time("2026-05-05T02:30:00Z")
@pytest.mark.parametrize(
    ("clip_report", "expected_featured"),
    [
        pytest.param({"name": "Top Clips", "game_name": "Fortnite", "is_featured": False}, "false", id="false"),
        pytest.param({"name": "Top Clips", "game_name": "Fortnite", "is_featured": True}, "true", id="true"),
        pytest.param({"name": "Top Clips", "game_name": "Fortnite"}, None, id="omitted"),
    ],
)
def test_custom_clips_read_resolves_game_and_serializes_is_featured(config_gen, clip_report, expected_featured):
    config = config_gen(custom_reports={"clips": [clip_report], "videos": []})
    with HttpMocker() as http_mocker:
        _mock_auth(http_mocker)
        http_mocker.get(
            HttpRequest(f"{API_URL}/games", query_params={"name": "Fortnite"}),
            HttpResponse(json.dumps({"data": [{"id": "33214", "name": "Fortnite"}]})),
        )
        http_mocker.get(
            HttpRequest(f"{API_URL}/clips", query_params=ANY_QUERY_PARAMS),
            HttpResponse(json.dumps({"data": [{"id": "c1", "created_at": "2026-05-05T00:01:00Z"}]})),
        )

        output = _read_stream(config, "custom_clips_top_clips", SyncMode.incremental)
        game_queries = [_query_params(request) for request in _requests_to(http_mocker, "/helix/games")]
        clip_queries = [_query_params(request) for request in _requests_to(http_mocker, "/helix/clips")]

    assert output.errors == []
    assert game_queries == [{"name": ["Fortnite"]}]
    assert {query["game_id"][0] for query in clip_queries} == {"33214"}
    assert {query["first"][0] for query in clip_queries} == {"100"}
    if expected_featured is None:
        assert all("is_featured" not in query for query in clip_queries)
    else:
        assert {query["is_featured"][0] for query in clip_queries} == {expected_featured}


def test_custom_videos_read_uses_game_id_without_cursor_pagination(config_gen):
    config = config_gen(
        custom_reports={
            "clips": [],
            "videos": [
                {"name": "Top Vods", "game_name": "Fortnite", "language": "en", "period": "week", "sort": "views", "type": "archive"}
            ],
        }
    )
    with HttpMocker() as http_mocker:
        _mock_auth(http_mocker)
        video_request = HttpRequest(
            f"{API_URL}/videos",
            query_params={
                "game_id": "33214",
                "first": "100",
                "sort": "views",
                "type": "archive",
                "period": "week",
                "language": "en",
            },
        )
        http_mocker.get(
            HttpRequest(f"{API_URL}/games", query_params={"name": "Fortnite"}),
            HttpResponse(json.dumps({"data": [{"id": "33214", "name": "Fortnite"}]})),
        )
        http_mocker.get(video_request, HttpResponse(json.dumps({"data": [{"id": "v1", "created_at": "2026-05-05T00:00:00Z"}]})))

        output = _read_stream(config, "custom_videos_top_vods", SyncMode.full_refresh)
        video_queries = [_query_params(request) for request in _requests_to(http_mocker, "/helix/videos")]

    assert output.errors == []
    assert len(output.records) == 1
    assert video_queries == [
        {"game_id": ["33214"], "first": ["100"], "sort": ["views"], "type": ["archive"], "period": ["week"], "language": ["en"]}
    ]
    assert "after" not in video_queries[0]
    assert "before" not in video_queries[0]
    assert len(video_queries) == 1


def test_users_read_retries_rate_limit_response(config_gen, requests_mock, mocker):
    sleep_mock = mocker.patch("time.sleep")
    config = config_gen(custom_reports={"clips": [], "videos": []})
    _mock_auth(requests_mock)
    requests_mock.get(
        f"{API_URL}/users",
        [
            {"status_code": 429, "json": {}, "headers": {"Ratelimit-Remaining": "0", "Ratelimit-Reset": "1777948201"}},
            {"status_code": 200, "json": {"data": [{"id": "u1", "login": "airbyte"}]}},
        ],
    )

    output = _read_stream(config, "users", SyncMode.full_refresh)

    assert output.errors == []
    assert len(output.records) == 1
    assert len(_requests_to(requests_mock, "/helix/users")) == 2
    sleep_mock.assert_called()


def test_custom_category_lookup_resolves_game_name_from_parameters():
    manifest = _load_manifest()
    interpolation = JinjaInterpolation()
    name_template = manifest["definitions"]["custom_category_lookup_stream"]["retriever"]["requester"]["request_parameters"]["name"]

    assert interpolation.eval(name_template, {}, parameters={"game_name": "Fortnite"}) == "Fortnite"


def test_custom_category_lookup_uses_games_endpoint():
    manifest = _load_manifest()
    url = manifest["definitions"]["custom_category_lookup_stream"]["retriever"]["requester"]["url"]

    assert url == "https://api.twitch.tv/helix/games"


def test_game_name_propagates_to_parent_stream():
    manifest = _load_manifest()
    resolved = ManifestReferenceResolver().preprocess_manifest(manifest)

    for ds in resolved["dynamic_streams"]:
        template = ds["stream_template"]
        game_name_mapping = None
        for mapping in ds["components_resolver"]["components_mapping"]:
            if mapping["field_path"][-1] == "name" and "parent_stream_configs" in mapping["field_path"]:
                game_name_mapping = mapping
                break

        assert game_name_mapping is not None, f"No ComponentMappingDefinition found for parent stream name in {ds['name']}"

        target = template
        for key in game_name_mapping["field_path"][:-1]:
            if isinstance(target, list):
                target = target[int(key)]
            else:
                target = target[key]
        target[game_name_mapping["field_path"][-1]] = "Minecraft"

        parent_params = template["retriever"]["partition_router"]["parent_stream_configs"][0]["stream"]["retriever"]["requester"][
            "request_parameters"
        ]
        assert parent_params["name"] == "Minecraft", f"Expected name='Minecraft' after mapping, got: {parent_params}"


def test_custom_reports_schema_matches_normalization_schema():
    manifest = _load_manifest()
    connection_spec_custom_reports = manifest["spec"]["connection_specification"]["properties"]["custom_reports"]
    normalization_schema = _custom_reports_normalization_schema(manifest)

    assert _strip_ui_schema_fields(connection_spec_custom_reports) == normalization_schema
