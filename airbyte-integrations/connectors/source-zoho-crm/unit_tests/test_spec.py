#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path


def test_dc_region_documentation_url():
    spec_path = Path(__file__).parents[1] / "source_zoho_crm" / "spec.json"
    spec_text = spec_path.read_text()
    spec = json.loads(spec_text)
    description = spec["connectionSpecification"]["properties"]["dc_region"]["description"]

    assert "https://www.zoho.com/crm/developer/docs/api/v8/multi-dc.html" in description
    assert "/crm/developer/docs/api/v2/" not in spec_text
