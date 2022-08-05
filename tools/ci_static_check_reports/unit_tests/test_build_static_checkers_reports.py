#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import os
import subprocess

import pytest


@pytest.mark.parametrize(
    "changed_module,should_build_reports",
    [
        ('[{"dir": "tools/ci_static_check_reports", "lang": "py"}]', True),
        ('[{"dir": "airbyte-integrations/connectors/destination-bigquery", "lang": "java"}]', False),
        ('[{"dir": "airbyte-integrations/connectors/not-existing-module", "lang": "other"}]', False),
    ],
)
def test_build_static_checkers_reports(changed_module: str, should_build_reports: bool) -> None:
    subprocess.call(["ci_build_python_checkers_reports", changed_module], shell=False)
    static_checker_reports_path = f"static_checker_reports/{changed_module}"

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
