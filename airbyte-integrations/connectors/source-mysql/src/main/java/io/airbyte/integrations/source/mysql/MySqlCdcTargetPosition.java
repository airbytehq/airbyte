/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
