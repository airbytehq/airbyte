#!/usr/bin/env bash
# Drop every non-system database in the local backend.
#
# Used by `run.sh --reset=fixture` between the control and target image
# runs, so the target sees the fixture applied to a clean database
# rather than to the state control's sweep left behind. Faster than
# recreating the container (which is `--reset=backend`): the SQL Server
# process stays up, only the user databases are recreated. The
# server-wide log-LSN clock keeps ticking, so per-record LSN columns and
# STATE offsets still differ between the two sweeps — that is what
# `--reset=backend` is for.
#
# Env:
#   BACKEND_NAME            container name (default: source-mssql-db-backend)
#   BACKEND_SA_PASSWORD     sa password (default: Test_password_1)
set -euo pipefail

BACKEND_NAME="${BACKEND_NAME:-source-mssql-db-backend}"
BACKEND_SA_PASSWORD="${BACKEND_SA_PASSWORD:-Test_password_1}"

# database_id 1..4 are master/tempdb/model/msdb; everything above is a
# user database. SINGLE_USER WITH ROLLBACK IMMEDIATE kicks any active
# connections (a still-running Debezium engine, an sqlcmd session) so
# the DROP does not block waiting for them. Dropping the database drops
# its CDC schema and change tables along with it — no separate
# `sys.sp_cdc_disable_db` step needed.
TSQL=$(cat <<'SQL'
DECLARE @sql NVARCHAR(MAX) = N'';
SELECT @sql += N'ALTER DATABASE [' + name + N'] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;'
             + CHAR(10)
             + N'DROP DATABASE [' + name + N'];'
             + CHAR(10)
FROM sys.databases
WHERE database_id > 4;
IF LEN(@sql) > 0
    EXEC sp_executesql @sql;
SQL
)

echo "[reset-databases] dropping non-system databases on $BACKEND_NAME" >&2
docker exec -i "$BACKEND_NAME" /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "$BACKEND_SA_PASSWORD" -C -b -Q "$TSQL"
