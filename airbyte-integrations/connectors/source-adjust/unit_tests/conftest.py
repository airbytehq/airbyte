#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from pytest import fixture


@fixture
def config_pass():
    return {
        "ingest_start": "2024-05-20T20:30:40Z",
        "api_token": "token",
        "metrics": ["installs", "network_installs", "network_cost", "network_ecpi"],
        "dimensions": ["app", "partner_name", "campaign", "campaign_id_network", "campaign_network"],
        "additional_metrics": [],
        "until_today": True,
    }


@fixture
def auth_token():
    return {"access_token": "good", "expires_in": 3600}


@fixture
def report_url():
    return "https://dash.adjust.com/control-center/reports-service/report"


@fixture
def mock_report_response():
    return {
        "rows": [
            {
                "attr_dependency": {"campaign_id_network": "unknown", "partner_id": "-300", "partner": "Organic"},
                "app": "Test app",
                "partner_name": "Organic",
                "campaign": "unknown",
                "campaign_id_network": "unknown",
                "campaign_network": "unknown",
                "installs": "10",
                "network_installs": "0",
                "network_cost": "0.0",
                "network_ecpi": "0.0",
            }
        ],
        "totals": {"installs": 10.0, "network_installs": 0.0, "network_cost": 0.0, "network_ecpi": 0.0},
        "warnings": [],
    }
