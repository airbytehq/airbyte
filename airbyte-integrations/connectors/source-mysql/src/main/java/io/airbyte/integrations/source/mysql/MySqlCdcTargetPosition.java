/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.debezium.CdcTargetPosition;
import io.airbyte.integrations.debezium.internals.SnapshotMetadata;
import java.sql.SQLException;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlCdcTargetPosition implements CdcTargetPosition {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlCdcTargetPosition.class);
  public final String fileName;
  public final Integer position;

  public MySqlCdcTargetPosition(String fileName, Integer position) {
    this.fileName = fileName;
    this.position = position;
  }

  @Override
  public boolean equals(Object obj) {
    if (obj instanceof MySqlCdcTargetPosition) {
      MySqlCdcTargetPosition cdcTargetPosition = (MySqlCdcTargetPosition) obj;
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

  public static MySqlCdcTargetPosition targetPosition(JdbcDatabase database) {
    try {
      List<MySqlCdcTargetPosition> masterStatus = database.resultSetQuery(
          connection -> connection.createStatement().executeQuery("SHOW MASTER STATUS"),
          resultSet -> {
            String file = resultSet.getString("File");
            int position = resultSet.getInt("Position");
            if (file == null || position == 0) {
              return new MySqlCdcTargetPosition(null, null);
            }
            return new MySqlCdcTargetPosition(file, position);
          }).collect(Collectors.toList());
      MySqlCdcTargetPosition targetPosition = masterStatus.get(0);
      LOGGER.info("Target File position : " + targetPosition);

      return targetPosition;
    } catch (SQLException e) {
      throw new RuntimeException(e);
    }

  }

  @Override
  public boolean reachedTargetPosition(JsonNode valueAsJson) {
    String eventFileName = valueAsJson.get("source").get("file").asText();
    int eventPosition = valueAsJson.get("source").get("pos").asInt();

    boolean isSnapshot = SnapshotMetadata.TRUE == SnapshotMetadata.valueOf(
        valueAsJson.get("source").get("snapshot").asText().toUpperCase());

    if (isSnapshot || fileName.compareTo(eventFileName) > 0
        || (fileName.compareTo(eventFileName) == 0 && position >= eventPosition)) {
      return false;
    }

    LOGGER.info("Signalling close because record's binlog file : " + eventFileName + " , position : " + eventPosition
        + " is after target file : "
        + fileName + " , target position : " + position);
    return true;
  }

}
