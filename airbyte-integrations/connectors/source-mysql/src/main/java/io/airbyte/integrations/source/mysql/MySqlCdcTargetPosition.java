/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.debezium.CdcTargetPosition;
import io.airbyte.integrations.debezium.internals.SnapshotMetadata;
import java.sql.SQLException;
import java.util.List;
import java.util.Objects;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlCdcTargetPosition implements CdcTargetPosition {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlCdcTargetPosition.class);
  public final String fileName;
  public final Integer position;

  public MySqlCdcTargetPosition(final String fileName, final Integer position) {
    this.fileName = fileName;
    this.position = position;
  }

  @Override
  public boolean equals(final Object obj) {
    if (obj instanceof final MySqlCdcTargetPosition cdcTargetPosition) {
      return fileName.equals(cdcTargetPosition.fileName) && cdcTargetPosition.position.equals(position);
    }
    return false;
  }

  @Override
  public int hashCode() {
    return Objects.hash(fileName, position);
  }

  @Override
  public String toString() {
    return "FileName: " + fileName + ", Position : " + position;
  }

  public static MySqlCdcTargetPosition targetPosition(final JdbcDatabase database) {
    try (final Stream<MySqlCdcTargetPosition> stream = database.unsafeResultSetQuery(
        connection -> connection.createStatement().executeQuery("SHOW MASTER STATUS"),
        resultSet -> {
          final String file = resultSet.getString("File");
          final int position = resultSet.getInt("Position");
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
    final SnapshotMetadata snapshotMetadata = SnapshotMetadata.valueOf(valueAsJson.get("source").get("snapshot").asText().toUpperCase());

    if (SnapshotMetadata.TRUE == snapshotMetadata) {
      return false;
    } else if (SnapshotMetadata.LAST == snapshotMetadata) {
      LOGGER.info("Signalling close because Snapshot is complete");
      return true;
    } else {
      final int eventPosition = valueAsJson.get("source").get("pos").asInt();
      final boolean isEventPositionAfter =
          eventFileName.compareTo(fileName) > 0 || (eventFileName.compareTo(fileName) == 0 && eventPosition >= position);
      if (isEventPositionAfter) {
        LOGGER.info("Signalling close because record's binlog file : " + eventFileName + " , position : " + eventPosition
            + " is after target file : "
            + fileName + " , target position : " + position);
      }
      return isEventPositionAfter;
    }

  }

}
