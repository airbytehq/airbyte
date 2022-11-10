/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import static io.debezium.connector.postgresql.PostgresOffsetContext.LAST_COMMIT_LSN_KEY;
import static io.debezium.connector.postgresql.SourceInfo.LSN_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.debezium.config.Configuration;
import io.debezium.connector.common.OffsetReader;
import io.debezium.connector.postgresql.PostgresConnectorConfig;
import io.debezium.connector.postgresql.PostgresOffsetContext;
import io.debezium.connector.postgresql.PostgresOffsetContext.Loader;
import io.debezium.connector.postgresql.PostgresPartition;
import io.debezium.connector.postgresql.connection.Lsn;
import io.debezium.pipeline.spi.Offsets;
import io.debezium.pipeline.spi.Partition;
import java.util.Collections;
import java.util.Map;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.Properties;
import java.util.Set;
import org.apache.kafka.connect.json.JsonConverter;
import org.apache.kafka.connect.runtime.WorkerConfig;
import org.apache.kafka.connect.runtime.standalone.StandaloneConfig;
import org.apache.kafka.connect.storage.FileOffsetBackingStore;
import org.apache.kafka.connect.storage.OffsetStorageReaderImpl;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class is inspired by Debezium's Postgres connector internal implementation on how it parses
 * the state
 */
public class PostgresDebeziumStateUtil {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresDebeziumStateUtil.class);

  public boolean isSavedOffsetAfterReplicationSlotLSN(final Properties baseProperties,
                                                      final ConfiguredAirbyteCatalog catalog,
                                                      final JsonNode cdcState,
                                                      final JsonNode replicationSlot,
                                                      final JsonNode config) {

    final DebeziumPropertiesManager debeziumPropertiesManager = new DebeziumPropertiesManager(baseProperties, config, catalog,
        AirbyteFileOffsetBackingStore.initializeState(cdcState),
        Optional.empty());
    final Properties debeziumProperties = debeziumPropertiesManager.getDebeziumProperties();
    final OptionalLong savedOffset = parseSavedOffset(debeziumProperties);

    if (savedOffset.isPresent()) {
      if (replicationSlot.has("confirmed_flush_lsn")) {
        final long confirmedFlushLsnOnServerSide = Lsn.valueOf(replicationSlot.get("confirmed_flush_lsn").asText()).asLong();
        LOGGER.info("Replication slot confirmed_flush_lsn : " + confirmedFlushLsnOnServerSide + " Saved offset LSN : " + savedOffset.getAsLong());
        return savedOffset.getAsLong() >= confirmedFlushLsnOnServerSide;
      } else if (replicationSlot.has("restart_lsn")) {
        final long restartLsn = Lsn.valueOf(replicationSlot.get("restart_lsn").asText()).asLong();
        LOGGER.info("Replication slot restart_lsn : " + restartLsn + " Saved offset LSN : " + savedOffset.getAsLong());
        return savedOffset.getAsLong() >= restartLsn;
      }
    }

    // We return true when saved offset is not present cause using an empty offset would result in sync
    // from scratch anyway
    return true;
  }

  /**
   *
   * @param properties Properties should contain the relevant properties like path to the debezium
   *        state file, etc. It's assumed that the state file is already initialised with the saved
   *        state
   * @return Returns the LSN that Airbyte has acknowledged in the source database server
   */
  private OptionalLong parseSavedOffset(final Properties properties) {

    FileOffsetBackingStore fileOffsetBackingStore = null;
    OffsetStorageReaderImpl offsetStorageReader = null;
    try {
      fileOffsetBackingStore = new FileOffsetBackingStore();
      final Map<String, String> propertiesMap = Configuration.from(properties).asMap();
      propertiesMap.put(WorkerConfig.KEY_CONVERTER_CLASS_CONFIG, JsonConverter.class.getName());
      propertiesMap.put(WorkerConfig.VALUE_CONVERTER_CLASS_CONFIG, JsonConverter.class.getName());
      fileOffsetBackingStore.configure(new StandaloneConfig(propertiesMap));
      fileOffsetBackingStore.start();

      final JsonConverter keyConverter = new JsonConverter();
      keyConverter.configure(Configuration.from(properties).subset("internal.key.converter" + ".", true).asMap(), true);
      final JsonConverter valueConverter = new JsonConverter();
      // Make sure that the JSON converter is configured to NOT enable schemas ...
      final Configuration valueConverterConfig = Configuration.from(properties).edit().with("internal.value.converter" + ".schemas.enable", false)
          .build();
      valueConverter.configure(valueConverterConfig.subset("internal.value.converter" + ".", true).asMap(), false);

      offsetStorageReader = new OffsetStorageReaderImpl(fileOffsetBackingStore, properties.getProperty("name"), keyConverter,
          valueConverter);
      final PostgresConnectorConfig postgresConnectorConfig = new PostgresConnectorConfig(Configuration.from(properties));
      final PostgresCustomLoader loader = new PostgresCustomLoader(postgresConnectorConfig);
      final OffsetReader<Partition, PostgresOffsetContext, Loader> offsetReader = new OffsetReader<>(offsetStorageReader, loader);
      final Set<Partition> partitions = Collections.singleton(new PostgresPartition(postgresConnectorConfig.getLogicalName()));
      final Map<Partition, PostgresOffsetContext> offsets = offsetReader.offsets(partitions);

      return extractLsn(partitions, offsets, loader);

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

  private OptionalLong extractLsn(final Set<Partition> partitions,
                                  final Map<Partition, PostgresOffsetContext> offsets,
                                  final PostgresCustomLoader loader) {
    boolean found = false;
    for (final Partition partition : partitions) {
      final PostgresOffsetContext postgresOffsetContext = offsets.get(partition);

      if (postgresOffsetContext != null) {
        found = true;
        LOGGER.info("Found previous partition offset {}: {}", partition, postgresOffsetContext.getOffset());
      }
    }

    if (!found) {
      LOGGER.info("No previous offsets found");
      return OptionalLong.empty();
    }

    final Offsets<Partition, PostgresOffsetContext> of = Offsets.of(offsets);
    final PostgresOffsetContext previousOffset = of.getTheOnlyOffset();

    final Map<String, ?> offset = previousOffset.getOffset();

    if (offset.containsKey(LAST_COMMIT_LSN_KEY)) {
      return OptionalLong.of((long) offset.get(LAST_COMMIT_LSN_KEY));
    } else if (offset.containsKey(LSN_KEY)) {
      return OptionalLong.of((long) offset.get(LSN_KEY));
    } else if (loader.getRawOffset().containsKey(LSN_KEY)) {
      return OptionalLong.of(Long.parseLong(loader.getRawOffset().get(LSN_KEY).toString()));
    }

    return OptionalLong.empty();

  }

}
