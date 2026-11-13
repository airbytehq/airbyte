# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

from airbyte_cdk.test.mock_http import HttpResponse


def response_for(stream: str, primary_key: str, ids: list[int]) -> HttpResponse:
    template = json.loads((Path(__file__).parent.parent / "resource" / "http" / "records.json").read_text())
    template["RECDATA"] = [{primary_key: identifier if stream == "activities" else str(identifier)} for identifier in ids]
    template["METADATA"]["RESULTS"]["CURRENT_COUNT"] = len(ids)
    return HttpResponse(json.dumps(template), 200)
