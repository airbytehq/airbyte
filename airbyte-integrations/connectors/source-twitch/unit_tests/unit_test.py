# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from pathlib import Path

import pytest
import yaml

from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.types import StreamSlice
from airbyte_cdk.utils.mapping_helpers import get_interpolation_context

from conftest import get_source


def _load_manifest():
    with open(Path(__file__).parent.parent / "manifest.yaml", "r") as manifest_file:
        return yaml.safe_load(manifest_file)


def _evaluate_request_parameters(definition_name, components_values, stream_slice):
    manifest = _load_manifest()
    request_parameters = manifest["definitions"][definition_name]["retriever"]["requester"]["request_parameters"]
    interpolation = JinjaInterpolation()
    context = get_interpolation_context(stream_slice=stream_slice)
    return {
        key: value
        for key, value in (
            (
                key,
                interpolation.eval(template, {}, components_values=components_values, **context),
            )
            for key, template in request_parameters.items()
        )
        if value is not None
    }


def test_config_validations(config_gen):
    config_valid = config_gen()
    config_missing_name = config_gen(custom_reports={"clips": [{"game_name": "Fortnite"}], "videos": []})
    config_missing_game_name = config_gen(custom_reports={"clips": [], "videos": [{"name": "Top Videos"}]})
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


def test_streams_with_custom_reports(config):
    streams = get_source(config).streams(config)
    stream_names = [stream.name for stream in streams]

    assert stream_names[:3] == ["users", "clips", "videos"]
    assert "custom_clips_top_clips" in stream_names
    assert "custom_videos_top_vods" in stream_names
    assert len(stream_names) == 5


def test_streams_without_custom_reports(config_gen):
    config = config_gen(custom_reports=...)

    streams = get_source(config).streams(config)

    assert [stream.name for stream in streams] == ["users", "clips", "videos"]


def test_custom_clips_request_params_use_interval_and_optional_is_featured():
    stream_slice = StreamSlice(
        partition={"game_id": "33214"},
        cursor_slice={"start_time": "2026-05-05T00:00:00Z", "end_time": "2026-05-05T01:00:00Z"},
    )

    request_params = _evaluate_request_parameters(
        "custom_clips_stream",
        {"name": "Highlighted Clips", "game_name": "Fortnite", "is_featured": False},
        stream_slice,
    )

    assert request_params == {
        "game_id": 33214,
        "started_at": "2026-05-05T00:00:00Z",
        "ended_at": "2026-05-05T01:00:00Z",
        "is_featured": False,
    }


def test_custom_videos_request_params_only_include_selected_filters():
    stream_slice = StreamSlice(partition={"game_id": "33214"}, cursor_slice={})

    request_params = _evaluate_request_parameters(
        "custom_videos_stream",
        {
            "name": "Language Filter",
            "game_name": "Fortnite",
            "language": "en",
            "period": "week",
            "sort": "views",
            "type": "archive",
        },
        stream_slice,
    )

    assert request_params == {
        "game_id": 33214,
        "language": "en",
        "period": "week",
        "sort": "views",
        "type": "archive",
    }
    assert "after" not in request_params
    assert "before" not in request_params


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
    """Verify the ComponentMappingDefinition field_path can navigate through
    the resolved $ref to set the game_id_resolver's name request parameter."""
    from copy import deepcopy
    from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver

    manifest = _load_manifest()
    resolved = ManifestReferenceResolver().preprocess_manifest(manifest)

    for ds in resolved["dynamic_streams"]:
        template = deepcopy(ds["stream_template"])
        game_name_mapping = None
        for mapping in ds["components_resolver"]["components_mapping"]:
            if mapping["field_path"][-1] == "name" and "parent_stream_configs" in mapping["field_path"]:
                game_name_mapping = mapping
                break

        assert game_name_mapping is not None, (
            f"No ComponentMappingDefinition found for parent stream name in {ds['name']}"
        )

        target = template
        for key in game_name_mapping["field_path"][:-1]:
            if isinstance(target, list):
                target = target[int(key)]
            else:
                target = target[key]
        target[game_name_mapping["field_path"][-1]] = "Minecraft"

        parent_params = (
            template["retriever"]["partition_router"]["parent_stream_configs"][0]
            ["stream"]["retriever"]["requester"]["request_parameters"]
        )
        assert parent_params["name"] == "Minecraft", (
            f"Expected name='Minecraft' after mapping, got: {parent_params}"
        )
