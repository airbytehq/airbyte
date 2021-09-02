/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.debezium.CdcTargetPosition;
import io.airbyte.integrations.debezium.internals.SnapshotMetadata;
import io.debezium.connector.sqlserver.Lsn;
import java.io.IOException;
import java.sql.SQLException;
import java.util.List;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MssqlCdcTargetPosition implements CdcTargetPosition {

  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlCdcTargetPosition.class);
  public final Lsn targetLsn;

  public MssqlCdcTargetPosition(Lsn targetLsn) {
    this.targetLsn = targetLsn;
  }

  @Override
  public boolean reachedTargetPosition(JsonNode valueAsJson) {
    Lsn recordLsn = extractLsn(valueAsJson);

    if (targetLsn.compareTo(recordLsn) > 0) {
      return false;
    } else {
      SnapshotMetadata snapshotMetadata = SnapshotMetadata.valueOf(valueAsJson.get("source").get("snapshot").asText().toUpperCase());
      // if not snapshot or is snapshot but last record in snapshot.
      return SnapshotMetadata.TRUE != snapshotMetadata;
    }
  }

  private Lsn extractLsn(JsonNode valueAsJson) {
    return Optional.ofNullable(valueAsJson.get("source"))
        .flatMap(source -> Optional.ofNullable(source.get("commit_lsn").asText()))
        .map(Lsn::valueOf)
        .orElseThrow(() -> new IllegalStateException("Could not find LSN"));
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    MssqlCdcTargetPosition that = (MssqlCdcTargetPosition) o;
    return targetLsn.equals(that.targetLsn);
  }

  @Override
  public int hashCode() {
    return targetLsn.hashCode();
  }

  public static MssqlCdcTargetPosition getTargetPosition(JdbcDatabase database, String dbName) {
    try {
      final List<JsonNode> jsonNodes = database
          .bufferedResultSetQuery(conn -> conn.createStatement().executeQuery(
              "USE " + dbName + "; SELECT sys.fn_cdc_get_max_lsn() AS max_lsn;"), JdbcUtils.getDefaultSourceOperations()::rowToJson);
      Preconditions.checkState(jsonNodes.size() == 1);
      if (jsonNodes.get(0).get("max_lsn") != null) {
        Lsn maxLsn = Lsn.valueOf(jsonNodes.get(0).get("max_lsn").binaryValue());
        LOGGER.info("identified target lsn: " + maxLsn);
        return new MssqlCdcTargetPosition(maxLsn);
      } else {
        throw new RuntimeException("SQL returned max LSN as null, this might be because the SQL Server Agent is not running. " +
            "Please enable the Agent and try again (https://docs.microsoft.com/en-us/sql/ssms/agent/start-stop-or-pause-the-sql-server-agent-service?view=sql-server-ver15)");
      }
    } catch (SQLException | IOException e) {
      throw new RuntimeException(e);
    }
  }

}
