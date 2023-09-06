/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals.mysql;

import static io.debezium.relational.RelationalDatabaseConnectorConfig.DATABASE_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.debezium.internals.AirbyteFileOffsetBackingStore;
import io.airbyte.integrations.debezium.internals.AirbyteSchemaHistoryStorage;
import io.airbyte.integrations.debezium.internals.DebeziumPropertiesManager;
import io.airbyte.integrations.debezium.internals.DebeziumRecordPublisher;
import io.airbyte.integrations.debezium.internals.RelationalDbDebeziumPropertiesManager;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.debezium.config.Configuration;
import io.debezium.connector.common.OffsetReader;
import io.debezium.connector.mysql.GtidSet;
import io.debezium.connector.mysql.MySqlConnectorConfig;
import io.debezium.connector.mysql.MySqlOffsetContext;
import io.debezium.connector.mysql.MySqlOffsetContext.Loader;
import io.debezium.connector.mysql.MySqlPartition;
import io.debezium.engine.ChangeEvent;
import io.debezium.pipeline.spi.Offsets;
import io.debezium.pipeline.spi.Partition;
import java.sql.PreparedStatement;
import java.sql.SQLException;
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
import org.apache.kafka.connect.json.JsonConverter;
import org.apache.kafka.connect.json.JsonConverterConfig;
import org.apache.kafka.connect.runtime.WorkerConfig;
import org.apache.kafka.connect.runtime.standalone.StandaloneConfig;
import org.apache.kafka.connect.storage.FileOffsetBackingStore;
import org.apache.kafka.connect.storage.OffsetStorageReaderImpl;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlDebeziumStateUtil {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlDebeziumStateUtil.class);
  public static final String MYSQL_CDC_OFFSET = "mysql_cdc_offset";
  public static final String MYSQL_DB_HISTORY = "mysql_db_history";

  public boolean savedOffsetStillPresentOnServer(final JdbcDatabase database, final MysqlDebeziumStateAttributes savedState) {
    if (savedState.gtidSet().isPresent()) {
      final Optional<String> availableGtidStr = getStateAttributesFromDB(database).gtidSet();
      if (availableGtidStr.isEmpty()) {
        // Last offsets had GTIDs but the server does not use them
        LOGGER.info("Connector used GTIDs previously, but MySQL server does not know of any GTIDs or they are not enabled");
        return false;
      }
      final GtidSet gtidSetFromSavedState = new GtidSet(savedState.gtidSet().get());
      // Get the GTID set that is available in the server
      final GtidSet availableGtidSet = new GtidSet(availableGtidStr.get());
      if (gtidSetFromSavedState.isContainedWithin(availableGtidSet)) {
        LOGGER.info("MySQL server current GTID set {} does contain the GTID set required by the connector {}", availableGtidSet,
            gtidSetFromSavedState);
        final Optional<GtidSet> gtidSetToReplicate = subtractGtidSet(availableGtidSet, gtidSetFromSavedState, database);
        if (gtidSetToReplicate.isPresent()) {
          final Optional<GtidSet> purgedGtidSet = purgedGtidSet(database);
          if (purgedGtidSet.isPresent()) {
            LOGGER.info("MySQL server has already purged {} GTIDs", purgedGtidSet.get());
            final Optional<GtidSet> nonPurgedGtidSetToReplicate = subtractGtidSet(gtidSetToReplicate.get(), purgedGtidSet.get(), database);
            if (nonPurgedGtidSetToReplicate.isPresent()) {
              LOGGER.info("GTIDs known by the MySQL server but not processed yet {}, for replication are available only {}", gtidSetToReplicate,
                  nonPurgedGtidSetToReplicate);
              if (!gtidSetToReplicate.equals(nonPurgedGtidSetToReplicate)) {
                LOGGER.info("Some of the GTIDs needed to replicate have been already purged by MySQL server");
                return false;
              }
            }
          }
        }
        return true;
      }
      LOGGER.info("Connector last known GTIDs are {}, but MySQL server only has {}", gtidSetFromSavedState, availableGtidSet);
      return false;
    }

    final List<String> existingLogFiles = getExistingLogFiles(database);
    final boolean found = existingLogFiles.stream().anyMatch(savedState.binlogFilename()::equals);
    if (!found) {
      LOGGER.info("Connector requires binlog file '{}', but MySQL server only has {}", savedState.binlogFilename(),
          String.join(", ", existingLogFiles));
    } else {
      LOGGER.info("MySQL server has the binlog file '{}' required by the connector", savedState.binlogFilename());
    }

    return found;

  }

  private List<String> getExistingLogFiles(final JdbcDatabase database) {
    try (final Stream<String> stream = database.unsafeResultSetQuery(
        connection -> connection.createStatement().executeQuery("SHOW BINARY LOGS"),
        resultSet -> resultSet.getString(1))) {
      return stream.toList();
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  private Optional<GtidSet> subtractGtidSet(final GtidSet set1, final GtidSet set2, final JdbcDatabase database) {
    try (final Stream<GtidSet> stream = database.unsafeResultSetQuery(
        connection -> {
          final PreparedStatement ps = connection.prepareStatement("SELECT GTID_SUBTRACT(?, ?)");
          ps.setString(1, set1.toString());
          ps.setString(2, set2.toString());
          return ps.executeQuery();
        },
        resultSet -> new GtidSet(resultSet.getString(1)))) {
      final List<GtidSet> gtidSets = stream.toList();
      if (gtidSets.isEmpty()) {
        return Optional.empty();
      } else if (gtidSets.size() == 1) {
        return Optional.of(gtidSets.get(0));
      } else {
        throw new RuntimeException("Not expecting gtid set size to be greater than 1");
      }
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  private Optional<GtidSet> purgedGtidSet(final JdbcDatabase database) {
    try (final Stream<Optional<GtidSet>> stream = database.unsafeResultSetQuery(
        connection -> connection.createStatement().executeQuery("SELECT @@global.gtid_purged"),
        resultSet -> {
          if (resultSet.getMetaData().getColumnCount() > 0) {
            String string = resultSet.getString(1);
            if (string != null && !string.isEmpty()) {
              return Optional.of(new GtidSet(string));
            }
          }
          return Optional.empty();
        })) {
      List<Optional<GtidSet>> gtidSet = stream.toList();
      if (gtidSet.isEmpty()) {
        return Optional.empty();
      } else if (gtidSet.size() == 1) {
        return gtidSet.get(0);
      } else {
        throw new RuntimeException("Not expecting the size to be greater than 1");
      }
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  public Optional<MysqlDebeziumStateAttributes> savedOffset(final Properties baseProperties,
                                                            final ConfiguredAirbyteCatalog catalog,
                                                            final JsonNode cdcOffset,
                                                            final JsonNode config) {
    if (Objects.isNull(cdcOffset)) {
      return Optional.empty();
    }

    final DebeziumPropertiesManager debeziumPropertiesManager = new RelationalDbDebeziumPropertiesManager(baseProperties, config, catalog,
        AirbyteFileOffsetBackingStore.initializeState(cdcOffset, Optional.empty()),
        Optional.empty());
    final Properties debeziumProperties = debeziumPropertiesManager.getDebeziumProperties();
    return parseSavedOffset(debeziumProperties);
  }

  private Optional<MysqlDebeziumStateAttributes> parseSavedOffset(final Properties properties) {

    FileOffsetBackingStore fileOffsetBackingStore = null;
    OffsetStorageReaderImpl offsetStorageReader = null;
    try {
      fileOffsetBackingStore = new FileOffsetBackingStore();
      final Map<String, String> propertiesMap = Configuration.from(properties).asMap();
      propertiesMap.put(WorkerConfig.KEY_CONVERTER_CLASS_CONFIG, JsonConverter.class.getName());
      propertiesMap.put(WorkerConfig.VALUE_CONVERTER_CLASS_CONFIG, JsonConverter.class.getName());
      fileOffsetBackingStore.configure(new StandaloneConfig(propertiesMap));
      fileOffsetBackingStore.start();

      final Map<String, String> internalConverterConfig = Collections.singletonMap(JsonConverterConfig.SCHEMAS_ENABLE_CONFIG, "false");
      final JsonConverter keyConverter = new JsonConverter();
      keyConverter.configure(internalConverterConfig, true);
      final JsonConverter valueConverter = new JsonConverter();
      valueConverter.configure(internalConverterConfig, false);

      final MySqlConnectorConfig connectorConfig = new MySqlConnectorConfig(Configuration.from(properties));
      final MySqlOffsetContext.Loader loader = new MySqlOffsetContext.Loader(connectorConfig);
      final Set<Partition> partitions =
          Collections.singleton(new MySqlPartition(connectorConfig.getLogicalName(), properties.getProperty(DATABASE_NAME.name())));

      offsetStorageReader = new OffsetStorageReaderImpl(fileOffsetBackingStore, properties.getProperty("name"), keyConverter,
          valueConverter);
      final OffsetReader<Partition, MySqlOffsetContext, Loader> offsetReader = new OffsetReader<>(offsetStorageReader,
          loader);
      final Map<Partition, MySqlOffsetContext> offsets = offsetReader.offsets(partitions);

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

  private Optional<MysqlDebeziumStateAttributes> extractStateAttributes(final Set<Partition> partitions,
                                                                        final Map<Partition, MySqlOffsetContext> offsets) {
    boolean found = false;
    for (final Partition partition : partitions) {
      final MySqlOffsetContext mySqlOffsetContext = offsets.get(partition);

      if (mySqlOffsetContext != null) {
        found = true;
        LOGGER.info("Found previous partition offset {}: {}", partition, mySqlOffsetContext.getOffset());
      }
    }

    if (!found) {
      LOGGER.info("No previous offsets found");
      return Optional.empty();
    }

    final Offsets<Partition, MySqlOffsetContext> of = Offsets.of(offsets);
    final MySqlOffsetContext previousOffset = of.getTheOnlyOffset();

    return Optional.of(new MysqlDebeziumStateAttributes(previousOffset.getSource().binlogFilename(), previousOffset.getSource().binlogPosition(),
        Optional.ofNullable(previousOffset.gtidSet())));

  }

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
    try (final DebeziumRecordPublisher publisher = new DebeziumRecordPublisher(properties,
        database.getSourceConfig(),
        catalog,
        offsetManager,
        Optional.of(schemaHistoryStorage),
        DebeziumPropertiesManager.DebeziumConnectorType.RELATIONALDB)) {
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

  public static MysqlDebeziumStateAttributes getStateAttributesFromDB(final JdbcDatabase database) {
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

  private static Optional<String> removeNewLineChars(final String gtidSet) {
    if (gtidSet != null && !gtidSet.trim().isEmpty()) {
      // Remove all the newline chars that exist in the GTID set string ...
      return Optional.of(gtidSet.replace("\n", "").replace("\r", ""));
    }

    return Optional.empty();
  }

  public record MysqlDebeziumStateAttributes(String binlogFilename, long binlogPosition, Optional<String> gtidSet) {

  }

}
