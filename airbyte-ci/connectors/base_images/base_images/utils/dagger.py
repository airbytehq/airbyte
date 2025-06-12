# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


def sh_dash_c(lines: list[str]) -> list[str]:
    """Wrap sequence of commands in shell for safe usage of dagger Container's with_exec method."""
    return ["sh", "-c", " && ".join(["set -o xtrace"] + lines)]
