#!/usr/bin/env python3
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

# MSSQL engine shim; implementation moved to db-harness-lib.
import os
import subprocess
import sys


SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = subprocess.run(
    ["git", "-C", SKILL_DIR, "rev-parse", "--show-toplevel"],
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()

TARGET = os.path.join(REPO_ROOT, "airbyte-integrations", "db-harness-lib", "scripts", "extract-state.py")
os.execv(TARGET, [TARGET, *sys.argv[1:]])
