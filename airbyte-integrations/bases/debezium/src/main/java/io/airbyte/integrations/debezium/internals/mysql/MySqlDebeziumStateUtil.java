package io.airbyte.integrations.debezium.internals.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.debezium.time.Conversions;
import java.sql.SQLException;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlDebeziumStateUtil {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlDebeziumStateUtil.class);

  /**
   * Method to construct initial Debezium state which can be passed onto Debezium engine to make it process binlogs from a specific file and position
   * and skip snapshot phase
   */
  public JsonNode constructInitialDebeziumState(final JdbcDatabase database, final String dbName) {

//    final String showMasterStmt = "SHOW MASTER STATUS";
//    connection.query(showMasterStmt, rs -> {
//      if (rs.next()) {
//        final String binlogFilename = rs.getString(1);
//        final long binlogPosition = rs.getLong(2);
//        offsetContext.setBinlogStartPoint(binlogFilename, binlogPosition);
//        if (rs.getMetaData().getColumnCount() > 4) {
//          // This column exists only in MySQL 5.6.5 or later ...
//          final String gtidSet = rs.getString(5); // GTID set, may be null, blank, or contain a GTID set
//          offsetContext.setCompletedGtidSet(gtidSet);
//          LOGGER.info("\t using binlog '{}' at position '{}' and gtid '{}'", binlogFilename, binlogPosition,
//              gtidSet);
//        }
    return format(MySqlCdcTargetPosition.targetPosition(database).getTargetPosition(), dbName, Instant.now());
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

  @VisibleForTesting
  public JsonNode format(final MySqlCdcPosition position, final String dbName, final Instant time) {
    final String key = "[\"" + dbName + "\",{\"server\":\"" + dbName + "\"}]";
    final String value =
        "{\"transaction_id\":null,\"ts_sec\":" + time.getEpochSecond() + ",\"file\":" + position.fileName + ",\"pos\":" + position.position
            + "}";

    final Map<String, String> result = new HashMap<>();
    result.put(key, value);

    final JsonNode jsonNode = Jsons.jsonNode(result);
    LOGGER.info("Initial Debezium state constructed: {}", jsonNode);

    return jsonNode;
  }

}
