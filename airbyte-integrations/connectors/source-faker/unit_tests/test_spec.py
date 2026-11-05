import json
from pathlib import Path


def test_spec_json_records_per_slice_default():
    spec_path = Path(__file__).resolve().parent.parent / "source_faker" / "spec.json"
    spec = json.loads(spec_path.read_text())

    assert spec["connectionSpecification"]["properties"]["records_per_slice"]["default"] == 1000
