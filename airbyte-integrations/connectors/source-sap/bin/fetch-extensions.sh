#!/usr/bin/env bash
# Download and pre-warm the ERPL DuckDB extensions.
#
# `erpl` is a trampoline: loading it once unpacks erpl_rfc / erpl_bics / erpl_odp
# and the SAP + ICU shared libraries into the extension directory. After that the
# 180 MB trampoline is dead weight, so it is deleted.
#
# The download runs through Python rather than curl, because the Airbyte
# connector base image ships neither curl nor wget.
#
# The artifacts are unsigned DuckDB extensions loaded as native code, so they are
# fetched over HTTPS and verified against pinned checksums. A mismatch fails the
# build rather than shipping an unverified binary.
set -euo pipefail

TARGET="${1:-${ERPL_EXTENSION_DIR:-/airbyte/duckdb_extensions}}"
export DUCKDB_VERSION="${DUCKDB_VERSION:-v1.5.5}"
export ERPL_PLATFORM="${ERPL_PLATFORM:-linux_amd64}"
export ERPL_REPO="${ERPL_REPO:-https://get.erpl.io}"
# Set to 1 only when deliberately moving to a new ERPL version, to print the new
# checksums before pinning them in checksums.txt.
export ERPL_ALLOW_UNPINNED="${ERPL_ALLOW_UNPINNED:-0}"
# The pre-warm step must run on a duckdb matching DUCKDB_VERSION, because the
# trampoline unpacks into a version-named directory. Prefer the project venv.
_here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-$( [ -x "${_here}/../.venv/bin/python" ] && echo "${_here}/../.venv/bin/python" || echo python3 )}"

export ERPL_CHECKSUM_FILE="${ERPL_CHECKSUM_FILE:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/checksums.txt}"

"${PYTHON}" - "$TARGET" <<'PY'
import gzip
import hashlib
import os
import pathlib
import shutil
import sys
import urllib.request

target = pathlib.Path(sys.argv[1])
duckdb_version = os.environ["DUCKDB_VERSION"]
platform = os.environ["ERPL_PLATFORM"]
repo = os.environ["ERPL_REPO"].rstrip("/")

dest = target / duckdb_version / platform
dest.mkdir(parents=True, exist_ok=True)

allow_unpinned = os.environ.get("ERPL_ALLOW_UNPINNED") == "1"
checksums = {}
checksum_file = pathlib.Path(os.environ["ERPL_CHECKSUM_FILE"])
if checksum_file.exists():
    for line in checksum_file.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            digest, key = line.split(None, 1)
            checksums[key.strip()] = digest

for name in ("erpl", "erpl_web"):
    url = f"{repo}/{duckdb_version}/{platform}/{name}.duckdb_extension.gz"
    key = f"{duckdb_version}/{platform}/{name}.duckdb_extension.gz"
    print(f"fetching {url}", flush=True)
    with urllib.request.urlopen(url, timeout=300) as response:
        payload = response.read()

    digest = hashlib.sha256(payload).hexdigest()
    expected = checksums.get(key)
    if expected is None:
        if not allow_unpinned:
            raise SystemExit(
                f"no pinned checksum for {key}.\n"
                f"  measured: {digest}\n"
                "Add it to bin/checksums.txt, or re-run with ERPL_ALLOW_UNPINNED=1 to "
                "print checksums when moving to a new ERPL version."
            )
        print(f"  UNPINNED {digest}  {key}", flush=True)
    elif digest != expected:
        raise SystemExit(
            f"checksum mismatch for {key}\n  expected: {expected}\n  measured: {digest}"
        )

    import io

    with gzip.GzipFile(fileobj=io.BytesIO(payload)) as unpacked, open(
        dest / f"{name}.duckdb_extension", "wb"
    ) as out:
        shutil.copyfileobj(unpacked, out)

print("pre-warming the trampoline", flush=True)
import duckdb  # noqa: E402 - only needed once the binaries are on disk

installed = f"v{duckdb.__version__}"
if installed != duckdb_version:
    raise SystemExit(
        f"the duckdb running this script is {installed}, but the extensions were "
        f"fetched for {duckdb_version}. The trampoline unpacks into a directory named "
        f"after the running version, so these must match. Run it with a matching "
        f"interpreter (PYTHON=... ) or set DUCKDB_VERSION={installed}."
    )

con = duckdb.connect(
    config={"allow_unsigned_extensions": "true", "extension_directory": str(target)}
)
con.load_extension("erpl")  # unpacks erpl_rfc / erpl_bics / erpl_odp + SAP libs
con.load_extension("erpl_web")
con.close()

# The trampoline has served its purpose; the sub-extensions load directly as long
# as LD_LIBRARY_PATH points at this directory.
(dest / "erpl.duckdb_extension").unlink(missing_ok=True)

print(f"extensions ready in {dest}:", flush=True)
for path in sorted(dest.iterdir()):
    print(f"  {path.name}  {path.stat().st_size // 1024 // 1024} MB", flush=True)
PY
