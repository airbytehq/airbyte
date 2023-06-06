import json

import pytest

from airbyte_cdk.entrypoint import launch
from unit_tests.sources.file_based.helpers import make_file, json_spec
from unit_tests.sources.file_based.scenarios.csv_scenarios import SingleCsvTestScenario


scenarios = [
    SingleCsvTestScenario(),
]


@pytest.mark.parametrize("scenario", scenarios)
def test_discover(capsys, tmp_path, json_spec, scenario):
    launch(
        scenario.source,
        ["discover", "--config", make_file(tmp_path / "config.json", scenario.config)],
    )
    captured = capsys.readouterr()
    catalog = json.loads(captured.out.splitlines()[0])["catalog"]
    assert catalog == scenario.expected_catalog


@pytest.mark.parametrize("scenario", scenarios)
def test_read(capsys, tmp_path, json_spec, scenario):
    launch(
        scenario.source,
        [
            "read",
            "--config",
            make_file(tmp_path / "config.json", scenario.config),
            "--catalog",
            make_file(tmp_path / "catalog.json", scenario.configured_catalog()),
        ],
    )
    captured = capsys.readouterr()
    records = [
        msg
        for msg in (json.loads(line) for line in captured.out.splitlines())
        if msg["type"] == "RECORD"
    ]
    expected_records = scenario.expected_records
    assert len(records) == len(expected_records)
    for actual, expected in zip(records, expected_records):
        assert actual["record"]["data"] == expected
