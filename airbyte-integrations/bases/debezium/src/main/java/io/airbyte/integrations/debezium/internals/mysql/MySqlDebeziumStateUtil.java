/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.debezium.internals.AirbyteFileOffsetBackingStore;
import io.airbyte.integrations.debezium.internals.AirbyteSchemaHistoryStorage;
import io.airbyte.integrations.debezium.internals.DebeziumRecordPublisher;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.debezium.engine.ChangeEvent;
import java.sql.SQLException;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Properties;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlDebeziumStateUtil {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlDebeziumStateUtil.class);
  public static final String MYSQL_CDC_OFFSET = "mysql_cdc_offset";
  public static final String MYSQL_DB_HISTORY = "mysql_db_history";

  public JsonNode constructInitialDebeziumState(final Properties properties,
                                                final ConfiguredAirbyteCatalog catalog,
                                                final JdbcDatabase database) {
    // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-snapshot-mode
    // We use the schema_only_recovery property cause using this mode will instruct Debezium to
    // construct the db schema history.
    properties.setProperty("snapshot.mode", "schema_only_recovery");
    final AirbyteFileOffsetBackingStore offsetManager = AirbyteFileOffsetBackingStore.initializeState(
        constructBinlogOffset(database, database.getSourceConfig().get(JdbcUtils.DATABASE_KEY).asText()),
        Optional.empty());
    final AirbyteSchemaHistoryStorage schemaHistoryStorage = AirbyteSchemaHistoryStorage.initializeDBHistory(Optional.empty());
    final LinkedBlockingQueue<ChangeEvent<String, String>> queue = new LinkedBlockingQueue<>();
    try (final DebeziumRecordPublisher publisher = new DebeziumRecordPublisher(properties, database.getSourceConfig(), catalog, offsetManager,
        Optional.of(schemaHistoryStorage))) {
      publisher.start(queue);
      while (!publisher.hasClosed()) {
        final ChangeEvent<String, String> event = queue.poll(10, TimeUnit.SECONDS);
        if (event == null) {
          continue;
        }
        LOGGER.info("A record is returned, closing the engine since the state is constructed");
        publisher.close();
        break;
      }
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }

    final Map<String, String> offset = offsetManager.read();
    final String dbHistory = schemaHistoryStorage.read();

    assert !offset.isEmpty();
    assert Objects.nonNull(dbHistory);

    final Map<String, Object> state = new HashMap<>();
    state.put(MYSQL_CDC_OFFSET, offset);
    state.put(MYSQL_DB_HISTORY, dbHistory);

    final JsonNode asJson = Jsons.jsonNode(state);
    LOGGER.info("Initial Debezium state constructed: {}", asJson);

    return asJson;
  }

  /**
   * Method to construct initial Debezium state which can be passed onto Debezium engine to make it
   * process binlogs from a specific file and position and skip snapshot phase
   */
  private JsonNode constructBinlogOffset(final JdbcDatabase database, final String dbName) {
    return format(getStateAttributesFromDB(database), dbName, Instant.now());
  }

  @VisibleForTesting
  public JsonNode format(final MysqlDebeziumStateAttributes attributes, final String dbName, final Instant time) {
    final String key = "[\"" + dbName + "\",{\"server\":\"" + dbName + "\"}]";
    final String gtidSet = attributes.gtidSet().isPresent() ? ",\"gtids\":\"" + attributes.gtidSet().get() + "\"" : "";
    final String value =
        "{\"transaction_id\":null,\"ts_sec\":" + time.getEpochSecond() + ",\"file\":\"" + attributes.binlogFilename() + "\",\"pos\":"
            + attributes.binlogPosition()
            + gtidSet + "}";

    final Map<String, String> result = new HashMap<>();
    result.put(key, value);

    final JsonNode jsonNode = Jsons.jsonNode(result);
    LOGGER.info("Initial Debezium state offset constructed: {}", jsonNode);

    return jsonNode;
  }

  public MysqlDebeziumStateAttributes getStateAttributesFromDB(final JdbcDatabase database) {
    try (final Stream<MysqlDebeziumStateAttributes> stream = database.unsafeResultSetQuery(
        connection -> connection.createStatement().executeQuery("SHOW MASTER STATUS"),
        resultSet -> {
          final String file = resultSet.getString("File");
          final long position = resultSet.getLong("Position");
          assert file != null;
          assert position >= 0;
          if (resultSet.getMetaData().getColumnCount() > 4) {
            // This column exists only in MySQL 5.6.5 or later ...
            final String gtidSet = resultSet.getString(5); // GTID set, may be null, blank, or contain a GTID set
            return new MysqlDebeziumStateAttributes(file, position, removeNewLineChars(gtidSet));
          }
          return new MysqlDebeziumStateAttributes(file, position, Optional.empty());
        })) {
      final List<MysqlDebeziumStateAttributes> stateAttributes = stream.toList();
      assert stateAttributes.size() == 1;
      return stateAttributes.get(0);
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  private Optional<String> removeNewLineChars(final String gtidSet) {
    if (gtidSet != null && !gtidSet.trim().isEmpty()) {
      // Remove all the newline chars that exist in the GTID set string ...
      return Optional.of(gtidSet.replace("\n", "").replace("\r", ""));
    }

    return Optional.empty();
  }

  public record MysqlDebeziumStateAttributes(String binlogFilename, long binlogPosition, Optional<String> gtidSet) {

  }

}
