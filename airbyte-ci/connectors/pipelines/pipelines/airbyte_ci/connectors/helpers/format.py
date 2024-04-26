from pathlib import Path
import subprocess
from typing import List


async def format_prettier(files: List[Path]):
    if len(files) == 0:
        return

    to_format = [str(file) for file in files]
    config_path = Path(__file__).parent / ".prettierrc"

    print(f"       Formatting files: npx prettier --write {' '.join(to_format)}")
    command = ["npx", "prettier", "--config", str(config_path), "--write"] + to_format
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        print("Files formatted successfully.")
        print(result.stdout)
    else:
        print("Error formatting files.")
        print(result.stderr)
