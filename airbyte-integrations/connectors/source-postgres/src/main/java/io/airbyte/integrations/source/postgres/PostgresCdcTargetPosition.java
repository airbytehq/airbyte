/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.db.PgLsn;
import io.airbyte.db.PostgresUtils;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.debezium.CdcTargetPosition;
import io.airbyte.integrations.debezium.internals.SnapshotMetadata;
import io.debezium.engine.ChangeEvent;
import java.lang.reflect.Field;
import java.sql.SQLException;
import java.util.Objects;
import java.util.Optional;
import org.apache.kafka.connect.source.SourceRecord;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresCdcTargetPosition implements CdcTargetPosition {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresCdcTargetPosition.class);
  @VisibleForTesting
  final PgLsn targetLsn;

  public PostgresCdcTargetPosition(final PgLsn targetLsn) {
    this.targetLsn = targetLsn;
  }

  @Override
  public boolean equals(final Object obj) {
    if (obj instanceof PostgresCdcTargetPosition) {
      final PostgresCdcTargetPosition cdcTargetPosition = (PostgresCdcTargetPosition) obj;
      return cdcTargetPosition.targetLsn.compareTo(targetLsn) == 0;
    }
    return false;
  }

  @Override
  public int hashCode() {
    return Objects.hash(targetLsn.asLong());
  }

  static PostgresCdcTargetPosition targetPosition(final JdbcDatabase database) {
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
    final SnapshotMetadata snapshotMetadata = SnapshotMetadata.valueOf(valueAsJson.get("source").get("snapshot").asText().toUpperCase());

    if (SnapshotMetadata.TRUE == snapshotMetadata) {
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

  private boolean isHeartbeatEvent(final ChangeEvent<String, String> event) {
    return Objects.nonNull(event) && !event.value().contains("source");
  }

  @Override
  public Long getHeartbeatPosition(final ChangeEvent<String, String> heartbeatEvent) {
    if (isHeartbeatEvent(heartbeatEvent)) {
      try {
        final Field f = heartbeatEvent.getClass().getDeclaredField("sourceRecord");
        f.setAccessible(true);
        final SourceRecord sr = (SourceRecord) f.get(heartbeatEvent);
        final Long hbLsn = (Long) sr.sourceOffset().get("lsn");
        LOGGER.debug("Found heartbeat lsn: {}", hbLsn);
        return hbLsn;
      } catch (final NoSuchFieldException | IllegalAccessException e) {
        LOGGER.info("failed to get heartbeat lsn");
      }
    }
    return null;
  }

  @Override
  public boolean reachedTargetPosition(final Long lsn) {
    return (lsn == null) ? false : lsn.compareTo(targetLsn.asLong()) >= 0;
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

}
