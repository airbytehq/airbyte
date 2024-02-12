#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import datetime
import json
from copy import deepcopy

import pytest

# json credentials with fake private key
json_credentials = """
{
    "type": "service_account",
    "project_id": "unittest-project-id",
    "private_key_id": "9qf98e52oda52g5ne23al6evnf13649c2u077162c",
    "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIBVQIBADANBgkqhkiG9w0BAQEFAASCAT8wggE7AgEAAkEA3slcXL+dA36ESmOi\\n1xBhZmp5Hn0WkaHDtW4naba3plva0ibloBNWhFhjQOh7Ff01PVjhT4D5jgqXBIgc\\nz9Gv3QIDAQABAkEArlhYPoD5SB2/O1PjwHgiMPrL1C9B9S/pr1cH4vPJnpY3VKE3\\n5hvdil14YwRrcbmIxMkK2iRLi9lM4mJmdWPy4QIhAPsRFXZSGx0TZsDxD9V0ZJmZ\\n0AuDCj/NF1xB5KPLmp7pAiEA4yoFox6w7ql/a1pUVaLt0NJkDfE+22pxYGNQaiXU\\nuNUCIQCsFLaIJZiN4jlgbxlyLVeya9lLuqIwvqqPQl6q4ad12QIgS9gG48xmdHig\\n8z3IdIMedZ8ZCtKmEun6Cp1+BsK0wDUCIF0nHfSuU+eTQ2qAON2SHIrJf8UeFO7N\\nzdTN1IwwQqjI\\n-----END PRIVATE KEY-----\\n",
    "client_email": "google-analytics-access@unittest-project-id.iam.gserviceaccount.com",
    "client_id": "213243192021686092537",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/google-analytics-access%40unittest-project-id.iam.gserviceaccount.com"
}
"""


@pytest.fixture
def one_year_ago():
    return datetime.datetime.strftime((datetime.datetime.now() - datetime.timedelta(days=1)), "%Y-%m-%d")


@pytest.fixture
def config(one_year_ago):
    return {
        "property_id": "108176369",
        "property_ids": ["108176369"],
        "credentials": {"auth_type": "Service", "credentials_json": json_credentials},
        "date_ranges_start_date": one_year_ago,
        "dimensions": ["date", "deviceCategory", "operatingSystem", "browser"],
        "metrics": [
            "totalUsers",
            "newUsers",
            "sessions",
            "sessionsPerUser",
            "averageSessionDuration",
            "screenPageViews",
            "screenPageViewsPerSession",
            "bounceRate",
        ],
        "keep_empty_rows": True,
        "custom_reports": json.dumps(
            [
                {
                    "name": "report1",
                    "dimensions": ["date", "browser"],
                    "metrics": ["totalUsers", "sessions", "screenPageViews"],
                }
            ]
        ),
    }


@pytest.fixture
def config_without_date_range():
    return {
        "property_id": "108176369",
        "property_ids": ["108176369"],
        "credentials": {"auth_type": "Service", "credentials_json": json_credentials},
        "dimensions": ["deviceCategory", "operatingSystem", "browser"],
        "metrics": [
            "totalUsers",
            "newUsers",
            "sessions",
            "sessionsPerUser",
            "averageSessionDuration",
            "screenPageViews",
            "screenPageViewsPerSession",
            "bounceRate",
        ],
        "custom_reports": [],
    }


@pytest.fixture
def patch_base_class(one_year_ago, config_without_date_range):
    return {"config": config_without_date_range}


@pytest.fixture
def config_gen(config):
    def inner(**kwargs):
        new_config = deepcopy(config)
        # WARNING, no support deep dictionaries
        new_config.update(kwargs)
        return {k: v for k, v in new_config.items() if v is not ...}

    return inner
