#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

"""
End-to-end CDC test for Airbyte source-mysql WITHOUT the RELOAD privilege.

Validates that the patched connector can perform initial snapshot and
incremental CDC (INSERT, UPDATE, DELETE) from a MySQL source that does
NOT grant RELOAD to the replication user — as is the case on OCI HeatWave,
Amazon Aurora, Google Cloud SQL, and other managed MySQL services.

Prerequisites (fill in the CONFIG section below):
  - Staging MySQL with binlog enabled:
      log_bin=ON, binlog_format=ROW, binlog_row_image=FULL,
      binlog_row_value_options='' (empty, NOT 'PARTIAL_JSON').

      On OCI HeatWave MySQL the default for binlog_row_value_options is
      PARTIAL_JSON, which causes Debezium to silently drop UPDATE events
      (INSERT and DELETE still flow). Set it to an empty string via the
      OCI custom-configuration parameter group, or at runtime with
      `SET GLOBAL binlog_row_value_options = '';` if the user has
      SYSTEM_VARIABLES_ADMIN. See:
      https://blogs.oracle.com/mysql/heatwave-mysql-solving-missing-updates-for-debezium-cdc

  - MySQL user with: SELECT, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT
    (explicitly NO RELOAD)
  - Staging Snowflake warehouse + database + schema + service-account credentials
  - Airbyte OSS instance with the custom source-mysql image loaded

Usage:
  pip install mysql-connector-python snowflake-connector-python requests
  python test_cdc_no_reload.py
"""

import datetime
import json
import os
import sys
import time
import traceback

import mysql.connector
import requests
import snowflake.connector


# ──────────────────────────────────────────────────────────────────────
# CONFIG — fill in with your staging credentials
# Can also be set via environment variables (shown as fallbacks).
# ──────────────────────────────────────────────────────────────────────

MYSQL_HOST = os.getenv("MYSQL_HOST", "<YOUR_OCI_HEAT_HOST>")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "<YOUR_MYSQL_USER>")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "<YOUR_MYSQL_PASSWORD>")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "<YOUR_MYSQL_DATABASE>")

SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT", "<YOUR_SF_ACCOUNT>")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER", "<YOUR_SF_USER>")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD", "<YOUR_SF_PASSWORD>")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "<YOUR_SF_WAREHOUSE>")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE", "<YOUR_SF_DATABASE>")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", "<YOUR_SF_SCHEMA>")

AIRBYTE_URL = os.getenv("AIRBYTE_URL", "http://localhost:8000")  # Airbyte API base
AIRBYTE_WORKSPACE_ID = os.getenv("AIRBYTE_WORKSPACE_ID", "")  # filled automatically if empty

# Test table name — unique to avoid collisions.
TEST_TABLE = "airbyte_cdc_reload_test"

# How long to wait for an Airbyte sync to finish (seconds).
SYNC_TIMEOUT = 600
SYNC_POLL_INTERVAL = 10

# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────

results: list[dict] = []


def record(test_id: str, passed: bool, detail: str = ""):
    status = "PASS" if passed else "FAIL"
    results.append({"id": test_id, "status": status, "detail": detail})
    print(f"  [{status}] {test_id}{(' -- ' + detail) if detail else ''}")


def abort(msg: str):
    print(f"\nABORT: {msg}")
    print_summary()
    sys.exit(1)


def mysql_conn():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
    )


def sf_conn():
    return snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
    )


def sf_query(sql: str) -> list:
    with sf_conn() as conn:
        cur = conn.cursor()
        try:
            cur.execute(sql)
            return cur.fetchall()
        finally:
            cur.close()


def sf_row_count() -> int:
    rows = sf_query(f'SELECT COUNT(*) FROM "{SNOWFLAKE_DATABASE}"."{SNOWFLAKE_SCHEMA}"."{TEST_TABLE}" WHERE "_AB_CDC_DELETED_AT" IS NULL')
    return rows[0][0]


def sf_total_row_count() -> int:
    rows = sf_query(f'SELECT COUNT(*) FROM "{SNOWFLAKE_DATABASE}"."{SNOWFLAKE_SCHEMA}"."{TEST_TABLE}"')
    return rows[0][0]


def airbyte(method: str, endpoint: str, body: dict | None = None) -> dict:
    url = f"{AIRBYTE_URL}/api/v1/{endpoint}"
    if method == "POST":
        r = requests.post(url, json=body or {}, headers={"Content-Type": "application/json"})
    else:
        r = requests.get(url, params=body)
    r.raise_for_status()
    return r.json()


def get_workspace_id() -> str:
    global AIRBYTE_WORKSPACE_ID
    if AIRBYTE_WORKSPACE_ID:
        return AIRBYTE_WORKSPACE_ID
    data = airbyte("POST", "workspaces/list")
    AIRBYTE_WORKSPACE_ID = data["workspaces"][0]["workspaceId"]
    return AIRBYTE_WORKSPACE_ID


def wait_for_sync(connection_id: str) -> dict:
    """Poll until the latest job for this connection completes. Returns job info."""
    deadline = time.time() + SYNC_TIMEOUT
    while time.time() < deadline:
        jobs = airbyte(
            "POST",
            "jobs/list",
            {
                "configTypes": ["sync"],
                "configId": connection_id,
            },
        )
        if jobs["jobs"]:
            latest = jobs["jobs"][0]
            status = latest["job"]["status"]
            if status in ("succeeded", "failed", "cancelled"):
                return latest
        time.sleep(SYNC_POLL_INTERVAL)
    raise TimeoutError(f"Sync did not complete within {SYNC_TIMEOUT}s")


def trigger_sync(connection_id: str) -> dict:
    airbyte("POST", "connections/sync", {"connectionId": connection_id})
    time.sleep(2)  # brief pause to let the job register
    return wait_for_sync(connection_id)


def get_job_logs(job_id: int) -> str:
    """Retrieve logs for a given job attempt."""
    try:
        data = airbyte("POST", "attempt/get_for_job", {"jobId": job_id})
        attempts = data.get("attempts", [])
        if attempts:
            log_lines = attempts[-1].get("logs", {}).get("logLines", [])
            return "\n".join(log_lines)
    except Exception:
        pass
    return ""


# ──────────────────────────────────────────────────────────────────────
# Airbyte resource IDs — filled in during Phase 2
# ──────────────────────────────────────────────────────────────────────
source_id = None
destination_id = None
connection_id = None


# ──────────────────────────────────────────────────────────────────────
# Phase 1: Connection & Setup Validation
# ──────────────────────────────────────────────────────────────────────


def phase1():
    print("\n=== Phase 1: Connection & Setup Validation ===\n")

    # TEST-1.1: Connect to MySQL
    try:
        conn = mysql_conn()
        conn.close()
        record("TEST-1.1", True, "Connected to staging MySQL")
    except Exception as e:
        record("TEST-1.1", False, str(e))
        abort("Cannot connect to MySQL, remaining tests would fail.")

    # TEST-1.2 .. 1.4: binlog variables that must match for CDC to work
    variable_checks = [
        ("TEST-1.2", "log_bin", "ON"),
        ("TEST-1.3", "binlog_format", "ROW"),
        ("TEST-1.4", "binlog_row_image", "FULL"),
    ]
    conn = mysql_conn()
    cur = conn.cursor()
    for test_id, var, expected in variable_checks:
        cur.execute(f"SHOW VARIABLES LIKE '{var}'")
        row = cur.fetchone()
        if row and row[1].upper() == expected:
            record(test_id, True, f"{var}={row[1]}")
        else:
            record(test_id, False, f"{var}={row[1] if row else 'NOT FOUND'}, expected {expected}")

    # TEST-1.4b: binlog_row_value_options must be empty.
    # OCI HeatWave defaults this to PARTIAL_JSON, which causes Debezium to
    # silently drop UPDATE events on rows containing JSON columns — INSERT
    # and DELETE still flow normally, so the failure mode is "creates and
    # deletes work, updates never arrive" with no error logged.
    cur.execute("SHOW VARIABLES LIKE 'binlog_row_value_options'")
    row = cur.fetchone()
    value = row[1] if row else ""
    if value == "":
        record("TEST-1.4b", True, "binlog_row_value_options=<empty>")
    else:
        record(
            "TEST-1.4b",
            False,
            f"binlog_row_value_options={value!r}, expected empty string "
            "(OCI HeatWave default is PARTIAL_JSON; set to '' via OCI "
            "parameter group or `SET GLOBAL binlog_row_value_options = '';`)",
        )
    cur.close()
    conn.close()

    # TEST-1.5: Connect to Snowflake
    try:
        conn = sf_conn()
        conn.close()
        record("TEST-1.5", True, "Connected to staging Snowflake")
    except Exception as e:
        record("TEST-1.5", False, str(e))
        abort("Cannot connect to Snowflake, remaining tests would fail.")

    # TEST-1.6: Airbyte check_connection
    try:
        workspace = get_workspace_id()
        result = (
            airbyte(
                "POST",
                "sources/check_connection",
                {
                    "sourceId": source_id,
                },
            )
            if source_id
            else {"status": "skip"}
        )

        # If source not yet created, create it first and then check
        if not source_id:
            record("TEST-1.6", True, "Deferred to Phase 2 (source not yet created)")
        elif result.get("status") == "succeeded":
            record("TEST-1.6", True, "Airbyte check_connection succeeded")
        else:
            record("TEST-1.6", False, f"Airbyte check_connection: {result}")
    except Exception as e:
        record("TEST-1.6", False, str(e))


# ──────────────────────────────────────────────────────────────────────
# Phase 2: Initial Snapshot
# ──────────────────────────────────────────────────────────────────────


def phase2():
    global source_id, destination_id, connection_id
    print("\n=== Phase 2: Initial Snapshot ===\n")

    # TEST-2.1: Create test table with 50 seed rows
    try:
        conn = mysql_conn()
        cur = conn.cursor()
        cur.execute(f"DROP TABLE IF EXISTS `{TEST_TABLE}`")
        # `meta` is a JSON column so the test also exercises the
        # PARTIAL_JSON / Debezium UPDATE-drop regression — if the source
        # MySQL still has binlog_row_value_options=PARTIAL_JSON, UPDATE
        # events on this row will be silently dropped and the UPDATE
        # assertions in Phase 3 will fail with stale Snowflake values.
        cur.execute(f"""
            CREATE TABLE `{TEST_TABLE}` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'active',
                value INT NOT NULL DEFAULT 0,
                meta JSON DEFAULT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        for i in range(1, 51):
            cur.execute(
                f"INSERT INTO `{TEST_TABLE}` (name, status, value, meta) VALUES (%s, %s, %s, %s)",
                (f"row_{i:03d}", "active", i * 10, json.dumps({"v": i})),
            )
        conn.commit()
        cur.close()
        conn.close()
        record("TEST-2.1", True, "Created test table with 50 seed rows")
    except Exception as e:
        record("TEST-2.1", False, str(e))
        abort("Cannot create test table.")

    # TEST-2.2: Configure Airbyte connection via API
    try:
        workspace = get_workspace_id()

        # Create source
        src = airbyte(
            "POST",
            "sources/create",
            {
                "workspaceId": workspace,
                "sourceDefinitionId": "435bb9a5-7887-4809-aa58-28c27df0d7ad",  # MySQL
                "connectionConfiguration": {
                    "host": MYSQL_HOST,
                    "port": MYSQL_PORT,
                    "database": MYSQL_DATABASE,
                    "username": MYSQL_USER,
                    "password": MYSQL_PASSWORD,
                    "replication_method": {
                        "method": "CDC",
                        "initial_waiting_seconds": 300,
                        "server_time_zone": "UTC",
                        "invalid_cdc_cursor_position_behavior": "Re-sync data",
                    },
                    "ssl_mode": {"mode": "preferred"},
                },
                "name": f"test-mysql-no-reload-{int(time.time())}",
            },
        )
        source_id = src["sourceId"]

        # Check connection now that we have a source
        check = airbyte("POST", "sources/check_connection", {"sourceId": source_id})
        if check.get("status") == "succeeded":
            record("TEST-1.6", True, "Airbyte check_connection succeeded (deferred from Phase 1)")
        else:
            msg = check.get("message", str(check))
            record("TEST-1.6", False, f"check_connection failed: {msg}")
            abort(f"Airbyte source check_connection failed: {msg}")

        # Create destination (Snowflake)
        dst = airbyte(
            "POST",
            "destinations/create",
            {
                "workspaceId": workspace,
                "destinationDefinitionId": "424892c4-daac-4491-b35d-c6688ba547ba",  # Snowflake
                "connectionConfiguration": {
                    "host": f"{SNOWFLAKE_ACCOUNT}.snowflakecomputing.com",
                    "role": os.environ["SNOWFLAKE_ROLE"],
                    "warehouse": SNOWFLAKE_WAREHOUSE,
                    "database": SNOWFLAKE_DATABASE,
                    "schema": SNOWFLAKE_SCHEMA,
                    "username": SNOWFLAKE_USER,
                    "credentials": {
                        "auth_type": "Username and Password",
                        "password": SNOWFLAKE_PASSWORD,
                    },
                },
                "name": f"test-snowflake-{int(time.time())}",
            },
        )
        destination_id = dst["destinationId"]

        # Discover schema to build catalog
        discover = airbyte("POST", "sources/discover_schema", {"sourceId": source_id})
        catalog = discover["catalog"]

        # Find our test table stream and configure it for CDC incremental
        streams_config = []
        for stream_entry in catalog["streams"]:
            s = stream_entry["stream"]
            if s["name"] == TEST_TABLE:
                streams_config.append(
                    {
                        "stream": s,
                        "config": {
                            "syncMode": "incremental",
                            "destinationSyncMode": "append_dedup",
                            "primaryKey": [["id"]],
                            "cursorField": ["_ab_cdc_cursor"],
                            "selected": True,
                        },
                    }
                )
                break

        if not streams_config:
            record("TEST-2.2", False, f"Test table {TEST_TABLE} not found in discovered schema")
            abort("Cannot find test table in Airbyte schema discovery.")

        # Create connection
        conn_resp = airbyte(
            "POST",
            "connections/create",
            {
                "sourceId": source_id,
                "destinationId": destination_id,
                "syncCatalog": {"streams": streams_config},
                "status": "active",
                "scheduleType": "manual",
                "namespaceDefinition": "source",
                "name": f"test-cdc-no-reload-{int(time.time())}",
            },
        )
        connection_id = conn_resp["connectionId"]
        record("TEST-2.2", True, f"Connection created: {connection_id}")
    except Exception as e:
        record("TEST-2.2", False, str(e))
        abort("Cannot configure Airbyte connection.")

    # TEST-2.3 & 2.4: Trigger initial sync and wait
    try:
        job = trigger_sync(connection_id)
        job_status = job["job"]["status"]
        job_id = job["job"]["id"]
        if job_status != "succeeded":
            record("TEST-2.3", False, f"Initial sync status: {job_status}")
            logs = get_job_logs(job_id)
            if logs:
                print(f"    Last 20 log lines:\n{'    '.join(logs.split(chr(10))[-20:])}")
            abort("Initial sync failed.")
        record("TEST-2.3", True, f"Initial sync completed (job {job_id})")
    except Exception as e:
        record("TEST-2.3", False, str(e))
        abort("Initial sync failed.")

    # TEST-2.5: Verify row count in Snowflake
    try:
        time.sleep(5)  # brief settle time
        count = sf_row_count()
        record("TEST-2.5", count == 50, f"Snowflake row count: {count} (expected 50)")
    except Exception as e:
        record("TEST-2.5", False, str(e))

    # TEST-2.6: Check logs for snapshot.locking.mode
    try:
        logs = get_job_logs(job_id)
        found = "snapshot.locking.mode" in logs and "none" in logs
        record(
            "TEST-2.6", found, "snapshot.locking.mode=none in logs" if found else "Not found in logs (may require docker log inspection)"
        )
    except Exception as e:
        record("TEST-2.6", False, str(e))

    # TEST-2.7: No RELOAD errors in logs
    try:
        logs = get_job_logs(job_id)
        has_reload_error = "RELOAD" in logs.upper() and "ERROR" in logs.upper()
        record("TEST-2.7", not has_reload_error, "No RELOAD-related errors in logs")
    except Exception as e:
        record("TEST-2.7", False, str(e))


# ──────────────────────────────────────────────────────────────────────
# Phase 3: CDC Operations
# ──────────────────────────────────────────────────────────────────────


def phase3():
    print("\n=== Phase 3: CDC Operations ===\n")

    # TEST-3.1 & 3.2 & 3.3: INSERT 5 rows
    try:
        conn = mysql_conn()
        cur = conn.cursor()
        for i in range(51, 56):
            cur.execute(
                f"INSERT INTO `{TEST_TABLE}` (name, status, value, meta) VALUES (%s, %s, %s, %s)",
                (f"row_{i:03d}", "active", i * 10, json.dumps({"v": i})),
            )
        conn.commit()
        cur.close()
        conn.close()
        record("TEST-3.1", True, "Inserted 5 rows (ids 51-55)")
    except Exception as e:
        record("TEST-3.1", False, str(e))

    try:
        job = trigger_sync(connection_id)
        record("TEST-3.2", job["job"]["status"] == "succeeded", f"Incremental sync: {job['job']['status']}")
    except Exception as e:
        record("TEST-3.2", False, str(e))

    try:
        time.sleep(5)
        count = sf_row_count()
        record("TEST-3.3", count == 55, f"Snowflake active rows: {count} (expected 55)")
    except Exception as e:
        record("TEST-3.3", False, str(e))

    # TEST-3.4 & 3.5 & 3.6: UPDATE 3 rows
    try:
        conn = mysql_conn()
        cur = conn.cursor()
        # Also mutate the JSON column — this is the regression surface for
        # PARTIAL_JSON: under that binlog mode Debezium drops these UPDATEs
        # silently and the assertions below stay stuck on the pre-UPDATE state.
        cur.execute(
            f"UPDATE `{TEST_TABLE}` "
            f"SET status='updated', value=9999, meta=JSON_OBJECT('v', 0, 'updated', true) "
            f"WHERE id IN (51, 52, 53)"
        )
        conn.commit()
        cur.close()
        conn.close()
        record("TEST-3.4", True, "Updated 3 rows (ids 51,52,53)")
    except Exception as e:
        record("TEST-3.4", False, str(e))

    try:
        job = trigger_sync(connection_id)
        record("TEST-3.5", job["job"]["status"] == "succeeded", f"Incremental sync: {job['job']['status']}")
    except Exception as e:
        record("TEST-3.5", False, str(e))

    try:
        time.sleep(5)
        # Check that the 3 rows have status='updated' and value=9999
        rows = sf_query(
            f'SELECT COUNT(*) FROM "{SNOWFLAKE_DATABASE}"."{SNOWFLAKE_SCHEMA}"."{TEST_TABLE}"'
            f' WHERE "STATUS" = \'updated\' AND "VALUE" = 9999'
            f' AND "_AB_CDC_DELETED_AT" IS NULL'
        )
        updated_count = rows[0][0]
        # Also check no duplicates — total active rows should still be 55
        active_count = sf_row_count()
        passed = updated_count == 3 and active_count == 55
        record("TEST-3.6", passed, f"Updated rows: {updated_count}/3, active total: {active_count}/55")
    except Exception as e:
        record("TEST-3.6", False, str(e))

    # TEST-3.7 & 3.8 & 3.9: DELETE 2 rows
    try:
        conn = mysql_conn()
        cur = conn.cursor()
        cur.execute(f"DELETE FROM `{TEST_TABLE}` WHERE id IN (54, 55)")
        conn.commit()
        cur.close()
        conn.close()
        record("TEST-3.7", True, "Deleted 2 rows (ids 54,55)")
    except Exception as e:
        record("TEST-3.7", False, str(e))

    try:
        job = trigger_sync(connection_id)
        record("TEST-3.8", job["job"]["status"] == "succeeded", f"Incremental sync: {job['job']['status']}")
    except Exception as e:
        record("TEST-3.8", False, str(e))

    try:
        time.sleep(5)
        # Active rows should be 53 (55 - 2 deleted)
        active_count = sf_row_count()
        # Check soft-deleted rows
        deleted_rows = sf_query(
            f'SELECT COUNT(*) FROM "{SNOWFLAKE_DATABASE}"."{SNOWFLAKE_SCHEMA}"."{TEST_TABLE}" WHERE "_AB_CDC_DELETED_AT" IS NOT NULL'
        )
        deleted_count = deleted_rows[0][0]
        passed = active_count == 53 and deleted_count >= 2
        record("TEST-3.9", passed, f"Active rows: {active_count}/53, soft-deleted: {deleted_count} (>= 2)")
    except Exception as e:
        record("TEST-3.9", False, str(e))

    # TEST-3.10 & 3.11 & 3.12: Bulk UPDATE 20 rows
    try:
        conn = mysql_conn()
        cur = conn.cursor()
        cur.execute(f"UPDATE `{TEST_TABLE}` SET status='bulk_updated', value=1111 WHERE id BETWEEN 1 AND 20")
        affected = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        record("TEST-3.10", affected == 20, f"Bulk updated {affected} rows (expected 20)")
    except Exception as e:
        record("TEST-3.10", False, str(e))

    try:
        job = trigger_sync(connection_id)
        record("TEST-3.11", job["job"]["status"] == "succeeded", f"Incremental sync: {job['job']['status']}")
    except Exception as e:
        record("TEST-3.11", False, str(e))

    try:
        time.sleep(5)
        rows = sf_query(
            f'SELECT COUNT(*) FROM "{SNOWFLAKE_DATABASE}"."{SNOWFLAKE_SCHEMA}"."{TEST_TABLE}"'
            f' WHERE "STATUS" = \'bulk_updated\' AND "VALUE" = 1111'
            f' AND "_AB_CDC_DELETED_AT" IS NULL'
        )
        bulk_count = rows[0][0]
        record("TEST-3.12", bulk_count == 20, f"Bulk-updated rows in Snowflake: {bulk_count}/20")
    except Exception as e:
        record("TEST-3.12", False, str(e))


# ──────────────────────────────────────────────────────────────────────
# Phase 4: Stability
# ──────────────────────────────────────────────────────────────────────


def phase4():
    print("\n=== Phase 4: Stability ===\n")

    try:
        conn = mysql_conn()
        cur = conn.cursor()

        # Sync A: 5 inserts + 3 updates
        for i in range(56, 61):
            cur.execute(
                f"INSERT INTO `{TEST_TABLE}` (name, status, value) VALUES (%s, %s, %s)",
                (f"row_{i:03d}", "stability_a", i * 10),
            )
        cur.execute(f"UPDATE `{TEST_TABLE}` SET status='stability_a_upd' WHERE id IN (21, 22, 23)")
        conn.commit()
        cur.close()
        conn.close()

        job_a = trigger_sync(connection_id)
        assert job_a["job"]["status"] == "succeeded", f"Sync A failed: {job_a['job']['status']}"

        # Sync B: 2 updates + 1 delete
        conn = mysql_conn()
        cur = conn.cursor()
        cur.execute(f"UPDATE `{TEST_TABLE}` SET status='stability_b_upd' WHERE id IN (24, 25)")
        cur.execute(f"DELETE FROM `{TEST_TABLE}` WHERE id = 56")
        conn.commit()
        cur.close()
        conn.close()

        job_b = trigger_sync(connection_id)
        assert job_b["job"]["status"] == "succeeded", f"Sync B failed: {job_b['job']['status']}"

        # Sync C: No changes (zero-record sync)
        job_c = trigger_sync(connection_id)
        assert job_c["job"]["status"] == "succeeded", f"Sync C failed: {job_c['job']['status']}"

        record("TEST-4.1", True, "3 consecutive syncs completed (mixed ops + zero-record)")
    except Exception as e:
        record("TEST-4.1", False, str(e))

    # TEST-4.2: Verify final state
    try:
        time.sleep(5)
        # Expected state after all operations:
        #   Original 50 rows
        #   +5 inserts (51-55), -2 deletes (54,55) = 53
        #   +5 inserts (56-60), -1 delete (56) = 57 active rows
        conn = mysql_conn()
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(*) FROM `{TEST_TABLE}`")
        mysql_count = cur.fetchone()[0]
        cur.close()
        conn.close()

        sf_count = sf_row_count()
        record("TEST-4.2", sf_count == mysql_count, f"MySQL active: {mysql_count}, Snowflake active: {sf_count}")
    except Exception as e:
        record("TEST-4.2", False, str(e))

    # TEST-4.3: No duplicates
    try:
        dup_check = sf_query(
            f'SELECT "ID", COUNT(*) as cnt'
            f' FROM "{SNOWFLAKE_DATABASE}"."{SNOWFLAKE_SCHEMA}"."{TEST_TABLE}"'
            f' WHERE "_AB_CDC_DELETED_AT" IS NULL'
            f' GROUP BY "ID" HAVING COUNT(*) > 1'
        )
        record("TEST-4.3", len(dup_check) == 0, f"Duplicate IDs found: {len(dup_check)}" if dup_check else "Zero duplicates")
    except Exception as e:
        record("TEST-4.3", False, str(e))


# ──────────────────────────────────────────────────────────────────────
# Phase 5: Cleanup & Report
# ──────────────────────────────────────────────────────────────────────


def phase5():
    print("\n=== Phase 5: Cleanup & Report ===\n")

    # TEST-5.1: Drop MySQL test table
    try:
        conn = mysql_conn()
        cur = conn.cursor()
        cur.execute(f"DROP TABLE IF EXISTS `{TEST_TABLE}`")
        conn.commit()
        cur.close()
        conn.close()
        record("TEST-5.1", True, "Dropped MySQL test table")
    except Exception as e:
        record("TEST-5.1", False, str(e))

    # TEST-5.2: Clean up Snowflake test data
    try:
        sf_query(f'DROP TABLE IF EXISTS "{SNOWFLAKE_DATABASE}"."{SNOWFLAKE_SCHEMA}"."{TEST_TABLE}"')
        record("TEST-5.2", True, "Dropped Snowflake test table")
    except Exception as e:
        record("TEST-5.2", False, str(e))

    # Clean up Airbyte resources (best-effort)
    try:
        if connection_id:
            airbyte("POST", "connections/delete", {"connectionId": connection_id})
        if destination_id:
            airbyte("POST", "destinations/delete", {"destinationId": destination_id})
        if source_id:
            airbyte("POST", "sources/delete", {"sourceId": source_id})
    except Exception:
        pass  # best-effort cleanup

    print_summary()


def print_summary():
    print("\n" + "=" * 50)
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    print(f"  TOTAL:  {total} tests")
    print(f"  PASSED: {passed}")
    print(f"  FAILED: {failed}")
    print("=" * 50)
    if failed:
        print("\nFailures:")
        for r in results:
            if r["status"] == "FAIL":
                print(f"  {r['id']}: {r['detail']}")
    print()


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Airbyte CDC No-RELOAD Test Runner")
    print(f"Started: {datetime.datetime.now().isoformat()}")
    print(f"MySQL:     {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")
    print(f"Snowflake: {SNOWFLAKE_ACCOUNT} / {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}")
    print(f"Airbyte:   {AIRBYTE_URL}")

    try:
        phase1()
        phase2()
        phase3()
        phase4()
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        traceback.print_exc()
    finally:
        phase5()
