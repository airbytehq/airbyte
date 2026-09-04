#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import os
import sys

from airbyte_cdk.entrypoint import launch
from source_tiktok_organic import SourceTiktokOrganic


def _bootstrap_runtime_config(argv: list[str]) -> None:
    """
    Persist the raw connector config for custom components that may receive an empty
    declarative config context during runtime construction.
    """
    try:
        if "--config" not in argv:
            return
        config_index = argv.index("--config")
        if config_index + 1 >= len(argv):
            return
        config_path = argv[config_index + 1]
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        os.environ["SOURCE_TIKTOK_ORGANIC_CONFIG"] = json.dumps(config)
        os.environ["SOURCE_TIKTOK_ORGANIC_CONFIG_PATH"] = config_path
    except Exception:
        # Best-effort fallback only; normal CDK config injection is still preferred.
        return


def _bootstrap_runtime_state(argv: list[str]) -> None:
    """
    Expose whether a non-empty --state file was provided.
    This is used as a stable fallback when stream_state is not propagated
    into low-code requester context in local CLI runs.
    """
    try:
        if "--state" not in argv:
            os.environ["SOURCE_TIKTOK_ORGANIC_HAS_STATE"] = "0"
            return
        state_index = argv.index("--state")
        if state_index + 1 >= len(argv):
            os.environ["SOURCE_TIKTOK_ORGANIC_HAS_STATE"] = "0"
            return
        state_path = argv[state_index + 1]
        with open(state_path, "r", encoding="utf-8") as f:
            state_obj = json.load(f)
        has_state = isinstance(state_obj, list) and len(state_obj) > 0
        os.environ["SOURCE_TIKTOK_ORGANIC_HAS_STATE"] = "1" if has_state else "0"
    except Exception:
        os.environ["SOURCE_TIKTOK_ORGANIC_HAS_STATE"] = "0"


def _extract_loaded_config(argv: list[str]) -> tuple[dict, str | None]:
    try:
        if "--config" not in argv:
            return {}, None
        config_index = argv.index("--config")
        if config_index + 1 >= len(argv):
            return {}, None
        config_path = argv[config_index + 1]
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f), config_path
    except Exception:
        return {}, None


def run():
    args = sys.argv[1:]
    _bootstrap_runtime_config(args)
    _bootstrap_runtime_state(args)
    loaded_config, config_path = _extract_loaded_config(args)
    source = SourceTiktokOrganic(config=loaded_config, config_path=config_path)
    launch(source, args)
