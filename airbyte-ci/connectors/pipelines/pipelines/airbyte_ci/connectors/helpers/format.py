import os
from pathlib import Path
import subprocess
from typing import List

from pipelines.airbyte_ci.connectors.context import ConnectorContext


async def format_prettier(context: ConnectorContext, files: List[Path]):
    if len(files) == 0:
        return

    repo_root_path = Path(os.path.abspath(os.path.join(context.connector.metadata_file_path, "../../../..")))
    config_path = repo_root_path / ".prettierrc"
    if not config_path.exists():
        raise Exception(f"Prettier config file not found: {config_path}")

    to_format = [str(file) for file in files]

    print(f"       Formatting files: npx prettier --write {' '.join(to_format)}")
    command = ["npx", "prettier", "--config", str(config_path), "--write"] + to_format
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        print("Files formatted successfully.")
        print(result.stdout)
    else:
        print("Error formatting files.")
        print(result.stderr)
