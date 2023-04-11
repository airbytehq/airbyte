/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.debezium.CdcTargetPosition;
import io.airbyte.integrations.debezium.internals.SnapshotMetadata;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlCdcTargetPosition implements CdcTargetPosition<MySqlCdcPosition> {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlCdcTargetPosition.class);
  private final MySqlCdcPosition targetPosition;

  public MySqlCdcTargetPosition(final String fileName, final Long position) {
    this(new MySqlCdcPosition(fileName, position));
  }

  @Override
  public boolean equals(final Object obj) {
    if (obj instanceof final MySqlCdcTargetPosition cdcTargetPosition) {
      return targetPosition.equals(cdcTargetPosition.targetPosition);
    }
    return false;
  }

  @Override
  public int hashCode() {
    return targetPosition.hashCode();
  }

  @Override
  public String toString() {
    return targetPosition.toString();
  }

  public MySqlCdcTargetPosition(final MySqlCdcPosition targetPosition) {
    this.targetPosition = targetPosition;
  }

  public static MySqlCdcTargetPosition targetPosition(final JdbcDatabase database) {
    try (final Stream<MySqlCdcTargetPosition> stream = database.unsafeResultSetQuery(
        connection -> connection.createStatement().executeQuery("SHOW MASTER STATUS"),
        resultSet -> {
          final String file = resultSet.getString("File");
          final long position = resultSet.getLong("Position");
          if (file == null || position == 0) {
            return new MySqlCdcTargetPosition(null, null);
          }
          return new MySqlCdcTargetPosition(file, position);
        })) {
      final List<MySqlCdcTargetPosition> masterStatus = stream.toList();
      final MySqlCdcTargetPosition targetPosition = masterStatus.get(0);
      LOGGER.info("Target File position : " + targetPosition);
      return targetPosition;
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }

  }

  @Override
  public boolean reachedTargetPosition(final JsonNode valueAsJson) {
    final String eventFileName = valueAsJson.get("source").get("file").asText();
    final SnapshotMetadata snapshotMetadata = SnapshotMetadata.fromString(valueAsJson.get("source").get("snapshot").asText());
    if (SnapshotMetadata.isSnapshotEventMetadata(snapshotMetadata)) {
      return false;
    } else if (SnapshotMetadata.LAST == snapshotMetadata) {
      LOGGER.info("Signalling close because Snapshot is complete");
      return true;
    } else {
      final long eventPosition = valueAsJson.get("source").get("pos").asLong();
      final boolean isEventPositionAfter =
          eventFileName.compareTo(targetPosition.fileName) > 0 || (eventFileName.compareTo(
              targetPosition.fileName) == 0 && eventPosition >= targetPosition.position);
      if (isEventPositionAfter) {
        LOGGER.info("Signalling close because record's binlog file : " + eventFileName + " , position : " + eventPosition
            + " is after target file : "
            + targetPosition.fileName + " , target position : " + targetPosition.position);
      }
      return isEventPositionAfter;
    }

  }

  @Override
  public boolean reachedTargetPosition(final MySqlCdcPosition positionFromHeartbeat) {
    return positionFromHeartbeat.fileName.compareTo(targetPosition.fileName) > 0 ||
        (positionFromHeartbeat.fileName.compareTo(targetPosition.fileName) == 0
            && positionFromHeartbeat.position >= targetPosition.position);
  }

  @Override
  public boolean isHeartbeatSupported() {
    return true;
  }

  @Override
  public MySqlCdcPosition extractPositionFromHeartbeatOffset(final Map<String, ?> sourceOffset) {
    return new MySqlCdcPosition(sourceOffset.get("file").toString(), (Long) sourceOffset.get("pos"));
  }

}
