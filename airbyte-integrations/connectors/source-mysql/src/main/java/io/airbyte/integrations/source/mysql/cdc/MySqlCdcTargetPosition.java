/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.cdc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.debezium.CdcTargetPosition;
import io.airbyte.cdk.integrations.debezium.internals.ChangeEventWithMetadata;
import io.airbyte.cdk.integrations.debezium.internals.SnapshotMetadata;
import io.airbyte.commons.json.Jsons;
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
  public boolean reachedTargetPosition(final ChangeEventWithMetadata changeEventWithMetadata) {
    if (changeEventWithMetadata.isSnapshotEvent()) {
      return false;
    } else if (SnapshotMetadata.LAST == changeEventWithMetadata.snapshotMetadata()) {
      LOGGER.info("Signalling close because Snapshot is complete");
      return true;
    } else {
      final String eventFileName = changeEventWithMetadata.eventValueAsJson().get("source").get("file").asText();
      final long eventPosition = changeEventWithMetadata.eventValueAsJson().get("source").get("pos").asLong();
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
  public boolean isEventAheadOffset(final Map<String, String> offset, final ChangeEventWithMetadata event) {
    if (offset.size() != 1) {
      return false;
    }

    final String eventFileName = event.eventValueAsJson().get("source").get("file").asText();
    final long eventPosition = event.eventValueAsJson().get("source").get("pos").asLong();

    final JsonNode offsetJson = Jsons.deserialize((String) offset.values().toArray()[0]);

    final String offsetFileName = offsetJson.get("file").asText();
    final long offsetPosition = offsetJson.get("pos").asLong();
    if (eventFileName.compareTo(offsetFileName) != 0) {
      return eventFileName.compareTo(offsetFileName) > 0;
    }

    return eventPosition > offsetPosition;
  }

  @Override
  public boolean isSameOffset(final Map<String, String> offsetA, final Map<String, String> offsetB) {
    if ((offsetA == null || offsetA.size() != 1) || (offsetB == null || offsetB.size() != 1)) {
      return false;
    }

    final JsonNode offsetJsonA = Jsons.deserialize((String) offsetA.values().toArray()[0]);
    final String offsetAFileName = offsetJsonA.get("file").asText();
    final long offsetAPosition = offsetJsonA.get("pos").asLong();

    final JsonNode offsetJsonB = Jsons.deserialize((String) offsetB.values().toArray()[0]);
    final String offsetBFileName = offsetJsonB.get("file").asText();
    final long offsetBPosition = offsetJsonB.get("pos").asLong();

    return offsetAFileName.equals(offsetBFileName) && offsetAPosition == offsetBPosition;
  }

  @Override
  public MySqlCdcPosition extractPositionFromHeartbeatOffset(final Map<String, ?> sourceOffset) {
    return new MySqlCdcPosition(sourceOffset.get("file").toString(), (Long) sourceOffset.get("pos"));
  }

}
