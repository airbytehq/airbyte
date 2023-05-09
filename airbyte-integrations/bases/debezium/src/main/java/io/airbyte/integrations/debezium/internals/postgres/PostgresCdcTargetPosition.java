/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.PgLsn;
import io.airbyte.db.PostgresUtils;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.debezium.CdcTargetPosition;
import io.airbyte.integrations.debezium.internals.SnapshotMetadata;
import io.debezium.engine.ChangeEvent;
import java.sql.SQLException;
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
  public boolean reachedTargetPosition(final JsonNode valueAsJson) {
    final SnapshotMetadata snapshotMetadata = SnapshotMetadata.fromString(valueAsJson.get("source").get("snapshot").asText());

    if (SnapshotMetadata.isSnapshotEventMetadata(snapshotMetadata)) {
      return false;
    } else if (SnapshotMetadata.LAST == snapshotMetadata) {
      LOGGER.info("Signalling close because Snapshot is complete");
      return true;
    } else {
      final PgLsn eventLsn = extractLsn(valueAsJson);
      boolean isEventLSNAfter = targetLsn.compareTo(eventLsn) <= 0;
      if (isEventLSNAfter) {
        LOGGER.info("Signalling close because record's LSN : " + eventLsn + " is after target LSN : " + targetLsn);
      }
      return isEventLSNAfter;
    }
  }

  @Override
  public boolean reachedTargetPosition(final Long positionFromHeartbeat) {
    return positionFromHeartbeat != null && positionFromHeartbeat.compareTo(targetLsn.asLong()) >= 0;
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
  public boolean isSnapshotEvent(final ChangeEvent<String, String> event) {
    JsonNode isSnapshotEvent = Jsons.deserialize(event.value()).get("source").get("snapshot");
    return isSnapshotEvent != null && isSnapshotEvent.asBoolean();
  }

  @Override
  public boolean isRecordBehindOffset(final Map<String, String> offset, final ChangeEvent<String, String> event) {
    if (offset.size() != 1) {
      return false;
    }

    final JsonNode offsetJson = Jsons.deserialize((String) offset.values().toArray()[0]);

    final String offset_lsn =
        offsetJson.get("lsn_commit") != null ? String.valueOf(offsetJson.get("lsn_commit")) : String.valueOf(offsetJson.get("lsn"));
    final String event_lsn = String.valueOf(Jsons.deserialize(event.value()).get("source").get("lsn"));
    return Integer.parseInt(event_lsn) > Integer.parseInt(offset_lsn);
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

    return Integer.parseInt(lsnA) == Integer.parseInt(lsnB);
  }

}
