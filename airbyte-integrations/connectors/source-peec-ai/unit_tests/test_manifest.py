"""Exercise manifest.yaml against a mock Peec API, without touching the real one.

Covers the behaviour a YAML syntax check cannot: the x-api-key header, month-aligned
slicing, offset pagination inside the POST body, the AddFields transforms, primary-key
uniqueness, record/schema conformance, and incremental resume.

The mock deliberately mimics a **project-scoped** key, which is what we deploy: it
rejects GET /projects with 403 the way the real API does, so a regression that
reintroduces a dependency on that endpoint fails here rather than in production.

Run it after any edit to manifest.yaml:

    python3 -m venv .venv && .venv/bin/pip install airbyte-cdk==7.10.1 jsonschema pyyaml
    .venv/bin/python unit_tests/test_manifest.py

Pin the CDK to the version in metadata.yaml's baseImage so the test runs on the same
runtime as the shipped image.
"""

import json
import logging
import os
import re
import sys
import threading
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, HTTPServer

import yaml
from jsonschema import Draft7Validator

HERE = os.path.dirname(os.path.abspath(__file__))
CONNECTOR = os.path.dirname(HERE)
MANIFEST = os.path.join(CONNECTOR, "manifest.yaml")
CATALOG = os.path.join(CONNECTOR, "integration_tests", "configured_catalog.json")

API_KEY = "test-key"
PAGE_SIZE = 2          # forced down so offset pagination actually triggers
ROWS_PER_WINDOW = 5    # > PAGE_SIZE, so several pages are needed per window
LOG = logging.getLogger("test_manifest")

BRANDS = [
    {"id": "kw_own", "name": "Acme", "domains": ["acme.example"], "aliases": [],
     "regex": None, "is_own": True, "color": "#123456", "source": None},
    {"id": "kw_rival", "name": "Rival", "domains": ["rival.com"], "aliases": [],
     "regex": None, "is_own": False, "color": "#654321", "source": None},
]
MODEL_CHANNELS = [
    {"id": "openai-0", "description": "ChatGPT", "current_model": {"id": "gpt-x"},
     "is_active": True, "unsupported_country_codes": []},
    {"id": "openai-1", "description": "ChatGPT Search", "current_model": {"id": "gpt-y"},
     "is_active": True, "unsupported_country_codes": ["CN"]},
]

requests_log = defaultdict(list)


def _rows(kind, body):
    """A page of fake report rows for the window the connector asked for."""
    month = body["start_date"][:7] + "-01"
    offset = body.get("offset") or 0
    limit = body.get("limit", 1000)
    out = []
    for i in range(ROWS_PER_WINDOW):
        row = {"month": month, "model_channel": {"id": f"openai-{i % 2}"},
               "country_code": "FR"}
        if kind == "brands":
            row |= {"brand": {"id": f"kw_{i}", "name": f"Brand {i}"},
                    "visibility": 0.25, "visibility_count": 5, "visibility_total": 20,
                    "share_of_voice": 0.1, "mention_count": 3, "sentiment": 70.0,
                    "sentiment_sum": 140.0, "sentiment_count": 2, "position": 2.0,
                    "position_sum": 4.0, "position_count": 2}
        elif kind == "domains":
            row |= {"domain": f"example{i}.com", "classification": "EDITORIAL",
                    "retrieval_count": 12, "retrieval_rate": 0.4,
                    "retrieved_percentage": 0.4, "retrieved_chat_count": 4,
                    "total_chat_count": 10, "citation_count": 3, "citation_rate": 0.3,
                    "mentioned_brands": [{"id": "kw_own"}]}
        else:
            row |= {"url": f"https://example{i}.com/page", "classification": "ARTICLE",
                    "title": f"Page {i}", "channel_title": None, "retrieval_count": 7,
                    "citation_count": 2, "citation_rate": 0.28,
                    "mentioned_brands": [{"id": "kw_own"}]}
        out.append(row)
    return out[offset:offset + limit]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, payload, code=200):
        raw = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _authenticated(self):
        if self.headers.get("x-api-key") != API_KEY:
            self._send({"message": "unauthorized"}, 401)
            return False
        return True

    def do_GET(self):
        if not self._authenticated():
            return
        path, _, qs = self.path.partition("?")
        params = dict(p.split("=", 1) for p in qs.split("&") if "=" in p)
        # A project-scoped key cannot list projects. Mirror the real 403 so a
        # regression that depends on this endpoint fails loudly here.
        if path == "/customer/v1/projects":
            requests_log["projects"].append(params)
            return self._send({"message": "Not a Company API Key"}, 403)
        if path == "/customer/v1/brands":
            requests_log["brands_lookup"].append(params)
            rows = BRANDS
        elif path == "/customer/v1/model-channels":
            requests_log["model_channels"].append(params)
            rows = MODEL_CHANNELS
        else:
            return self._send({"message": "not found"}, 404)
        offset, limit = int(params.get("offset", 0)), int(params.get("limit", 1000))
        self._send({"data": rows[offset:offset + limit]})

    def do_POST(self):
        if not self._authenticated():
            return
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        match = re.fullmatch(r"/customer/v1/reports/(brands|domains|urls)", self.path)
        if not match:
            return self._send({"message": "not found"}, 404)
        requests_log[match.group(1)].append(body)
        self._send({"data": _rows(match.group(1), body)})


class Checker:
    def __init__(self):
        self.failures = []

    def __call__(self, label, ok, detail=""):
        print(f"  {'PASS' if ok else 'FAIL'}  {label}" + (f"  -> {detail}" if detail and not ok else ""))
        if not ok:
            self.failures.append(label)


def main():
    server = HTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()

    with open(MANIFEST) as fh:
        manifest = yaml.safe_load(fh)
    manifest["definitions"]["base_requester"]["url_base"] = f"http://127.0.0.1:{port}/customer/v1"
    # The mock serves tiny pages so pagination is exercised over a handful of
    # rows. Pin the shipped values first -- otherwise this override hides a
    # regression in the real page_size, which must stay at the API maximum
    # (limit=10000 is accepted, 15000 answers 400). That the *ordering* is
    # stable at that size is proved live by
    # integration_tests/check_paging_stability.py; it cannot be shown here,
    # because the mock defines its own order.
    shipped_report = manifest["definitions"]["report_paginator"]["pagination_strategy"]["page_size"]
    shipped_lookup = manifest["definitions"]["lookup_paginator"]["pagination_strategy"]["page_size"]
    assert shipped_report == 10000, (
        "report_paginator page_size is %r, expected 10000 (the API maximum)" % shipped_report
    )
    assert shipped_lookup == 1000, (
        "lookup_paginator page_size is %r, expected 1000" % shipped_lookup
    )

    manifest["definitions"]["report_paginator"]["pagination_strategy"]["page_size"] = PAGE_SIZE
    manifest["definitions"]["lookup_paginator"]["pagination_strategy"]["page_size"] = PAGE_SIZE

    from airbyte_cdk.models import (
        AirbyteStateMessageSerializer,
        ConfiguredAirbyteCatalogSerializer,
    )
    from airbyte_cdk.sources.declarative.concurrent_declarative_source import (
        ConcurrentDeclarativeSource,
    )

    # Deliberately mid-month: the manifest must snap it back to the 1st.
    config = {"api_key": API_KEY, "start_date": "2025-11-17"}
    with open(CATALOG) as fh:
        catalog = ConfiguredAirbyteCatalogSerializer.load(json.load(fh))
    source = ConcurrentDeclarativeSource(
        source_config=manifest, config=config, catalog=catalog, state=None
    )
    check = Checker()

    print("\n== spec ==")
    spec = source.spec(LOG).connectionSpecification
    check("requires api_key + start_date", spec["required"] == ["api_key", "start_date"])
    check("project_id is optional", "project_id" in spec["properties"]
          and "project_id" not in spec["required"])
    check("api_key is a secret", spec["properties"]["api_key"].get("airbyte_secret") is True)

    print("\n== check ==")
    check("check returns SUCCEEDED", source.check(LOG, config).status.value == "SUCCEEDED")

    print("\n== discover ==")
    streams = {s.name: s for s in source.discover(LOG, config).streams}
    check("5 streams", set(streams) == {"brands", "model_channels", "brands_report",
                                        "domains_report", "urls_report"}, str(set(streams)))
    for name in ("brands_report", "domains_report", "urls_report"):
        check(f"{name} incremental on month",
              "incremental" in [m.value for m in streams[name].supported_sync_modes]
              and streams[name].default_cursor_field == ["month"])

    print("\n== read ==")
    records, states = defaultdict(list), defaultdict(list)
    for msg in source.read(LOG, config, catalog, None):
        if msg.type.value == "RECORD":
            records[msg.record.stream].append(msg.record.data)
        elif msg.type.value == "STATE" and msg.state.stream:
            states[msg.state.stream.stream_descriptor.name].append(msg.state.stream.stream_state)
    for name in streams:
        check(f"{name} produced records", records[name], f"{len(records[name])} records")

    print("\n-- never calls the company-only endpoint --")
    check("GET /projects was never requested", not requests_log["projects"],
          f"{len(requests_log['projects'])} calls")

    print("\n-- own brand is identifiable --")
    own = [b for b in records["brands"] if b.get("is_own")]
    check("exactly one is_own brand", len(own) == 1 and own[0]["name"] == "Acme")

    print("\n-- month-aligned slicing --")
    windows = sorted({(b["start_date"], b["end_date"]) for b in requests_log["brands"]})
    check("every slice starts on the 1st",
          all(s.endswith("-01") for s, _ in windows), str(windows[:3]))
    check("no slice straddles two months",
          all(s[:7] == e[:7] for s, e in windows),
          str([w for w in windows if w[0][:7] != w[1][:7]][:3]))
    check("mid-month start_date snapped back to 2025-11-01", windows[0][0] == "2025-11-01",
          windows[0][0])
    print(f"     {windows[0]} .. {windows[-1]}  ({len(windows)} slices)")

    print("\n-- offset pagination --")
    offsets = sorted({b.get("offset", 0) for b in requests_log["brands"]})
    check("offsets walked 0,2,4", offsets == [0, 2, 4], str(offsets))
    check("limit sent in POST body",
          all(b.get("limit") == PAGE_SIZE for b in requests_log["brands"]))
    check("all rows per window collected",
          len(records["brands_report"]) == len(windows) * ROWS_PER_WINDOW,
          str(len(records["brands_report"])))
    check("dimensions are month + model_channel_id",
          all(b.get("dimensions") == ["month", "model_channel_id"] for b in requests_log["brands"]))
    # The API rejects an explicit null project_id with 400 ("expected string,
    # received null"), so an unset config must leave the field out altogether
    # rather than send null. A project-scoped key then resolves its own project.
    check("project_id omitted entirely when unset (never null)",
          all("project_id" not in b for b in requests_log["brands"]),
          str([b.get("project_id") for b in requests_log["brands"][:3]]))

    print("\n-- AddFields transforms --")
    rec = records["brands_report"][0]
    check("brand_id flattened", rec.get("brand_id") == rec["brand"]["id"])
    check("brand_name flattened", rec.get("brand_name") == rec["brand"]["name"])
    check("model_channel_id flattened",
          rec.get("model_channel_id") == rec["model_channel"]["id"])
    check("no 'None' string leaked in",
          not any(v == "None" for v in rec.values() if isinstance(v, str)))

    print("\n-- primary keys --")
    keys = {"brands": ["id"],
            "model_channels": ["id"],
            "brands_report": ["month", "brand_id", "model_channel_id"],
            "domains_report": ["month", "domain", "model_channel_id"]}
    for name, key in keys.items():
        seen = [tuple(r.get(k) for k in key) for r in records[name]]
        check(f"{name} PK unique ({len(seen)} rows)", len(seen) == len(set(seen)),
              f"{len(seen) - len(set(seen))} duplicates")
        check(f"{name} PK never null", all(all(p is not None for p in s) for s in seen))
    # urls_report deliberately declares no primary key: the live API returns rows
    # that are identical across every exposed dimension but differ in metrics.
    check("urls_report declares no primary key",
          not streams["urls_report"].source_defined_primary_key,
          str(streams["urls_report"].source_defined_primary_key))

    print("\n-- schema conformance --")
    for name in streams:
        validator = Draft7Validator(streams[name].json_schema)
        errors = [e.message for r in records[name] for e in validator.iter_errors(r)]
        check(f"{name} records conform", not errors, str(errors[:3]))

    print("\n== incremental resume (monthly refresh) ==")
    final_state = json.loads(json.dumps(
        states["brands_report"][-1], default=lambda o: getattr(o, "__dict__", str(o))))
    print(f"     state: {json.dumps(final_state.get('state'))}")
    requests_log["brands"].clear()
    resume = [AirbyteStateMessageSerializer.load(
        {"type": "STREAM",
         "stream": {"stream_descriptor": {"name": "brands_report"},
                    "stream_state": final_state}})]
    resumed = ConcurrentDeclarativeSource(
        source_config=manifest, config=config, catalog=catalog, state=resume
    )
    for _ in resumed.read(LOG, config, catalog, resume):
        pass
    months = sorted({b["start_date"][:7] for b in requests_log["brands"]})
    all_months = sorted({s[:7] for s, _ in windows})
    check("resume re-reads only the tail", len(months) < len(all_months),
          f"{len(months)} of {len(all_months)} months")
    check("resume re-reads the previous month (lookback P1M)", len(months) >= 2, str(months))
    check("resume covers the current month", months[-1] == all_months[-1], str(months))
    print(f"     months re-read: {months}")

    print("\n== company-scoped key mode ==")
    requests_log["brands"].clear()
    company_config = dict(config, project_id="or_company_project")
    company = ConcurrentDeclarativeSource(
        source_config=manifest, config=company_config, catalog=catalog, state=None
    )
    for _ in company.read(LOG, company_config, catalog, None):
        pass
    check("project_id forwarded when the config sets it",
          requests_log["brands"]
          and all(b.get("project_id") == "or_company_project" for b in requests_log["brands"]),
          str({b.get("project_id") for b in requests_log["brands"]}))
    check("lookup streams scope to the project too",
          all(p.get("project_id") == "or_company_project"
              for p in requests_log["brands_lookup"] if "project_id" in p),
          str([p.get("project_id") for p in requests_log["brands_lookup"][:3]]))

    server.shutdown()
    print("\n" + "=" * 60)
    if check.failures:
        print(f"{len(check.failures)} FAILURE(S): {check.failures}")
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
