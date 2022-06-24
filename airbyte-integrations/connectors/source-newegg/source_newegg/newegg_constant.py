from typing import Any, Mapping

VERSION = 309
BASE_URL = "https://api.newegg.com/marketplace/"
AUTH_URL = "https://api.newegg.com/marketplace/ordermgmt/servicestatus?sellerid=%s"


def get_header(config: Mapping[str, Any]) -> Mapping[str, Any]:
    return {
        "Authorization": config["api_key"],
        "SecretKey": config["secret_key"],
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


