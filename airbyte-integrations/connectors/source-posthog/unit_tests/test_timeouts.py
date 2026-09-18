# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Event, Thread

import pytest
from requests.exceptions import ReadTimeout
from source_posthog import SourcePosthog
from source_posthog.components import PosthogHTTPAdapter

from airbyte_cdk.models import SyncMode


@pytest.mark.parametrize("always_stall", [False, True])
def test_stalled_http_request_retries_then_recovers_or_fails(monkeypatch, mocker, tmp_path, always_stall):
    attempts = []
    release = Event()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            attempts.append(self.path)
            if always_stall or len(attempts) == 1:
                release.wait(5)
                return
            body = json.dumps({"results": [{"id": "one"}], "next": None}).encode()
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    monkeypatch.setattr(PosthogHTTPAdapter, "timeout", (0.1, 0.1))
    monkeypatch.setenv("REQUEST_CACHE_PATH", str(tmp_path))
    mocker.patch("airbyte_cdk.sources.streams.http.rate_limiting.time.sleep")
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        config = {"api_key": "test", "base_url": f"http://127.0.0.1:{server.server_port}", "start_date": "2026-09-01T00:00:00Z"}
        persons = next(stream for stream in SourcePosthog().streams(config) if stream.name == "persons")
        if always_stall:
            with pytest.raises(ReadTimeout):
                list(persons.read_records(SyncMode.full_refresh, stream_slice={"id": 42}))
            assert len(attempts) == 6
        else:
            records = list(persons.read_records(SyncMode.full_refresh, stream_slice={"id": 42}))
            assert [record["id"] for record in records] == ["one"]
            assert len(attempts) == 2
        assert len(set(attempts)) == 1
    finally:
        release.set()
        server.shutdown()
        server.server_close()
        worker.join()
