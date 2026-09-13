"""Live SAP fixtures.

Tests here talk to a real SAP system -- by default the local ABAP Platform Trial.
Nothing is mocked. They skip (with a stated reason) when the environment does not
name a system, following the same convention as the erpl repository: a variable
must be **absent** to skip, not empty.
"""

from __future__ import annotations

import os
import subprocess
import sys

import pytest

EXTENSION_DIR = os.environ.get("ERPL_EXTENSION_DIR")


def _env(name: str) -> str | None:
    value = os.environ.get(name)
    return value if value else None


@pytest.fixture(scope="session", autouse=True)
def erpl_extensions() -> str:
    if not EXTENSION_DIR:
        pytest.skip("ERPL_EXTENSION_DIR is not set; run ./bin/fetch-extensions.sh first.")
    if not os.path.isdir(EXTENSION_DIR):
        pytest.skip(f"ERPL_EXTENSION_DIR={EXTENSION_DIR} does not exist.")
    return EXTENSION_DIR


@pytest.fixture(scope="session")
def sap_rfc_config() -> dict:
    ashost = _env("ERPL_SAP_ASHOST")
    if not ashost:
        pytest.skip("ERPL_SAP_ASHOST is not set; no SAP system to test against.")
    return {
        "ashost": ashost,
        "sysnr": _env("ERPL_SAP_SYSNR") or "00",
        "client": _env("ERPL_SAP_CLIENT") or "001",
        "user": _env("ERPL_SAP_USER") or "DEVELOPER",
        "password": _env("ERPL_SAP_PASSWORD") or "",
        "lang": _env("ERPL_SAP_LANG") or "EN",
        "concurrency": 2,
    }


@pytest.fixture(scope="session")
def sap_base_url() -> str:
    url = _env("ERPL_SAP_BASE_URL")
    if not url:
        pytest.skip("ERPL_SAP_BASE_URL is not set.")
    return url


@pytest.fixture(scope="session")
def odp_target() -> tuple[str, str]:
    context, name = _env("ERPL_SAP_ODP_CONTEXT"), _env("ERPL_SAP_ODP_NAME")
    if not (context and name):
        pytest.skip(
            "ERPL_SAP_ODP_CONTEXT / ERPL_SAP_ODP_NAME are not set. A stock system has no "
            "provisioned ODP object; see the erpl-web docs for how to create one."
        )
    return context, name


@pytest.fixture(scope="session")
def odp_odata_url() -> str:
    url = _env("ERPL_SAP_ODP_ODATA_URL")
    if not url:
        pytest.skip("ERPL_SAP_ODP_ODATA_URL is not set; no provisioned ODP OData service.")
    return url


@pytest.fixture(scope="session")
def bics_cube() -> str:
    cube = _env("ERPL_SAP_BICS_CUBE")
    if not cube:
        pytest.skip("ERPL_SAP_BICS_CUBE is not set; no BW InfoProvider to test against.")
    return cube


def run_connector(
    command: str, *, config: dict, catalog: dict | None = None, state: list | None = None, tmp_path
) -> list[dict]:
    """Run the connector exactly as the platform does: a subprocess over stdout.

    Going through the real entrypoint is the point -- it exercises argument
    parsing, secret filtering, serialization and the concurrent read loop.
    """
    import json

    args = [sys.executable, "-m", "source_sap.run", command]
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config))
    args += ["--config", str(config_file)]
    if catalog is not None:
        catalog_file = tmp_path / "catalog.json"
        catalog_file.write_text(json.dumps(catalog))
        args += ["--catalog", str(catalog_file)]
    if state is not None:
        state_file = tmp_path / "state.json"
        state_file.write_text(json.dumps(state))
        args += ["--state", str(state_file)]

    env = dict(os.environ)
    if EXTENSION_DIR:
        env["ERPL_EXTENSION_DIR"] = EXTENSION_DIR
        env.setdefault("LD_LIBRARY_PATH", os.path.join(EXTENSION_DIR, "v1.5.5", "linux_amd64"))
    proc = subprocess.run(args, capture_output=True, text=True, env=env, timeout=1800)
    messages = []
    unparsed = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        if not line.startswith("{"):
            unparsed.append(line)
            continue
        try:
            messages.append(json.loads(line))
        except json.JSONDecodeError:
            unparsed.append(line)

    # A crash after some records were emitted would otherwise slip past an
    # `errors(messages) == []` assertion, because the traceback is not a protocol
    # message. Surface a non-zero exit unless the connector reported the failure
    # properly as an ERROR trace.
    reported = any(m.get("type") == "TRACE" and m.get("trace", {}).get("type") == "ERROR" for m in messages)
    if proc.returncode != 0 and not reported:
        # A negative code is a signal. -9 in particular is the OOM killer, and
        # it reads as a connector defect unless it is named: the partial output
        # looks exactly like a short read.
        killed = (
            f" (killed by signal {-proc.returncode}"
            + ("; -9 is usually the OOM killer -- check free memory on this host" if proc.returncode == -9 else "")
            + ")"
            if proc.returncode < 0
            else ""
        )
        raise AssertionError(
            f"connector exited {proc.returncode}{killed} without an ERROR trace message\n"
            f"unparsed stdout:\n" + "\n".join(unparsed[-20:]) + "\n"
            f"stderr:\n{proc.stderr[-4000:]}"
        )
    if not messages:
        raise AssertionError(f"connector produced no messages (exit {proc.returncode})\nstderr:\n{proc.stderr[-4000:]}")
    return messages


def records(messages: list[dict], stream: str | None = None) -> list[dict]:
    return [
        m["record"]
        for m in messages
        if m.get("type") == "RECORD" and (stream is None or m["record"]["stream"] == stream)
    ]


def states(messages: list[dict], stream: str | None = None) -> list[dict]:
    out = []
    for m in messages:
        if m.get("type") != "STATE":
            continue
        blob = m["state"].get("stream") or {}
        if stream is None or blob.get("stream_descriptor", {}).get("name") == stream:
            out.append(m["state"])
    return out


def errors(messages: list[dict]) -> list[dict]:
    return [m["trace"] for m in messages if m.get("type") == "TRACE" and m["trace"].get("type") == "ERROR"]
