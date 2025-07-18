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
import io.airbyte.commons.json.Jsons;
import io.debezium.connector.sqlserver.Lsn;
import java.io.IOException;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MssqlCdcTargetPosition implements CdcTargetPosition<Lsn> {

  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlCdcTargetPosition.class);

  public final Lsn targetLsn;

  public MssqlCdcTargetPosition(final Lsn targetLsn) {
    this.targetLsn = targetLsn;
  }

  @Override
  public boolean reachedTargetPosition(final ChangeEventWithMetadata changeEventWithMetadata) {
    if (changeEventWithMetadata.isSnapshotEvent()) {
      return false;
    } else if (SnapshotMetadata.LAST == changeEventWithMetadata.getSnapshotMetadata()) {
      LOGGER.info("Signalling close because Snapshot is complete");
      return true;
    } else {
      final Lsn recordLsn = extractLsn(changeEventWithMetadata.getEventValueAsJson());
      final boolean isEventLSNAfter = targetLsn.compareTo(recordLsn) <= 0;
      if (isEventLSNAfter) {
        LOGGER.info("Signalling close because record's LSN : " + recordLsn + " is after target LSN : " + targetLsn);
      }
      return isEventLSNAfter;
    }
  }

  @Override
  public Lsn extractPositionFromHeartbeatOffset(final Map<String, ?> sourceOffset) {
    final Object commitLsnValue = sourceOffset.get("commit_lsn");
    return (commitLsnValue == null) ? Lsn.NULL : Lsn.valueOf(commitLsnValue.toString());
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
      final String maxLsnQuery = """
                                 USE [%s];
                                 SELECT sys.fn_cdc_get_max_lsn() AS max_lsn;
                                 """.formatted(dbName);
      // Query the high-water mark.
      final List<JsonNode> jsonNodes = database.bufferedResultSetQuery(
          connection -> connection.createStatement().executeQuery(maxLsnQuery),
          JdbcUtils.getDefaultSourceOperations()::rowToJson);
      Preconditions.checkState(jsonNodes.size() == 1);

      final Lsn maxLsn;
      if (jsonNodes.get(0).get("max_lsn") != null) {
        maxLsn = Lsn.valueOf(jsonNodes.get(0).get("max_lsn").binaryValue());
      } else {
        maxLsn = Lsn.NULL;
      }
      LOGGER.info("identified target lsn: " + maxLsn);
      return new MssqlCdcTargetPosition(maxLsn);
    } catch (final SQLException | IOException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public boolean isHeartbeatSupported() {
    return true;
  }

  @Override
  public boolean reachedTargetPosition(Lsn positionFromHeartbeat) {
    return positionFromHeartbeat.compareTo(targetLsn) >= 0;
  }

  @Override
  public boolean isEventAheadOffset(Map<String, String> offset, ChangeEventWithMetadata event) {
    if (offset == null || offset.size() != 1) {
      return false;
    }
    final Lsn eventLsn = extractLsn(event.getEventValueAsJson());
    final Lsn offsetLsn = offsetToLsn(offset);
    return eventLsn.compareTo(offsetLsn) > 0;
  }

  @Override
  public boolean isSameOffset(Map<String, String> offsetA, Map<String, String> offsetB) {
    if ((offsetA == null || offsetA.size() != 1) || (offsetB == null || offsetB.size() != 1)) {
      return false;
    }
    return offsetToLsn(offsetA).equals(offsetToLsn(offsetB));
  }

  private Lsn offsetToLsn(Map<String, String> offset) {
    final JsonNode offsetJson = Jsons.deserialize((String) offset.values().toArray()[0]);
    final JsonNode commitLsnJson = offsetJson.get("commit_lsn");
    return (commitLsnJson == null || commitLsnJson.isNull()) ? Lsn.NULL : Lsn.valueOf(commitLsnJson.asText());
  }

}
