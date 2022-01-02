#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import json
import os
import shutil
import subprocess

import pytest


@pytest.mark.parametrize(
    "changed_module,should_build_reports",
    [
        ('[{"folder": "airbyte-integrations/connectors/source-airtable", "lang": "py", "module": "connectors/source-airtable"}]', True),
        (
                '[{"folder": "airbyte-integrations/connectors/destination-bigquery", "lang": "java", "module": "connectors/destination-bigquery" }]',
                False),
        ('[{"folder": "airbyte-integrations/connectors/not-existing-module", "lang": "other", "module": "connectors/not-existing-module"}]',
         False),
    ],
)
def test_build_static_checkers_reports(changed_module: str, should_build_reports: bool) -> None:
    static_checker_reports_path = "/tmp/report_" + json.loads(changed_module)[0]["module"].replace("/", "_")
    if os.path.exists(static_checker_reports_path):
        shutil.rmtree(static_checker_reports_path)
    subprocess.call(["ci_build_python_checkers_reports", changed_module,
                     "--output_folder", static_checker_reports_path],
                    shell=False)

    static_checker_reports_path_exists = os.path.exists(static_checker_reports_path)
    black_exists = os.path.exists(os.path.join(static_checker_reports_path, "black.txt"))
    coverage_exists = os.path.exists(os.path.join(static_checker_reports_path, "coverage.xml"))
    flake_exists = os.path.exists(os.path.join(static_checker_reports_path, "flake.xml"))
    isort_exists = os.path.exists(os.path.join(static_checker_reports_path, "isort.txt"))
    cobertura_exists = os.path.exists(os.path.join(static_checker_reports_path, "cobertura.xml"))
    pytest_exists = os.path.exists(os.path.join(static_checker_reports_path, "pytest.xml"))
    report_paths_exist = [
        static_checker_reports_path_exists,
        black_exists,
        coverage_exists,
        flake_exists,
        isort_exists,
        cobertura_exists,
        pytest_exists,
    ]

    if should_build_reports:
        assert all(report_paths_exist)
    else:
        assert not all(report_paths_exist)
