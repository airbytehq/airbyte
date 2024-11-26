import contextlib
import json
import logging
import subprocess
import time
from importlib import metadata
from pathlib import Path
from typing import cast

import dagger
from dagger._managers import SyncResource

from .conn import ConnectParams

logger = logging.getLogger(__name__)


OS_ETXTBSY = 26


def get_sdk_version():
    try:
        return metadata.version("dagger-io")
    except metadata.PackageNotFoundError:
        return "n/a"


def start_cli_session(cfg: dagger.Config, path: str):
    # TODO: Convert calling session subprocess to async.
    return SyncResource(start_cli_session_sync(cfg, path))


@contextlib.contextmanager
def start_cli_session_sync(cfg: dagger.Config, path: str):
    """Start an engine session with a provided CLI path."""
    logger.debug("Starting session using %s", path)
    try:
        with run(cfg, path) as proc:
            yield get_connect_params(proc)
    except (OSError, ValueError, TypeError) as e:
        raise dagger.SessionError(e) from e


def run(cfg: dagger.Config, path: str) -> subprocess.Popen[str]:
    args = [
        path,
        "session",
        "--label",
        "dagger.io/sdk.name:python",
        "--label",
        f"dagger.io/sdk.version:{get_sdk_version()}",
    ]
    if cfg.workdir:
        args.extend(["--workdir", str(Path(cfg.workdir).absolute())])
    if cfg.config_path:
        args.extend(["--project", str(Path(cfg.config_path).absolute())])

    # Retry starting if "text file busy" error is hit. That error can happen
    # due to a flaw in how Linux works: if any fork of this process happens
    # while the temp binary file is open for writing, a child process can
    # still have it open for writing before it calls exec.
    # See this golang issue (which itself links to bug reports in other
    # langs and the kernel): https://github.com/golang/go/issues/22315
    # Unfortunately, this sort of retry loop is the best workaround. The
    # case is obscure enough that it should not be hit very often at all.
    for _ in range(10):
        try:
            proc = subprocess.Popen(
                args,  # noqa: S603
                bufsize=0,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=cfg.log_output or subprocess.PIPE,
                encoding="utf-8",
            )
        except OSError as e:  # noqa: PERF203
            if e.errno != OS_ETXTBSY:
                raise
            logger.warning("file busy, retrying in 0.1 seconds...")
            time.sleep(0.1)
        else:
            return proc

    msg = "CLI busy"
    raise dagger.SessionError(msg)


def get_connect_params(proc: subprocess.Popen[str]) -> ConnectParams:
    # TODO: implement engine session timeout (self.cfg.engine_timeout?)
    assert proc.stdout
    conn = proc.stdout.readline()

    # Check if subprocess exited with an error
    if proc.poll():
        stdout = conn + proc.stdout.read()
        msg = make_process_error_msg(proc, stdout)
        raise dagger.SessionError(msg)

    if not conn:
        msg = "No connection params"
        raise dagger.SessionError(msg)

    try:
        return ConnectParams(**json.loads(conn))
    except (ValueError, TypeError) as e:
        msg = f"Invalid connection params: {conn}"
        raise dagger.SessionError(msg) from e


def make_process_error_msg(proc: subprocess.Popen[str], out: str) -> str:
    err = proc.stderr.read() if proc.stderr and proc.stderr.readable() else None
    args = cast(list[str], proc.args)

    # Reuse error message from CalledProcessError
    exc = subprocess.CalledProcessError(proc.returncode, " ".join(args))

    msg = str(exc)
    detail = err or out
    if detail and detail.strip():
        # `msg` ends in a period, just append
        msg = f"{msg} {detail.strip()}"

    return msg
