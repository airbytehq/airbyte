# Copyright (c) 2026 Albert Wong
# SPDX-License-Identifier: MIT
#!/usr/bin/env python3
"""Disposable Redis Software -> source CLI -> Airbyte destination -> PostgreSQL.

Requires Python 3.11+, Docker, and a built source image. No cloud credentials.
All containers and the private network are removed, including after failure.
Only the Software management API is published, on a random localhost port.
"""

import argparse
import json
import ssl
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path


SOFTWARE = "redislabs/redis:8.2.0-78.18"
POSTGRES = "postgres:16.10"
DESTINATION = "airbyte/destination-postgres:3.0.23@sha256:1a122ed76f97b45fcdf7a8183bed93330a8f8eedad365e883d738774a35d69ea"


def docker(*args, stdin=None, check=True):
    result = subprocess.run(["docker", *args], input=stdin, text=True, capture_output=True)
    if check and result.returncode:
        raise RuntimeError(f"Docker command {args[:2]} failed:\n{result.stdout[-6000:]}\n{result.stderr[-2000:]}")
    return result


def wait_for(description, predicate, seconds=240):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            value = predicate()
            if value:
                return value
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError):
            pass
        time.sleep(2)
    raise RuntimeError(f"Timed out waiting for {description}")


def bootstrap(name):
    port = docker("port", name, "9443/tcp").stdout.strip().rsplit(":", 1)[1]
    base = f"https://127.0.0.1:{port}/v1"
    # Fixed credentials are confined to this disposable local test cluster.
    import base64

    auth = base64.b64encode(b"admin@example.com:airbyte-local-test").decode()

    def api(path, body=None):
        request = urllib.request.Request(
            base + path,
            data=json.dumps(body).encode() if body is not None else None,
            headers={"Authorization": "Basic " + auth, "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, context=ssl._create_unverified_context(), timeout=10) as response:
            return json.load(response)

    requested = False

    def ready():
        nonlocal requested
        state = api("/bootstrap")["bootstrap_status"]["state"]
        if state == "completed":
            return True
        if state == "failed":
            raise RuntimeError("Redis Software bootstrap failed")
        if state == "idle" and not requested:
            api(
                "/bootstrap/create_cluster",
                {
                    "action": "create_cluster",
                    "cluster": {"name": "airbyte-test.local"},
                    "node": {},
                    "credentials": {"username": "admin@example.com", "password": "airbyte-local-test"},
                },
            )
            requested = True
        return False

    wait_for("Redis Software bootstrap", ready)
    body = {
        "name": "airbyte-test",
        "type": "redis",
        "redis_version": "8.6",
        "port": 12000,
        "memory_size": 1073741824,
        "replication": False,
        "data_persistence": "disabled",
        "eviction_policy": "noeviction",
        "shards_count": 1,
        "sharding": False,
        "query_performance_factor": {"active": True, "scaling_factor": 4},
    }
    uid = wait_for("Redis Software database creation", lambda: api("/bdbs", body)["uid"])
    wait_for("Redis Software database", lambda: api(f"/bdbs/{uid}")["status"] == "active")
    database = api(f"/bdbs/{uid}")
    if database["eviction_policy"] != "noeviction" or database["query_performance_factor"]["scaling_factor"] != 4:
        raise RuntimeError("Redis Software test policy/QPF validation failed")
    wait_for(
        "Redis Search",
        lambda: docker("exec", name, "/opt/redislabs/bin/redis-cli", "-e", "-p", "12000", "FT._LIST", check=False).returncode == 0,
    )


def messages(output):
    result = []
    for line in output.splitlines():
        try:
            result.append(json.loads(line))
        except ValueError:
            continue  # Destination JVM startup diagnostics are not protocol data.
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-image", default="airbyte/source-redis-adbc:0.1.0")
    parser.add_argument("--test-image", help="Optional test image to run the three native Redis tests on the disposable server")
    args = parser.parse_args()
    suffix = uuid.uuid4().hex[:10]
    network = "airbyte-e2e-" + suffix
    redis = network + "-redis"
    postgres = network + "-postgres"
    source = args.source_image
    table = "airbyte_e2e_" + suffix
    empty = table + "_empty"
    docker("network", "create", network)
    try:
        docker("run", "-d", "--name", redis, "--network", network, "--cap-add", "SYS_RESOURCE", "-p", "127.0.0.1::9443", SOFTWARE)
        docker(
            "run",
            "-d",
            "--name",
            postgres,
            "--network",
            network,
            "-e",
            "POSTGRES_PASSWORD=airbyte-test",
            "-e",
            "POSTGRES_DB=airbyte",
            POSTGRES,
        )
        print("Bootstrapping isolated Redis Software with Search and QPF 4x...", flush=True)
        bootstrap(redis)
        wait_for("PostgreSQL", lambda: docker("exec", postgres, "pg_isready", "-U", "postgres", check=False).returncode == 0)
        if args.test_image:
            native = docker(
                "run",
                "--rm",
                "--network",
                network,
                "-e",
                f"REDIS_URI=redis://{redis}:12000/0",
                args.test_image,
                "-q",
                "integration_tests/test_integration.py",
            )
            print(native.stdout, flush=True)
        with tempfile.TemporaryDirectory(prefix="airbyte-e2e-") as folder:
            config_dir = Path(folder)
            # Test-only credentials/configs, removed when the test finishes.
            config_dir.chmod(0o755)  # Source runs as an unprivileged container user.
            (config_dir / "source.json").write_text(json.dumps({"uri": f"redis://{redis}:12000/0", "batch_size": 2}))
            (config_dir / "destination.json").write_text(
                json.dumps(
                    {
                        "host": postgres,
                        "port": 5432,
                        "database": "airbyte",
                        "schema": "public",
                        "username": "postgres",
                        "password": "airbyte-test",
                        "ssl_mode": {"mode": "disable"},
                        "tunnel_method": {"tunnel_method": "NO_TUNNEL"},
                    }
                )
            )
            base = ["run", "--rm", "--network", network, "-v", f"{folder}:/config:ro"]

            def run_source(*command, check=True):
                return docker(*base, source, *command, check=check)

            assert any(m.get("type") == "SPEC" for m in messages(run_source("spec").stdout))
            seed = f"""import json
from contextlib import closing
from source_redis_adbc.backend import connect
with closing(connect(json.load(open('/config/source.json')))) as c, closing(c.cursor()) as cur:
    cur.execute('CREATE TABLE {table} (id BIGINT, label VARCHAR, amount DECIMAL(30,9), active BOOLEAN, payload BYTEA, created TIMESTAMP)')
    cur.execute("INSERT INTO {table} VALUES (9007199254740993, 'first', 12345678901234567890.123456789, TRUE, X'00FF', TIMESTAMP '2026-11-01 01:02:03.123456'), (2, NULL, NULL, FALSE, NULL, NULL), (3, 'third', 1.000000001, TRUE, X'AB', TIMESTAMP '2026-11-01 00:00:00'), (4, 'fourth', 0, NULL, NULL, NULL), (5, 'fifth', -0.000000001, FALSE, NULL, NULL)")
    cur.execute('CREATE TABLE {empty} (id BIGINT)')
"""
            docker(*base, "-i", "--entrypoint", "python", source, "-", stdin=seed)
            status = messages(run_source("check", "--config", "/config/source.json").stdout)
            assert any(m.get("connectionStatus", {}).get("status") == "SUCCEEDED" for m in status), status
            discovered = next(
                m["catalog"]["streams"]
                for m in messages(run_source("discover", "--config", "/config/source.json").stdout)
                if m.get("type") == "CATALOG"
            )
            configured = {
                "streams": [
                    {
                        "stream": stream,
                        "sync_mode": "full_refresh",
                        "destination_sync_mode": "overwrite",
                        "generation_id": 1,
                        "minimum_generation_id": 1,
                        "sync_id": 1,
                    }
                    for stream in discovered
                    if stream["name"] in (table, empty)
                ]
            }
            assert len(configured["streams"]) == 2
            (config_dir / "catalog.json").write_text(json.dumps(configured))

            # Invalid selected stream must fail; retry uses a fresh full refresh.
            invalid = json.loads(json.dumps(configured))
            invalid["streams"][0]["stream"]["name"] = "missing_airbyte_table"
            (config_dir / "invalid.json").write_text(json.dumps(invalid))
            failed = run_source("read", "--config", "/config/source.json", "--catalog", "/config/invalid.json", check=False)
            assert failed.returncode != 0
            assert not any(m.get("type") == "RECORD" for m in messages(failed.stdout))

            # A failed native connection must not leak URI credentials to stdout/stderr.
            secret = "must-not-appear-in-diagnostics"
            (config_dir / "bad.json").write_text(json.dumps({"uri": f"redis://default:{secret}@127.0.0.1:1/0?dial_timeout=1s"}))
            bad = run_source("check", "--config", "/config/bad.json", check=False)
            assert secret not in bad.stdout + bad.stderr
            assert any(m.get("connectionStatus", {}).get("status") == "FAILED" for m in messages(bad.stdout))

            checked = docker(*base, DESTINATION, "check", "--config", "/config/destination.json")
            assert any(m.get("connectionStatus", {}).get("status") == "SUCCEEDED" for m in messages(checked.stdout)), checked.stdout[-2000:]

            for attempt in range(2):
                # The Airbyte platform supplies these fields in real jobs.
                # Advance the generation for a new overwrite to discard old rows.
                for stream in configured["streams"]:
                    stream.update(generation_id=attempt + 1, minimum_generation_id=attempt + 1, sync_id=attempt + 1)
                (config_dir / "catalog.json").write_text(json.dumps(configured))
                output = run_source("read", "--config", "/config/source.json", "--catalog", "/config/catalog.json").stdout
                records = [m for m in messages(output) if m.get("type") == "RECORD"]
                assert len(records) == 5
                data = {m["record"]["data"]["id"]: m["record"]["data"] for m in records}
                assert data["9007199254740993"]["amount"] == "12345678901234567890.123456789"
                assert data["9007199254740993"]["payload"] == "AP8="
                assert data["9007199254740993"]["created"] == "2026-11-01T01:02:03.123456"
                assert data["2"]["label"] is None
                wire = "".join(json.dumps(record) + "\n" for record in records)
                write = docker(
                    *base,
                    "-i",
                    DESTINATION,
                    "write",
                    "--config",
                    "/config/destination.json",
                    "--catalog",
                    "/config/catalog.json",
                    stdin=wire,
                )
                assert not any(
                    m.get("type") == "TRACE" and m.get("trace", {}).get("type") == "ERROR" for m in messages(write.stdout)
                ), write.stdout[-6000:]
                # Verify final typed destination data, not merely a zero exit code.
                query = f"""SELECT COALESCE(json_agg(t ORDER BY id), '[]'::json)
                    FROM (SELECT id, label, amount, active, payload,
                    to_char(created, 'YYYY-MM-DD\"T\"HH24:MI:SS.US') AS created FROM public.{table}) t"""
                loaded = json.loads(docker("exec", postgres, "psql", "-U", "postgres", "-d", "airbyte", "-Atc", query).stdout)
                expected = [
                    {
                        **row,
                        "created": datetime.fromisoformat(row["created"]).isoformat(timespec="microseconds") if row["created"] else None,
                    }
                    for row in data.values()
                ]
                assert sorted(loaded, key=lambda row: row["id"]) == sorted(expected, key=lambda row: row["id"]), loaded
                assert (
                    docker(
                        "exec", postgres, "psql", "-U", "postgres", "-d", "airbyte", "-Atc", f"SELECT count(*) FROM public.{empty}"
                    ).stdout.strip()
                    == "0"
                )
                print(f"Sync {attempt + 1}: all 5 rows verified in PostgreSQL; empty stream verified.", flush=True)
            print("PASS: native source, failed-read retry, credential sanitization, destination sync and overwrite replay.", flush=True)
    finally:
        docker("rm", "-f", redis, postgres, check=False)
        docker("network", "rm", network, check=False)


if __name__ == "__main__":
    main()
