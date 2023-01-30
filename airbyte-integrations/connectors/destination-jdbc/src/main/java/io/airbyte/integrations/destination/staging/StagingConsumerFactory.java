/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.staging;

import static java.util.stream.Collectors.joining;
import static java.util.stream.Collectors.toList;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.functional.CheckedBiConsumer;
import io.airbyte.commons.functional.CheckedBiFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnCloseFunction;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnStartFunction;
import io.airbyte.integrations.destination.jdbc.WriteConfig;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.destination.record_buffer.SerializedBufferingStrategy;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.function.Function;
import org.apache.commons.io.FileUtils;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Uses both Factory and Consumer design pattern to create a single point of creation for consuming {@link AirbyteMessage} for processing
 */
public class StagingConsumerFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(StagingConsumerFactory.class);

  // using a random string here as a placeholder for the moment.
  // This would avoid mixing data in the staging area between different syncs (especially if they
  // manipulate streams with similar names)
  // if we replaced the random connection id by the actual connection_id, we'd gain the opportunity to
  // leverage data that was uploaded to stage
  // in a previous attempt but failed to load to the warehouse for some reason (interrupted?) instead.
  // This would also allow other programs/scripts
  // to load (or reload backups?) in the connection's staging area to be loaded at the next sync.
  private static final DateTime SYNC_DATETIME = DateTime.now(DateTimeZone.UTC);
  private final UUID RANDOM_CONNECTION_ID = UUID.randomUUID();

  public AirbyteMessageConsumer create(final Consumer<AirbyteMessage> outputRecordCollector,
                                       final JdbcDatabase database,
                                       final StagingOperations stagingOperations,
                                       final NamingConventionTransformer namingResolver,
                                       final CheckedBiFunction<AirbyteStreamNameNamespacePair, ConfiguredAirbyteCatalog, SerializableBuffer, Exception> onCreateBuffer,
                                       final JsonNode config,
                                       final ConfiguredAirbyteCatalog catalog,
                                       final boolean purgeStagingData) {
    final List<WriteConfig> writeConfigs = createWriteConfigs(namingResolver, config, catalog);
    return new BufferedStreamConsumer(
        outputRecordCollector,
        onStartFunction(database, stagingOperations, writeConfigs),
        new SerializedBufferingStrategy(
            onCreateBuffer,
            catalog,
            flushBufferFunction(database, stagingOperations, writeConfigs, catalog)),
        onCloseFunction(database, stagingOperations, writeConfigs, purgeStagingData),
        catalog,
        stagingOperations::isValidData);
  }

  /**
   * Creates a list of all {@link WriteConfig} for each stream within a {@link ConfiguredAirbyteCatalog}. Each write config represents the configuration
   * settings for writing to a destination connector
   *
   * @param namingResolver {@link NamingConventionTransformer} used to transform names that are acceptable by each destination connector
   * @param config destination connector configuration parameters
   * @param catalog {@link ConfiguredAirbyteCatalog} collection of configured {@link ConfiguredAirbyteStream}
   * @return list of all write configs for each stream in a {@link ConfiguredAirbyteCatalog}
   */
  private static List<WriteConfig> createWriteConfigs(final NamingConventionTransformer namingResolver,
                                                      final JsonNode config,
                                                      final ConfiguredAirbyteCatalog catalog) {

    return catalog.getStreams().stream().map(toWriteConfig(namingResolver, config)).collect(toList());
  }

  private static Function<ConfiguredAirbyteStream, WriteConfig> toWriteConfig(final NamingConventionTransformer namingResolver,
                                                                              final JsonNode config) {
    return stream -> {
      Preconditions.checkNotNull(stream.getDestinationSyncMode(), "Undefined destination sync mode");
      final AirbyteStream abStream = stream.getStream();

      final String outputSchema = getOutputSchema(abStream, config.get("schema").asText(), namingResolver);

      final String streamName = abStream.getName();
      final String tableName = namingResolver.getRawTableName(streamName);
      final String tmpTableName = namingResolver.getTmpTableName(streamName);
      final DestinationSyncMode syncMode = stream.getDestinationSyncMode();

      final WriteConfig writeConfig =
          new WriteConfig(streamName, abStream.getNamespace(), outputSchema, tmpTableName, tableName, syncMode, SYNC_DATETIME);
      LOGGER.info("Write config: {}", writeConfig);

      return writeConfig;
    };
  }

  private static String getOutputSchema(final AirbyteStream stream,
                                        final String defaultDestSchema,
                                        final NamingConventionTransformer namingResolver) {
    return stream.getNamespace() != null
        ? namingResolver.getNamespace(stream.getNamespace())
        : namingResolver.getNamespace(defaultDestSchema);
  }

  private OnStartFunction onStartFunction(final JdbcDatabase database,
                                          final StagingOperations stagingOperations,
                                          final List<WriteConfig> writeConfigs) {
    return () -> {
      LOGGER.info("Preparing raw tables in destination started for {} streams", writeConfigs.size());
      final List<String> queryList = new ArrayList<>();
      for (final WriteConfig writeConfig : writeConfigs) {
        final String schema = writeConfig.getOutputSchemaName();
        final String stream = writeConfig.getStreamName();
        final String dstTableName = writeConfig.getOutputTableName();
        final String stageName = stagingOperations.getStageName(schema, stream);
        final String stagingPath = stagingOperations.getStagingPath(RANDOM_CONNECTION_ID, schema, stream, writeConfig.getWriteDatetime());

        LOGGER.info("Preparing staging area in destination started for schema {} stream {}: target table: {}, stage: {}",
            schema, stream, dstTableName, stagingPath);

        stagingOperations.createSchemaIfNotExists(database, schema);
        stagingOperations.createTableIfNotExists(database, schema, dstTableName);
        stagingOperations.createStageIfNotExists(database, stageName);

        /*
         * When we're in OVERWRITE, clear out the table at the start of a sync, this is an expected
         * side effect of checkpoint and the removal of temporary tables
         */
        switch (writeConfig.getSyncMode()) {
          case OVERWRITE -> queryList.add(stagingOperations.truncateTableQuery(database, schema, dstTableName));
          case APPEND, APPEND_DEDUP -> {}
          default -> throw new IllegalStateException("Unrecognized sync mode: " + writeConfig.getSyncMode());
        }

        LOGGER.info("Preparing staging area in destination completed for schema {} stream {}", schema, stream);
      }
      LOGGER.info("Executing finalization of tables.");
      stagingOperations.executeTransaction(database, queryList);
    };
  }

  private static AirbyteStreamNameNamespacePair toNameNamespacePair(final WriteConfig config) {
    return new AirbyteStreamNameNamespacePair(config.getStreamName(), config.getNamespace());
  }

  /**
   * Logic handling how destinations with staging areas (aka bucket storages) will flush their buffer
   *
   * @param database database used for syncing
   * @param stagingOperations collection of SQL queries necessary for writing data into a staging area
   * @param writeConfigs configuration settings for all destination connectors needed to write
   * @param catalog collection of configured streams (e.g. API endpoints or database tables)
   * @return
   */
  @VisibleForTesting
  CheckedBiConsumer<AirbyteStreamNameNamespacePair, SerializableBuffer, Exception> flushBufferFunction(
                                                                                                               final JdbcDatabase database,
                                                                                                               final StagingOperations stagingOperations,
                                                                                                               final List<WriteConfig> writeConfigs,
                                                                                                               final ConfiguredAirbyteCatalog catalog) {
    final Set<WriteConfig> conflictingStreams = new HashSet<>();
    final Map<AirbyteStreamNameNamespacePair, WriteConfig> pairToWriteConfig = new HashMap<>();
    for (final WriteConfig config : writeConfigs) {
      final AirbyteStreamNameNamespacePair streamIdentifier = toNameNamespacePair(config);
      if (pairToWriteConfig.containsKey(streamIdentifier)) {
        conflictingStreams.add(config);
        final WriteConfig existingConfig = pairToWriteConfig.get(streamIdentifier);
        // The first conflicting stream won't have any problems, so we need to explicitly add it here.
        conflictingStreams.add(existingConfig);
      } else {
        pairToWriteConfig.put(streamIdentifier, config);
      }
    }
    if (!conflictingStreams.isEmpty()) {
      final String message = String.format(
          "You are trying to write multiple streams to the same table. Consider switching to a custom namespace format using ${SOURCE_NAMESPACE}, or moving one of them into a separate connection with a different stream prefix. Affected streams: %s",
          conflictingStreams.stream().map(config -> config.getNamespace() + "." + config.getStreamName()).collect(joining(", "))
      );
      throw new ConfigErrorException(message);
    }
    return (pair, writer) -> {
      LOGGER.info("Flushing buffer for stream {} ({}) to staging", pair.getName(), FileUtils.byteCountToDisplaySize(writer.getByteCount()));
      if (!pairToWriteConfig.containsKey(pair)) {
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s", Jsons.serialize(catalog)));
      }

      final WriteConfig writeConfig = pairToWriteConfig.get(pair);
      final String schemaName = writeConfig.getOutputSchemaName();
      final String stageName = stagingOperations.getStageName(schemaName, writeConfig.getStreamName());
      final String stagingPath =
          stagingOperations.getStagingPath(RANDOM_CONNECTION_ID, schemaName, writeConfig.getStreamName(), writeConfig.getWriteDatetime());
      try (writer) {
        writer.flush();
        final String stagedFile = stagingOperations.uploadRecordsToStage(database, writer, schemaName, stageName, stagingPath);
        copyIntoTableFromStage(database, stageName, stagingPath, List.of(stagedFile), writeConfig.getOutputTableName(), schemaName, stagingOperations);
      } catch (final Exception e) {
        LOGGER.error("Failed to flush and commit buffer data into destination's raw table", e);
        throw new RuntimeException("Failed to upload buffer to stage and commit to destination", e);
      }
    };
  }

  /**
   * Handles copying data from staging area to destination table and clean up of staged files if
   * upload was unsuccessful
   */
  private void copyIntoTableFromStage(final JdbcDatabase database,
                                         final String stageName,
                                         final String stagingPath,
                                         final List<String> stagedFiles,
                                         final String tableName,
                                         final String schemaName,
                                         final StagingOperations stagingOperations) throws Exception {
    try {
      stagingOperations.copyIntoTableFromStage(database, stageName, stagingPath, stagedFiles,
          tableName, schemaName);
    } catch (final Exception e) {
      stagingOperations.cleanUpStage(database, stageName, stagedFiles);
      LOGGER.info("Cleaning stage path {}", stagingPath);
      throw new RuntimeException("Failed to upload data from stage " + stagingPath, e);
    }
  }

  /**
   * Tear down process, will attempt to try to clean out any staging area
   *
   * @param database database used for syncing
   * @param stagingOperations collection of SQL queries necessary for writing data into a staging area
   * @param writeConfigs configuration settings for all destination connectors needed to write
   * @param purgeStagingData drop staging area if true, keep otherwise
   * @return
   */
  private OnCloseFunction onCloseFunction(final JdbcDatabase database,
                                          final StagingOperations stagingOperations,
                                          final List<WriteConfig> writeConfigs,
                                          final boolean purgeStagingData) {
    return (hasFailed) -> {
      if (!hasFailed) {
        stagingOperations.onDestinationCloseOperations(database, writeConfigs);
        LOGGER.info("Finalizing tables in destination completed.");
      }
      // After moving data from staging area to the target table (airybte_raw) clean up the staging
      // area (if user configured)
      LOGGER.info("Cleaning up destination started for {} streams", writeConfigs.size());
      for (final WriteConfig writeConfig : writeConfigs) {
        final String schemaName = writeConfig.getOutputSchemaName();
        if (purgeStagingData) {
          final String stageName = stagingOperations.getStageName(schemaName, writeConfig.getStreamName());
          LOGGER.info("Cleaning stage in destination started for stream {}. schema {}, stage: {}", writeConfig.getStreamName(), schemaName,
              stageName);
          stagingOperations.dropStageIfExists(database, stageName);
        }
      }
      LOGGER.info("Cleaning up destination completed.");
    };
  }
}
