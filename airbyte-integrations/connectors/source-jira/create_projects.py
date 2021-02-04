import json
import pathlib
import requests

from requests.auth import HTTPBasicAuth


def create():
    source_directory = pathlib.Path(__file__).resolve().parent
    configs_path = source_directory.joinpath('secrets/config.json')
    with open(configs_path) as json_configs:
        configs = json.load(json_configs)
    auth = HTTPBasicAuth(configs.get('email'), configs.get('api_token'))
    base_api_url = f'https://{configs.get("domain")}/rest/api/3/project'

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    for index in range(1, 51):
        payload = json.dumps({
            "key": f"TESTKEY{index}",
            "name": f"Test project {index}",
            "projectTypeKey": "software",
            "projectTemplateKey": "com.pyxis.greenhopper.jira:gh-simplified-scrum-classic",
            "description": f"Test project {index} description",
            "leadAccountId": "5fc9e78d2730d800760becc4",
            "assigneeType": "PROJECT_LEAD",
        })

        requests.request(
            "POST",
            base_api_url,
            data=payload,
            headers=headers,
            auth=auth
        )


if __name__ == "__main__":
    create()
