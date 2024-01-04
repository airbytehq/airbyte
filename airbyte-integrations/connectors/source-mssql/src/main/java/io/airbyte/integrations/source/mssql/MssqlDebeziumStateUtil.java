package io.airbyte.integrations.source.mssql;

import static io.airbyte.cdk.integrations.debezium.internals.mysql.MysqlCdcStateConstants.COMPRESSION_ENABLED;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteFileOffsetBackingStore;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteSchemaHistoryStorage;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteSchemaHistoryStorage.SchemaHistory;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumPropertiesManager;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumRecordPublisher;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumStateUtil;
import io.airbyte.cdk.integrations.debezium.internals.RecordWaitTimeUtil;
import io.airbyte.cdk.integrations.debezium.internals.mysql.MysqlCdcStateConstants;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.debezium.engine.ChangeEvent;
import java.time.Duration;
import java.time.Instant;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Properties;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;

public class MssqlDebeziumStateUtil implements DebeziumStateUtil {
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
    final AirbyteSchemaHistoryStorage schemaHistoryStorage =
        AirbyteSchemaHistoryStorage.initializeDBHistory(new SchemaHistory<>(Optional.empty(), false), COMPRESSION_ENABLED);
    final LinkedBlockingQueue<ChangeEvent<String, String>> queue = new LinkedBlockingQueue<>();
    try (final DebeziumRecordPublisher publisher = new DebeziumRecordPublisher(properties,
        database.getSourceConfig(),
        catalog,
        offsetManager,
        Optional.of(schemaHistoryStorage),
        DebeziumPropertiesManager.DebeziumConnectorType.RELATIONALDB)) {
      publisher.start(queue);
      final Instant engineStartTime = Instant.now();
      while (!publisher.hasClosed()) {
        final ChangeEvent<String, String> event = queue.poll(10, TimeUnit.SECONDS);
        if (event == null) {
          Duration initialWaitingDuration = Duration.ofMinutes(5L);
          // If initial waiting seconds is configured and it's greater than 5 minutes, use that value instead
          // of the default value
          final Duration configuredDuration = RecordWaitTimeUtil.getFirstRecordWaitTime(database.getSourceConfig());
          if (configuredDuration.compareTo(initialWaitingDuration) > 0) {
            initialWaitingDuration = configuredDuration;
          }
          if (Duration.between(engineStartTime, Instant.now()).compareTo(initialWaitingDuration) > 0) {
            LOGGER.error("No record is returned even after {} seconds of waiting, closing the engine", initialWaitingDuration.getSeconds());
            publisher.close();
            throw new RuntimeException(
                "Building schema history has timed out. Please consider increasing the debezium wait time in advanced options.");
          }
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
    final SchemaHistory schemaHistory = schemaHistoryStorage.read();

    assert !offset.isEmpty();
    assert Objects.nonNull(schemaHistory);
    assert Objects.nonNull(schemaHistory.schema());

    final JsonNode asJson = serialize(offset, schemaHistory);
    LOGGER.info("Initial Debezium state constructed: {}", asJson);

    if (asJson.get(MysqlCdcStateConstants.MYSQL_DB_HISTORY).asText().isBlank()) {
      throw new RuntimeException("Schema history snapshot returned empty history.");
    }
    return asJson;

  }
}
