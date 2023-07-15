#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
from dataclasses import dataclass
from typing import List, Tuple, Optional, Mapping, Any
from freezegun import freeze_time

from source_stripe import SourceStripe
from airbyte_cdk.testing.scenario_builder import TestScenario, TestScenarioBuilder, MockedHttpRequestsSourceBuilder
from airbyte_cdk.testing import scenario_utils

@dataclass(eq=True, frozen=True)
class RequestDescriptor:
    url: str
    headers: Optional[Mapping[str, str]]
    body: Optional[Mapping[str, Any]]


@dataclass(eq=True, frozen=True)
class ResponseDescriptor:
    status_code: int
    body: Any # FIXME obviously this is not the right type
    headers: Any

#def test_stripe():
#    assert False


def read_request_response_mapping_from_file(file_path: str) -> Mapping[RequestDescriptor, List[ResponseDescriptor]]:
    with open(file_path) as f:
        mapping = {}
        lines = f.readlines()
        for line in lines:
            obj = json.loads(line)
            req = obj[0]
            res = obj[1]
            mapping_as_tuple = [
                (RequestDescriptor(url=req[0], headers=req[1], body=req[2]), ResponseDescriptor(status_code=res[0], body=res[1], headers=res[2]))
            ]
            for req, res in mapping_as_tuple:
                mapping.setdefault(req, []).append(res)
        return mapping

def read_records_from_read_output_file(file_path, streams):
    all_records = []
    replace = {
        "acct_1JwnoiEcXtiJtvvh": "my_stripe_account_id",
    }
    with open(file_path) as f:
        lines = f.readlines()

        for line in lines:
            for before, after in replace.items():
                line = line.replace(before, after)
            try:
                obj = json.loads(line)
                if obj["type"] == "RECORD" and obj["record"]["stream"] in streams:
                    all_records.append(obj["record"])
            except:
                pass

    return all_records

def read_catalog_from_file(file_path):
    with open(file_path) as f:
        return json.load(f)["catalog"]


streams = [
    #"accounts",
    #"customers",
    #"charges",
    #"balance_transactions",
    #"products",
    "invoices",
    "invoice_line_items",
]




stripe_scenario = (
    TestScenarioBuilder(lambda builder: MockedHttpRequestsSourceBuilder(builder, SourceStripe()))
    .set_name("stripe")
    .set_config({
        "client_secret": "my_stripe_secret",
        "account_id": "my_stripe_account_id",
        "start_date": "2020-05-01T00:00:00Z",
        "streams": [
            {"name": s} for s in streams
        ], # FIXME we shouldn't need this
    })
    .source_builder.set_request_response_mapping(read_request_response_mapping_from_file("/Users/alex/code/airbyte/airbyte-integrations/connectors/source-stripe/mapping_2.txt"))
    #.source_builder.set_now("2023-07-14 11:08:02.751182")
    .set_expected_catalog(read_catalog_from_file("/Users/alex/code/airbyte/airbyte-integrations/connectors/source-stripe/catalog.json"))
    .set_expected_records(read_records_from_read_output_file("/Users/alex/code/airbyte/airbyte-integrations/connectors/source-stripe/read_output_with_now.jsonl",
                                                             streams))
).build()

@freeze_time("2023-06-09T00:00:00Z")
def test_stripe(capsys, tmp_path, json_spec):
    scenario_utils.test_read(capsys, tmp_path, json_spec, stripe_scenario)
