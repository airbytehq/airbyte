/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.cdk.db.PgLsn;
import io.airbyte.cdk.db.PostgresUtils;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.debezium.CdcTargetPosition;
import io.airbyte.cdk.integrations.debezium.internals.ChangeEventWithMetadata;
import io.airbyte.cdk.integrations.debezium.internals.SnapshotMetadata;
import io.airbyte.commons.json.Jsons;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresCdcTargetPosition implements CdcTargetPosition<Long> {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresCdcTargetPosition.class);
  @VisibleForTesting
  public final PgLsn targetLsn;

  public PostgresCdcTargetPosition(final PgLsn targetLsn) {
    this.targetLsn = targetLsn;
  }

  @Override
  public boolean equals(final Object obj) {
    if (obj instanceof final PostgresCdcTargetPosition cdcTargetPosition) {
      return cdcTargetPosition.targetLsn.compareTo(targetLsn) == 0;
    }
    return false;
  }

  @Override
  public int hashCode() {
    return Objects.hash(targetLsn.asLong());
  }

  public static PostgresCdcTargetPosition targetPosition(final JdbcDatabase database) {
    try {
      final PgLsn lsn = PostgresUtils.getLsn(database);
      LOGGER.info("identified target lsn: " + lsn);
      return new PostgresCdcTargetPosition(lsn);
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  public boolean reachedTargetPosition(final ChangeEventWithMetadata changeEventWithMetadata) {
    if (changeEventWithMetadata.isSnapshotEvent()) {
      return false;
    } else if (SnapshotMetadata.LAST == changeEventWithMetadata.snapshotMetadata()) {
      LOGGER.info("Signalling close because Snapshot is complete");
      return true;
    } else {
      final PgLsn eventLsn = extractLsn(changeEventWithMetadata.eventValueAsJson());
      final boolean isEventLSNAfter = targetLsn.compareTo(eventLsn) <= 0;
      if (isEventLSNAfter) {
        LOGGER.info("Signalling close because record's LSN : " + eventLsn + " is after target LSN : " + targetLsn);
      }
      return isEventLSNAfter;
    }
  }

  @Override
  public boolean reachedTargetPosition(final Long positionFromHeartbeat) {
    final boolean reachedTargetPosition = positionFromHeartbeat != null && positionFromHeartbeat.compareTo(targetLsn.asLong()) >= 0;
    if (reachedTargetPosition) {
      LOGGER.info("Signalling close because heartbeat LSN : " + positionFromHeartbeat + " is after target LSN : " + targetLsn);
    }
    return reachedTargetPosition;
  }

  private PgLsn extractLsn(final JsonNode valueAsJson) {
    return Optional.ofNullable(valueAsJson.get("source"))
        .flatMap(source -> Optional.ofNullable(source.get("lsn").asText()))
        .map(Long::parseLong)
        .map(PgLsn::fromLong)
        .orElseThrow(() -> new IllegalStateException("Could not find LSN"));
  }

  @Override
  public boolean isHeartbeatSupported() {
    return true;
  }

  @Override
  public Long extractPositionFromHeartbeatOffset(final Map<String, ?> sourceOffset) {
    return (long) sourceOffset.get("lsn");
  }

  @Override
  public boolean isEventAheadOffset(final Map<String, String> offset, final ChangeEventWithMetadata event) {
    if (offset.size() != 1) {
      return false;
    }

    final JsonNode offsetJson = Jsons.deserialize((String) offset.values().toArray()[0]);

    if (offsetJson.get("lsn_commit") == null) {
      return false;
    }
    final String stateOffsetLsnCommit = String.valueOf(offsetJson.get("lsn_commit"));

    try {
      ObjectMapper objectMapper = new ObjectMapper();
      TypeReference<List<String>> listType = new TypeReference<>() {};
      /* @formatter:off
       The event source structure is :
          {
             "version":"2.4.0.Final",
             "connector":"postgresql",
             "name":"db_pkgzzfnybb",
             "ts_ms":1710283178042,
             "snapshot":"false",
             "db":"db_pkgzzfnybb",
             "sequence":"[\"30660608\",\"30660608\"]",
             "schema":"models_schema",
             "table":"models",
             "txId":777,
             "lsn":30660608,
             "xmin":null
          }
          See https://debezium.io/documentation/reference/2.4/connectors/postgresql.html#postgresql-create-events for the full event structure.
          @formatter:on
       */
      final JsonNode lsnSequenceNode = event.eventValueAsJson().get("source").get("sequence");
      List<String> lsnSequence = objectMapper.readValue(lsnSequenceNode.asText(), listType);
      // The sequence field is a pair of [lsn_commit, lsn_processed]. We want to make sure
      // lsn_commit(event) is compared against lsn_commit(state_offset). For the event, either of the lsn
      // values can be null.
      String eventLsnCommit = lsnSequence.get(0);
      if (eventLsnCommit == null) {
        return false;
      }
      return Long.parseLong(eventLsnCommit) > Long.parseLong(stateOffsetLsnCommit);
    } catch (Exception e) {
      LOGGER.info("Encountered an error while attempting to parse event's LSN sequence {}", e.getCause());
      return false;
    }
  }

  @Override
  public boolean isSameOffset(final Map<String, String> offsetA, final Map<String, String> offsetB) {
    if (offsetA == null || offsetA.size() != 1) {
      return false;
    }
    if (offsetB == null || offsetB.size() != 1) {
      return false;
    }
    final JsonNode offsetJsonA = Jsons.deserialize((String) offsetA.values().toArray()[0]);
    final JsonNode offsetJsonB = Jsons.deserialize((String) offsetB.values().toArray()[0]);

    final String lsnA =
        offsetJsonA.get("lsn_commit") != null ? String.valueOf(offsetJsonA.get("lsn_commit")) : String.valueOf(offsetJsonA.get("lsn"));
    final String lsnB =
        offsetJsonB.get("lsn_commit") != null ? String.valueOf(offsetJsonB.get("lsn_commit")) : String.valueOf(offsetJsonB.get("lsn"));

    return Long.parseLong(lsnA) == Long.parseLong(lsnB);
  }

}
