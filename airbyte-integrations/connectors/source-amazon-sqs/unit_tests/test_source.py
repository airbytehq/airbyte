#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
import logging

import requests_mock
from source_amazon_sqs.run import run
from source_amazon_sqs.source import SourceAmazonSqs

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


CONFIG = {
    "max_batch_size": 10,
    "max_wait_time": 20,
    "visibility_timeout": 21,
    "delete_messages": False,
    "attributes_to_return": "path,iter",
    "queue_url": "https://sqs.eu-west-1.amazonaws.com/123456789012/test-queue",
    "region": "eu-west-1",
    "target": "ReceiveMessage",
    "access_key": "test-access-key",
    "secret_key": "test-secret-key",
}

logger = logging.getLogger("airbyte")


def test_spec():
    spec = SourceAmazonSqs().spec(logger)
    assert {"queue_url", "region", "access_key", "secret_key"}.issubset(spec.connectionSpecification["properties"])


def test_read_signs_request_and_parses_messages():
    catalog = CatalogBuilder().with_stream("QueueMessages", SyncMode.full_refresh).build()
    response = {"Messages": [{"MessageId": "m-1", "Body": "hello", "Attributes": {"SentTimestamp": "1"}}]}

    with requests_mock.Mocker() as m:
        m.post("https://sqs.eu-west-1.amazonaws.com/", [{"json": response}, {"json": {}}])
        output = read(SourceAmazonSqs(catalog=catalog, config=CONFIG, state=None), CONFIG, catalog)

    assert not output.errors
    records = [r.record.data for r in output.records]
    assert records[0]["id"] == "m-1"
    assert records[0]["body"] == "hello"
    assert records[0]["attributes"] == {"SentTimestamp": "1"}

    request = m.request_history[0]
    assert request.headers["X-Amz-Target"] == "AmazonSQS.ReceiveMessage"
    assert request.headers["Content-Type"] == "application/x-amz-json-1.0"
    assert request.headers["Authorization"].startswith("AWS4-HMAC-SHA256 Credential=test-access-key/")
    assert "/eu-west-1/sqs/aws4_request" in request.headers["Authorization"]
    assert "X-Amz-Date" in request.headers
    body = json.loads(request.body)
    assert body["QueueUrl"] == CONFIG["queue_url"]
    assert body["AttributeNames"] == ["path", "iter"]
    assert body["MaxNumberOfMessages"] == 10


def test_run_check_passes_config_to_source(tmp_path, capsys, mocker):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(CONFIG))
    mocker.patch("sys.argv", ["source-amazon-sqs", "check", "--config", str(config_path)])

    with requests_mock.Mocker() as m:
        m.post("https://sqs.eu-west-1.amazonaws.com/", json={"Messages": [{"MessageId": "m-1", "Body": "hello"}]})
        run()

    messages = [json.loads(line) for line in capsys.readouterr().out.splitlines() if line.startswith("{")]
    statuses = [msg["connectionStatus"] for msg in messages if msg["type"] == "CONNECTION_STATUS"]
    assert statuses == [{"status": "SUCCEEDED"}]
