import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
import requests_mock

from ci_code_validator.ci_sonar_qube.log_parsers import LogParser

HERE = Path(__file__).parent
PACKAGE_DIR = HERE / "simple_package"
SMELL_PACKAGE_DIR = HERE / "simple_smell_package"
SIMPLE_FILES = HERE / "simple_files"
WITHOUT_ISSUE_REPORT = SIMPLE_FILES / "without_issues_report.json"

ISORT_CMD = """isort --diff {package_dir}"""  # config file should be in a started folder
BLACK_CMD = r"""black --config {toml_config_file} --diff {package_dir}"""
MYPY_CMD = r"""mypy {package_dir} --config-file={toml_config_file}"""


@pytest.fixture(scope="session")
def toml_config_file() -> Path:
    root_dir = HERE
    while str(root_dir) != root_dir.root:
        config_file = root_dir / "pyproject.toml"
        if config_file.is_file():
            return config_file
        root_dir = root_dir.parent
    raise Exception("can't found pyproject.toml")


@pytest.fixture(autouse=True)
def prepare_toml_file(toml_config_file):
    pyproject_toml = Path(os.getcwd()) / "pyproject.toml"
    if toml_config_file != pyproject_toml and not pyproject_toml.is_file():
        shutil.copy(toml_config_file, pyproject_toml)
    yield
    if toml_config_file != pyproject_toml and pyproject_toml.is_file():
        os.remove(str(pyproject_toml))


@pytest.mark.parametrize(
    "cmd,package_dir,expected_file",
    [
        (
                "mypy {package_dir} --config-file={toml_config_file}",
                SMELL_PACKAGE_DIR,
                SIMPLE_FILES / "mypy_smell_package_report.json"
        ),
        (
                "mypy {package_dir} --config-file={toml_config_file}",
                PACKAGE_DIR,
                WITHOUT_ISSUE_REPORT
        ),
        (
                "black --config {toml_config_file} --diff {package_dir}",
                SMELL_PACKAGE_DIR,
                HERE / "simple_files/black_smell_package_report.json"
        ),
        (
                "black --config {toml_config_file} --diff {package_dir}",
                PACKAGE_DIR,
                WITHOUT_ISSUE_REPORT
        ),
        (
                ISORT_CMD,
                SMELL_PACKAGE_DIR,
                HERE / "simple_files/isort_smell_package_report.json"
        ),
        (
                ISORT_CMD,
                PACKAGE_DIR,
                WITHOUT_ISSUE_REPORT,
        ),
    ],
    ids=["mypy_failed", "mypy_pass", "black_failed", "black_pass", "isort_failed", "isort_pass"]
)
def test_tool(tmp_path, toml_config_file, cmd, package_dir, expected_file):
    cmd = cmd.format(package_dir=package_dir, toml_config_file=toml_config_file)

    proc = subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _ = proc.communicate()
    file_log = tmp_path / "temp.log"
    file_log.write_bytes(out)
    assert file_log.is_file() is True
    issues_file = tmp_path / "issues.json"
    with requests_mock.Mocker() as m:
        m.get('/api/authentication/validate', json={"valid": True})
        m.get("/api/rules/search", json={"rules": []})
        m.post("/api/rules/create", json={})
        parser = LogParser(issues_file, host="http://fake.com/", token="fake_token")
        assert getattr(parser, f'from_{cmd.split(" ")[0]}')(file_log) == 0

        assert issues_file.is_file() is True
        data = json.loads(issues_file.read_text())
        for issue in data["issues"]:
            issue["primaryLocation"]["filePath"] = "/".join(issue["primaryLocation"]["filePath"].split("/")[-2:])

        expected_data = json.loads(Path(expected_file).read_text())
        assert json.dumps(data, sort_keys=True, separators=(',', ': ')) == json.dumps(expected_data, sort_keys=True, separators=(',', ': '))
