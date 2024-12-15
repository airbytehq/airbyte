from typing import Any, Mapping
import requests


def get_token(config: Mapping[str, Any]) -> str:
    response = requests.post(
        url=f"https://login.microsoftonline.com/{config['tenant_id']}/oauth2/v2.0/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "scope": "https://graph.microsoft.com/.default"
        }
    )
    response.raise_for_status()
    return response.json()["access_token"]
