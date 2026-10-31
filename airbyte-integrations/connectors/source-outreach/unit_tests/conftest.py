# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import importlib.util
import os
import sys
import types
from pathlib import Path


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

os.environ.setdefault("REQUEST_CACHE_PATH", "REQUEST_CACHE_PATH")

try:
    importlib.import_module("source_declarative_manifest.components")
except ImportError:
    _COMPONENTS_PATH = Path(__file__).parents[1] / "components.py"
    if _COMPONENTS_PATH.is_file():
        _spec = importlib.util.spec_from_file_location("source_declarative_manifest.components", _COMPONENTS_PATH)
        _module = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_module)
        sys.modules.setdefault("source_declarative_manifest", types.ModuleType("source_declarative_manifest"))
        sys.modules["source_declarative_manifest.components"] = _module
