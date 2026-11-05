import sys
import types
from pathlib import Path

pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

manifest_package = types.ModuleType("source_declarative_manifest")
manifest_package.__path__ = [str(Path(__file__).resolve().parents[1])]
sys.modules.setdefault("source_declarative_manifest", manifest_package)
