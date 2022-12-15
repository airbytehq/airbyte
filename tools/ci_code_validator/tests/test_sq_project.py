import pytest
import requests_mock
from ci_sonar_qube.sonar_qube_api import SonarQubeApi


@pytest.mark.parametrize(
    "module_name,pr, expected_title, expected_key",
    [
        ("connectors/source-s3", "airbyte/1234", "Airbyte Connectors Source S3(#1234)", "pr:1234:airbyte:connectors:source-s3"),
        ("tools/ci_code_validator", "airbyte/1111", "Airbyte Tools Ci Code Validator(#1111)", "pr:1111:airbyte:tools:ci-code-validator"),
        ("airbyte-cdk/python", "0", "Airbyte Airbyte Cdk Python", "master:airbyte:airbyte-cdk:python"),
    ]
)
def test_module2project(module_name, pr, expected_title, expected_key):
    with requests_mock.Mocker() as m:
        m.get('/api/authentication/validate', json={"valid": True})
        api = SonarQubeApi(host="http://fake.com/", token="<fake_token>", pr_name=pr)
        project_settings = api.prepare_project_settings(api.module2project(module_name))
    assert project_settings["name"] == expected_title
    assert project_settings["project"] == expected_key
