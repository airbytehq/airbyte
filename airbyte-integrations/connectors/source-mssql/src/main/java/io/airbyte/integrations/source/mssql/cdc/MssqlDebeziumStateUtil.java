/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql.cdc;

import static io.debezium.relational.RelationalDatabaseConnectorConfig.DATABASE_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteFileOffsetBackingStore;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteSchemaHistoryStorage;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteSchemaHistoryStorage.SchemaHistory;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumPropertiesManager;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumRecordPublisher;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumStateUtil;
import io.airbyte.cdk.integrations.debezium.internals.RecordWaitTimeUtil;
import io.airbyte.cdk.integrations.debezium.internals.RelationalDbDebeziumPropertiesManager;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.debezium.config.Configuration;
import io.debezium.connector.common.OffsetReader;
import io.debezium.connector.sqlserver.Lsn;
import io.debezium.connector.sqlserver.SqlServerConnectorConfig;
import io.debezium.connector.sqlserver.SqlServerOffsetContext;
import io.debezium.connector.sqlserver.SqlServerOffsetContext.Loader;
import io.debezium.connector.sqlserver.SqlServerPartition;
import io.debezium.engine.ChangeEvent;
import io.debezium.pipeline.spi.Offsets;
import io.debezium.pipeline.spi.Partition;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Properties;
import java.util.Set;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.stream.Stream;
import org.apache.kafka.connect.storage.FileOffsetBackingStore;
import org.apache.kafka.connect.storage.OffsetStorageReaderImpl;
import org.codehaus.plexus.util.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MssqlDebeziumStateUtil implements DebeziumStateUtil {

  // Testing is done concurrently so initialState is cached in a thread local variable
  // in order to provide each test thread with its own correct initial state
  private static ThreadLocal<JsonNode> initialState = new ThreadLocal<>();

  final static String LSN_OFFSET_INCLUDED_QUERY = """
                                                      DECLARE @saved_lsn BINARY(10), @min_lsn BINARY(10), @max_lsn BINARY(10), @res BIT
                                                      -- Set @saved_lsn = 0x0000DF7C000006A80006
                                                      Set @saved_lsn = ?
                                                      SELECT @min_lsn = MIN(start_lsn) FROM cdc.change_tables
                                                      SELECT @max_lsn = sys.fn_cdc_get_max_lsn()
                                                      IF (@saved_lsn >= @min_lsn)
                                                          Set @res = 1
                                                      ELSE
                                                          Set @res = 0
                                                      select @res as [included], @min_lsn as [min], @max_lsn as [max]
                                                  """;
  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlDebeziumStateUtil.class);

  /**
   * Generate initial state for debezium state.
   */
  public static synchronized JsonNode constructInitialDebeziumState(final Properties properties,
                                                                    final ConfiguredAirbyteCatalog catalog,
                                                                    final JdbcDatabase database) {
    // There is no need to construct an initial state after it was already constructed in this run
    // Starting and stopping mssql debezium too many times causes it to hang during shutdown
    if (initialState.get() == null) {
      properties.setProperty("heartbeat.interval.ms", "0");
      final JsonNode highWaterMark = constructLsnSnapshotState(database, database.getSourceConfig().get(JdbcUtils.DATABASE_KEY).asText());
      final AirbyteFileOffsetBackingStore emptyOffsetManager = AirbyteFileOffsetBackingStore.initializeState(null,
          Optional.empty());
      final AirbyteSchemaHistoryStorage schemaHistoryStorage =
          AirbyteSchemaHistoryStorage.initializeDBHistory(new SchemaHistory<>(Optional.empty(), false), false);
      final LinkedBlockingQueue<ChangeEvent<String, String>> queue = new LinkedBlockingQueue<>();
      final Instant engineStartTime = Instant.now();
      boolean schemaHistoryRead = false;
      SchemaHistory<String> schemaHistory = null;
      final var debeziumPropertiesManager =
          new RelationalDbDebeziumPropertiesManager(properties, database.getSourceConfig(), catalog, Collections.emptyList());
      try {
        final DebeziumRecordPublisher publisher = new DebeziumRecordPublisher(debeziumPropertiesManager);
        publisher.start(queue, emptyOffsetManager, Optional.of(schemaHistoryStorage));
        while (!publisher.hasClosed()) {
          final ChangeEvent<String, String> event = queue.poll(10, TimeUnit.SECONDS);

          // If no event such as an empty table, generating schema history may take a few cycles
          // depending on the size of history.
          schemaHistory = schemaHistoryStorage.read();
          schemaHistoryRead = Objects.nonNull(schemaHistory) && StringUtils.isNotBlank(schemaHistory.getSchema());

          if (event != null || schemaHistoryRead) {
            publisher.close();
            break;
          }

          Duration initialWaitingDuration = Duration.ofMinutes(5L);
          // If initial waiting seconds is configured and it's greater than 5 minutes, use that value instead
          // of the default value
          final Duration configuredDuration = RecordWaitTimeUtil.getFirstRecordWaitTime(database.getSourceConfig());
          if (configuredDuration.compareTo(initialWaitingDuration) > 0) {
            initialWaitingDuration = configuredDuration;
          }
          if (Duration.between(engineStartTime, Instant.now()).compareTo(initialWaitingDuration) > 0) {
            LOGGER.error("Schema history not constructed after {} seconds of waiting, closing the engine", initialWaitingDuration.getSeconds());
            publisher.close();
            throw new RuntimeException(
                "Building schema history has timed out. Please consider increasing the debezium wait time in advanced options.");
          }
        }
      } catch (final InterruptedException ine) {
        LOGGER.debug("Interrupted during closing of publisher");
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }

      final AirbyteFileOffsetBackingStore offsetManager = AirbyteFileOffsetBackingStore.initializeState(highWaterMark,
          Optional.empty());

      final Map<String, String> offset = offsetManager.read();
      if (!schemaHistoryRead) {
        schemaHistory = schemaHistoryStorage.read();
      }

      assert !offset.isEmpty();
      assert Objects.nonNull(schemaHistory);
      assert Objects.nonNull(schemaHistory.getSchema());

      final JsonNode asJson = serialize(offset, schemaHistory);
      LOGGER.info("Initial Debezium state constructed. offset={}", Jsons.jsonNode(offset));

      if (asJson.get(MssqlCdcStateConstants.MSSQL_DB_HISTORY).asText().isBlank()) {
        throw new RuntimeException("Schema history snapshot returned empty history.");
      }
      initialState.set(asJson);
    }
    return initialState.get();

  }

  public static void disposeInitialState() {
    LOGGER.debug("Dispose initial state cached for {}", Thread.currentThread());
    initialState.remove();
  }

  private static JsonNode serialize(final Map<String, String> offset, final SchemaHistory<String> dbHistory) {
    final Map<String, Object> state = new HashMap<>();
    state.put(MssqlCdcStateConstants.MSSQL_CDC_OFFSET, offset);
    state.put(MssqlCdcStateConstants.MSSQL_DB_HISTORY, dbHistory.getSchema());
    state.put(MssqlCdcStateConstants.IS_COMPRESSED, dbHistory.isCompressed());

    return Jsons.jsonNode(state);
  }

  public static MssqlDebeziumStateAttributes getStateAttributesFromDB(final JdbcDatabase database) {
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
  static JsonNode constructLsnSnapshotState(final JdbcDatabase database, final String dbName) {
    return format(getStateAttributesFromDB(database), dbName);
  }

  @VisibleForTesting
  public static JsonNode format(final MssqlDebeziumStateAttributes attributes, final String dbName) {
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

  public Optional<MssqlDebeziumStateAttributes> savedOffset(final Properties baseProperties,
                                                            final ConfiguredAirbyteCatalog catalog,
                                                            final JsonNode cdcOffset,
                                                            final JsonNode config) {
    if (Objects.isNull(cdcOffset)) {
      return Optional.empty();
    }

    final var offsetManager = AirbyteFileOffsetBackingStore.initializeState(cdcOffset, Optional.empty());
    final DebeziumPropertiesManager debeziumPropertiesManager =
        new RelationalDbDebeziumPropertiesManager(baseProperties, config, catalog, Collections.emptyList());
    final Properties debeziumProperties = debeziumPropertiesManager.getDebeziumProperties(offsetManager);
    return parseSavedOffset(debeziumProperties);
  }

  private Optional<MssqlDebeziumStateAttributes> parseSavedOffset(final Properties properties) {
    FileOffsetBackingStore fileOffsetBackingStore = null;
    OffsetStorageReaderImpl offsetStorageReader = null;

    try {
      fileOffsetBackingStore = getFileOffsetBackingStore(properties);
      offsetStorageReader = getOffsetStorageReader(fileOffsetBackingStore, properties);

      final SqlServerConnectorConfig connectorConfig = new SqlServerConnectorConfig(Configuration.from(properties));
      final SqlServerOffsetContext.Loader loader = new Loader(connectorConfig);
      final Set<Partition> partitions =
          Collections.singleton(new SqlServerPartition(connectorConfig.getLogicalName(), properties.getProperty(DATABASE_NAME.name())));
      final OffsetReader<Partition, SqlServerOffsetContext, Loader> offsetReader = new OffsetReader<>(offsetStorageReader, loader);
      final Map<Partition, SqlServerOffsetContext> offsets = offsetReader.offsets(partitions);
      return extractStateAttributes(partitions, offsets);
    } finally {
      LOGGER.info("Closing offsetStorageReader and fileOffsetBackingStore");
      if (offsetStorageReader != null) {
        offsetStorageReader.close();
      }

      if (fileOffsetBackingStore != null) {
        fileOffsetBackingStore.stop();
      }

    }
  }

  private Optional<MssqlDebeziumStateAttributes> extractStateAttributes(final Set<Partition> partitions,
                                                                        final Map<Partition, SqlServerOffsetContext> offsets) {
    boolean found = false;
    for (final Partition partition : partitions) {
      final SqlServerOffsetContext mssqlOffsetContext = offsets.get(partition);

      if (mssqlOffsetContext != null) {
        found = true;
        LOGGER.info("Found previous partition offset {}: {}", partition, mssqlOffsetContext.getOffset());
      }
    }

    if (!found) {
      LOGGER.info("No previous offsets found");
      return Optional.empty();
    }

    final Offsets<Partition, SqlServerOffsetContext> of = Offsets.of(offsets);
    final SqlServerOffsetContext previousOffset = of.getTheOnlyOffset();
    return Optional.of(new MssqlDebeziumStateAttributes(previousOffset.getChangePosition().getCommitLsn()));
  }

  public boolean savedOffsetStillPresentOnServer(final JdbcDatabase database, final MssqlDebeziumStateAttributes savedState) {
    final Lsn savedLsn = savedState.lsn();
    try (final Stream<Boolean> stream = database.unsafeResultSetQuery(
        connection -> {
          PreparedStatement stmt = connection.prepareStatement(LSN_OFFSET_INCLUDED_QUERY);
          stmt.setBytes(1, savedLsn.getBinary());
          return stmt.executeQuery();
        },
        resultSet -> {
          final byte[] minLsnBinary = resultSet.getBytes(2);
          Lsn min_lsn = Lsn.valueOf(minLsnBinary);
          final byte[] maxLsnBinary = resultSet.getBytes(3);
          Lsn max_lsn = Lsn.valueOf(maxLsnBinary);
          final Boolean included = resultSet.getBoolean(1);
          LOGGER.info("{} lsn exists on server: [{}]. (min server lsn: {} max server lsn: {})", savedLsn.toString(), included, min_lsn.toString(),
              max_lsn.toString());
          return included;
        })) {
      final List<Boolean> reses = stream.toList();
      assert reses.size() == 1;

      return reses.get(0);
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

}
