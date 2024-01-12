/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debezium.internals.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteFileOffsetBackingStore;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteSchemaHistoryStorage;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteSchemaHistoryStorage.SchemaHistory;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumPropertiesManager;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumRecordPublisher;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.debezium.connector.sqlserver.Lsn;
import io.debezium.engine.ChangeEvent;
import java.sql.SQLException;
import java.time.Duration;
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

public class MssqlDebeziumStateUtil {

  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlDebeziumStateUtil.class);

  /**
   * Generate initial state for debezium state.
   */
  public JsonNode constructInitialDebeziumState(final Properties properties,
                                                final ConfiguredAirbyteCatalog catalog,
                                                final JdbcDatabase database) {
    final JsonNode highWaterMark = constructLsnSnapshotState(database, database.getSourceConfig().get(JdbcUtils.DATABASE_KEY).asText());
    final AirbyteFileOffsetBackingStore emptyOffsetManager = AirbyteFileOffsetBackingStore.initializeState(null,
        Optional.empty());
    final AirbyteSchemaHistoryStorage schemaHistoryStorage =
        AirbyteSchemaHistoryStorage.initializeDBHistory(new SchemaHistory<>(Optional.empty(), false), false);
    final LinkedBlockingQueue<ChangeEvent<String, String>> queue = new LinkedBlockingQueue<>();
    final Instant engineStartTime = Instant.now();
    try {
      final DebeziumRecordPublisher publisher = new DebeziumRecordPublisher(properties,
          database.getSourceConfig(),
          catalog,
          emptyOffsetManager,
          Optional.of(schemaHistoryStorage),
          DebeziumPropertiesManager.DebeziumConnectorType.RELATIONALDB);
      publisher.start(queue);
      while (!publisher.hasClosed()) {
        final ChangeEvent<String, String> event = queue.poll(10, TimeUnit.SECONDS);
        if (event != null) {
          publisher.close();
          break;
        }
        if (Duration.between(engineStartTime, Instant.now()).compareTo(Duration.ofMinutes(5)) > 0) {
          LOGGER.error("No record is returned even after {} seconds of waiting, closing the engine", 300);
          publisher.close();
          throw new RuntimeException(
              "Building schema history has timed out. Please consider increasing the debezium wait time in advanced options.");
        }
      }
    } catch (Exception e) {
      throw new RuntimeException(e);
    }

    final AirbyteFileOffsetBackingStore offsetManager = AirbyteFileOffsetBackingStore.initializeState(highWaterMark,
        Optional.empty());

    final Map<String, String> offset = offsetManager.read();
    final SchemaHistory<String> schemaHistory = schemaHistoryStorage.read();

    assert !offset.isEmpty();
    assert Objects.nonNull(schemaHistory);
    assert Objects.nonNull(schemaHistory.schema());

    final JsonNode asJson = serialize(offset, schemaHistory);
    LOGGER.info("Initial Debezium state constructed: {}", asJson);

    if (asJson.get(MssqlCdcStateConstants.MSSQL_DB_HISTORY).asText().isBlank()) {
      throw new RuntimeException("Schema history snapshot returned empty history.");
    }
    return asJson;

  }

  private static JsonNode serialize(final Map<String, String> offset, final SchemaHistory<String> dbHistory) {
    final Map<String, Object> state = new HashMap<>();
    state.put(MssqlCdcStateConstants.MSSQL_CDC_OFFSET, offset);
    state.put(MssqlCdcStateConstants.MSSQL_DB_HISTORY, dbHistory.schema());
    state.put(MssqlCdcStateConstants.IS_COMPRESSED, dbHistory.isCompressed());

    return Jsons.jsonNode(state);
  }

  private static MssqlDebeziumStateAttributes getStateAttributesFromDB(final JdbcDatabase database) {
    try (final Stream<MssqlDebeziumStateAttributes> stream = database.unsafeResultSetQuery(
        connection -> connection.createStatement().executeQuery("select sys.fn_cdc_get_max_lsn()"),
        resultSet -> {
          final byte[] lsnBinary = resultSet.getBytes(1);
          Lsn lsn = Lsn.valueOf(lsnBinary);
          return new MssqlDebeziumStateAttributes(lsn);
        })) {
      final List<MssqlDebeziumStateAttributes> stateAttributes = stream.toList();
      assert stateAttributes.size() == 1;
      return stateAttributes.get(0);
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  public record MssqlDebeziumStateAttributes(Lsn lsn) {}

  /**
   * Method to construct initial Debezium state which can be passed onto Debezium engine to make it
   * process binlogs from a specific file and position and skip snapshot phase Example:
   * ["test",{"server":"test","database":"test"}]" :
   * "{"transaction_id":null,"event_serial_no":1,"commit_lsn":"00000644:00002ff8:0099","change_lsn":"0000062d:00017ff0:016d"}"
   */
  JsonNode constructLsnSnapshotState(final JdbcDatabase database, final String dbName) {
    return format(getStateAttributesFromDB(database), dbName);
  }

  @VisibleForTesting
  JsonNode format(final MssqlDebeziumStateAttributes attributes, final String dbName) {
    final String key = "[\"" + dbName + "\",{\"server\":\"" + dbName + "\",\"database\":\"" + dbName + "\"}]";
    final String value =
        "{\"commit_lsn\":\"" + attributes.lsn.toString() + "\",\"snapshot\":true,\"snapshot_completed\":true"
            + "}";

    final Map<String, String> result = new HashMap<>();
    result.put(key, value);

    final JsonNode jsonNode = Jsons.jsonNode(result);
    LOGGER.info("Initial Debezium state offset constructed: {}", jsonNode);

    return jsonNode;
  }

}
