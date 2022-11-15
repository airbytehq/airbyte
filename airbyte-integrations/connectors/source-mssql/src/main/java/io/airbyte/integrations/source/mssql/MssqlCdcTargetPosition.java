/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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

  public MssqlCdcTargetPosition(final Lsn targetLsn) {
    this.targetLsn = targetLsn;
  }

  @Override
  public boolean reachedTargetPosition(final JsonNode valueAsJson) {
    final Lsn recordLsn = extractLsn(valueAsJson);

    if (targetLsn.compareTo(recordLsn) > 0) {
      return false;
    } else {
      final SnapshotMetadata snapshotMetadata = SnapshotMetadata.valueOf(valueAsJson.get("source").get("snapshot").asText().toUpperCase());
      // if not snapshot or is snapshot but last record in snapshot.
      return SnapshotMetadata.TRUE != snapshotMetadata;
    }
  }

  private Lsn extractLsn(final JsonNode valueAsJson) {
    return Optional.ofNullable(valueAsJson.get("source"))
        .flatMap(source -> Optional.ofNullable(source.get("commit_lsn").asText()))
        .map(Lsn::valueOf)
        .orElseThrow(() -> new IllegalStateException("Could not find LSN"));
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final MssqlCdcTargetPosition that = (MssqlCdcTargetPosition) o;
    return targetLsn.equals(that.targetLsn);
  }

  @Override
  public int hashCode() {
    return targetLsn.hashCode();
  }

  public static MssqlCdcTargetPosition getTargetPosition(final JdbcDatabase database, final String dbName) {
    try {
      final List<JsonNode> jsonNodes = database
          .bufferedResultSetQuery(connection -> connection.createStatement().executeQuery(
              "USE [" + dbName + "]; SELECT sys.fn_cdc_get_max_lsn() AS max_lsn;"), JdbcUtils.getDefaultSourceOperations()::rowToJson);
      Preconditions.checkState(jsonNodes.size() == 1);
      if (jsonNodes.get(0).get("max_lsn") != null) {
        final Lsn maxLsn = Lsn.valueOf(jsonNodes.get(0).get("max_lsn").binaryValue());
        LOGGER.info("identified target lsn: " + maxLsn);
        return new MssqlCdcTargetPosition(maxLsn);
      } else {
        throw new RuntimeException("SQL returned max LSN as null, this might be because the SQL Server Agent is not running. " +
            "Please enable the Agent and try again (https://docs.microsoft.com/en-us/sql/ssms/agent/start-stop-or-pause-the-sql-server-agent-service?view=sql-server-ver15)");
      }
    } catch (final SQLException | IOException e) {
      throw new RuntimeException(e);
    }
  }

}
