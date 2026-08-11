#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Mapping


def build_credential_header(token: str) -> Mapping[str, str]:
    return {"Authorization": f"Bearer {token}"}
