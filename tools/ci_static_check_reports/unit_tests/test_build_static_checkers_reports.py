#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import os

from ..build_static_checkers_reports import build_static_checkers_reports


def test_build_static_checkers_reports() -> None:
    changed_module_path = "tools/ci_static_check_reports"
    build_static_checkers_reports([changed_module_path])
    static_checker_reports_path = "static_checker_reports/tools/ci_static_check_reports"

    assert os.path.exists(static_checker_reports_path)
    assert os.path.exists(os.path.join(static_checker_reports_path, "black.txt"))
    assert os.path.exists(os.path.join(static_checker_reports_path, "coverage.xml"))
    assert os.path.exists(os.path.join(static_checker_reports_path, "flake.xml"))
    assert os.path.exists(os.path.join(static_checker_reports_path, "isort.txt"))
    assert os.path.exists(os.path.join(static_checker_reports_path, "cobertura.xml"))
    assert os.path.exists(os.path.join(static_checker_reports_path, "pytest.xml"))
