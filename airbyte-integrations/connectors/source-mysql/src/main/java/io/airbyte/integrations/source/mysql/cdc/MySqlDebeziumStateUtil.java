/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.cdc;

import static io.airbyte.integrations.source.mysql.cdc.MysqlCdcStateConstants.COMPRESSION_ENABLED;
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
import io.debezium.connector.mysql.MySqlConnectorConfig;
import io.debezium.connector.mysql.MySqlOffsetContext;
import io.debezium.connector.mysql.MySqlOffsetContext.Loader;
import io.debezium.connector.mysql.MySqlPartition;
import io.debezium.connector.mysql.gtid.MySqlGtidSet;
import io.debezium.engine.ChangeEvent;
import io.debezium.pipeline.spi.Offsets;
import io.debezium.pipeline.spi.Partition;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
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
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlDebeziumStateUtil implements DebeziumStateUtil {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlDebeziumStateUtil.class);

  public boolean savedOffsetStillPresentOnServer(final JdbcDatabase database, final MysqlDebeziumStateAttributes savedState) {
    if (savedState.gtidSet().isPresent()) {
      final Optional<String> availableGtidStr = getStateAttributesFromDB(database).gtidSet();
      if (availableGtidStr.isEmpty()) {
        // Last offsets had GTIDs but the server does not use them
        LOGGER.info("Connector used GTIDs previously, but MySQL server does not know of any GTIDs or they are not enabled");
        return false;
      }
      final MySqlGtidSet gtidSetFromSavedState = new MySqlGtidSet(savedState.gtidSet().get());
      // Get the GTID set that is available in the server
      final MySqlGtidSet availableGtidSet = new MySqlGtidSet(availableGtidStr.get());
      if (gtidSetFromSavedState.isContainedWithin(availableGtidSet)) {
        LOGGER.info("MySQL server current GTID set {} does contain the GTID set required by the connector {}", availableGtidSet,
            gtidSetFromSavedState);
        final Optional<MySqlGtidSet> gtidSetToReplicate = subtractGtidSet(availableGtidSet, gtidSetFromSavedState, database);
        if (gtidSetToReplicate.isPresent()) {
          final Optional<MySqlGtidSet> purgedGtidSet = purgedGtidSet(database);
          if (purgedGtidSet.isPresent()) {
            LOGGER.info("MySQL server has already purged {} GTIDs", purgedGtidSet.get());
            final Optional<MySqlGtidSet> nonPurgedGtidSetToReplicate = subtractGtidSet(gtidSetToReplicate.get(), purgedGtidSet.get(), database);
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

  private Optional<MySqlGtidSet> subtractGtidSet(final MySqlGtidSet set1, final MySqlGtidSet set2, final JdbcDatabase database) {
    try (final Stream<MySqlGtidSet> stream = database.unsafeResultSetQuery(
        connection -> {
          final PreparedStatement ps = connection.prepareStatement("SELECT GTID_SUBTRACT(?, ?)");
          ps.setString(1, set1.toString());
          ps.setString(2, set2.toString());
          return ps.executeQuery();
        },
        resultSet -> new MySqlGtidSet(resultSet.getString(1)))) {
      final List<MySqlGtidSet> gtidSets = stream.toList();
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

  private Optional<MySqlGtidSet> purgedGtidSet(final JdbcDatabase database) {
    try (final Stream<Optional<MySqlGtidSet>> stream = database.unsafeResultSetQuery(
        connection -> connection.createStatement().executeQuery("SELECT @@global.gtid_purged"),
        resultSet -> {
          if (resultSet.getMetaData().getColumnCount() > 0) {
            String string = resultSet.getString(1);
            if (string != null && !string.isEmpty()) {
              return Optional.of(new MySqlGtidSet(string));
            }
          }
          return Optional.empty();
        })) {
      final List<Optional<MySqlGtidSet>> gtidSet = stream.toList();
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

    final var offsetManager = AirbyteFileOffsetBackingStore.initializeState(cdcOffset, Optional.empty());
    final DebeziumPropertiesManager debeziumPropertiesManager = new RelationalDbDebeziumPropertiesManager(baseProperties, config, catalog,
        new ArrayList<String>());
    final Properties debeziumProperties = debeziumPropertiesManager.getDebeziumProperties(offsetManager);
    return parseSavedOffset(debeziumProperties);
  }

  private Optional<MysqlDebeziumStateAttributes> parseSavedOffset(final Properties properties) {
    FileOffsetBackingStore fileOffsetBackingStore = null;
    OffsetStorageReaderImpl offsetStorageReader = null;

    try {
      fileOffsetBackingStore = getFileOffsetBackingStore(properties);
      offsetStorageReader = getOffsetStorageReader(fileOffsetBackingStore, properties);

      final MySqlConnectorConfig connectorConfig = new MySqlConnectorConfig(Configuration.from(properties));
      final MySqlOffsetContext.Loader loader = new MySqlOffsetContext.Loader(connectorConfig);
      final Set<Partition> partitions =
          Collections.singleton(new MySqlPartition(connectorConfig.getLogicalName(), properties.getProperty(DATABASE_NAME.name())));

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
    // We use the recovery property cause using this mode will instruct Debezium to
    // construct the db schema history.
    // Note that we used to use schema_only_recovery mode, but this mode has been deprecated.
    properties.setProperty("snapshot.mode", "recovery");
    final String dbName = database.getSourceConfig().get(JdbcUtils.DATABASE_KEY).asText();
    // Topic.prefix is sanitized version of database name. At this stage properties does not have this
    // value - it's set in RelationalDbDebeziumPropertiesManager.
    final AirbyteFileOffsetBackingStore offsetManager = AirbyteFileOffsetBackingStore.initializeState(
        constructBinlogOffset(database, dbName, DebeziumPropertiesManager.sanitizeTopicPrefix(dbName)),
        Optional.empty());
    final AirbyteSchemaHistoryStorage schemaHistoryStorage =
        AirbyteSchemaHistoryStorage.initializeDBHistory(new SchemaHistory<>(Optional.empty(), false), COMPRESSION_ENABLED);
    final LinkedBlockingQueue<ChangeEvent<String, String>> queue = new LinkedBlockingQueue<>();
    final var debeziumPropertiesManager =
        new RelationalDbDebeziumPropertiesManager(properties, database.getSourceConfig(), catalog, new ArrayList<String>());

    try (final DebeziumRecordPublisher publisher = new DebeziumRecordPublisher(debeziumPropertiesManager)) {
      publisher.start(queue, offsetManager, Optional.of(schemaHistoryStorage));
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
    assert Objects.nonNull(schemaHistory.getSchema());

    final JsonNode asJson = serialize(offset, schemaHistory);
    LOGGER.info("Initial Debezium state constructed: {}", asJson);

    if (asJson.get(MysqlCdcStateConstants.MYSQL_DB_HISTORY).asText().isBlank()) {
      throw new RuntimeException("Schema history snapshot returned empty history.");
    }
    return asJson;
  }

  public static JsonNode serialize(final Map<String, String> offset, final SchemaHistory dbHistory) {
    final Map<String, Object> state = new HashMap<>();
    state.put(MysqlCdcStateConstants.MYSQL_CDC_OFFSET, offset);
    state.put(MysqlCdcStateConstants.MYSQL_DB_HISTORY, dbHistory.getSchema());
    state.put(MysqlCdcStateConstants.IS_COMPRESSED, dbHistory.isCompressed());

    return Jsons.jsonNode(state);
  }

  /**
   * Method to construct initial Debezium state which can be passed onto Debezium engine to make it
   * process binlogs from a specific file and position and skip snapshot phase
   */
  private JsonNode constructBinlogOffset(final JdbcDatabase database, final String debeziumName, final String topicPrefixName) {
    return format(getStateAttributesFromDB(database), debeziumName, topicPrefixName, Instant.now());
  }

  @VisibleForTesting
  public JsonNode format(final MysqlDebeziumStateAttributes attributes, final String debeziumName, final String topicPrefixName, final Instant time) {
    final String key = "[\"" + debeziumName + "\",{\"server\":\"" + topicPrefixName + "\"}]";
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
