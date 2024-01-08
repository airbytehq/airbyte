/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.debezium.CdcTargetPosition;
import io.airbyte.cdk.integrations.debezium.internals.ChangeEventWithMetadata;
import io.airbyte.cdk.integrations.debezium.internals.SnapshotMetadata;
import io.debezium.connector.sqlserver.Lsn;
import java.io.IOException;
import java.sql.SQLException;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MssqlCdcTargetPosition implements CdcTargetPosition<Lsn> {

  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlCdcTargetPosition.class);

  public static final Duration MAX_LSN_QUERY_DELAY = Duration.ZERO;
  public static final Duration MAX_LSN_QUERY_DELAY_TEST = Duration.ofSeconds(1);
  public final Lsn targetLsn;

  public MssqlCdcTargetPosition(final Lsn targetLsn) {
    this.targetLsn = targetLsn;
  }

  @Override
  public boolean reachedTargetPosition(final ChangeEventWithMetadata changeEventWithMetadata) {
    if (changeEventWithMetadata.isSnapshotEvent()) {
      return false;
    } else if (SnapshotMetadata.LAST == changeEventWithMetadata.snapshotMetadata()) {
      LOGGER.info("Signalling close because Snapshot is complete");
      return true;
    } else {
      final Lsn recordLsn = extractLsn(changeEventWithMetadata.eventValueAsJson());
      final boolean isEventLSNAfter = targetLsn.compareTo(recordLsn) <= 0;
      if (isEventLSNAfter) {
        LOGGER.info("Signalling close because record's LSN : " + recordLsn + " is after target LSN : " + targetLsn);
      }
      return isEventLSNAfter;
    }
  }

  @Override
  public Lsn extractPositionFromHeartbeatOffset(final Map<String, ?> sourceOffset) {
    throw new RuntimeException("Heartbeat is not supported for MSSQL");
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
      // We might have to wait a bit before querying the max_lsn to give the CDC capture job
      // a chance to catch up. This is important in tests, where reads might occur in quick succession
      // which might leave the CT tables (which Debezium consumes) in a stale state.
      final JsonNode sourceConfig = database.getSourceConfig();
      final Duration delay = (sourceConfig != null && sourceConfig.has("is_test") && sourceConfig.get("is_test").asBoolean())
          ? MAX_LSN_QUERY_DELAY_TEST
          : MAX_LSN_QUERY_DELAY;
      final String maxLsnQuery = """
                                 USE [%s];
                                 WAITFOR DELAY '%02d:%02d:%02d';
                                 SELECT sys.fn_cdc_get_max_lsn() AS max_lsn;
                                 """.formatted(dbName, delay.toHours(), delay.toMinutesPart(), delay.toSecondsPart());
      // Query the high-water mark.
      final List<JsonNode> jsonNodes = database.bufferedResultSetQuery(
          connection -> connection.createStatement().executeQuery(maxLsnQuery),
          JdbcUtils.getDefaultSourceOperations()::rowToJson);
      Preconditions.checkState(jsonNodes.size() == 1);
      if (jsonNodes.get(0).get("max_lsn") != null) {
        final Lsn maxLsn = Lsn.valueOf(jsonNodes.get(0).get("max_lsn").binaryValue());
        LOGGER.info("identified target lsn: " + maxLsn);
        return new MssqlCdcTargetPosition(maxLsn);
      } else {
        throw new RuntimeException("SQL returned max LSN as null, this might be because the SQL Server Agent is not running. " +
            "Please enable the Agent and try again (https://docs.microsoft.com/en-us/sql/ssms/agent/start-stop-or-pause-the-sql-server-agent-service)");
      }
    } catch (final SQLException | IOException e) {
      throw new RuntimeException(e);
    }
  }

}
