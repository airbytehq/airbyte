/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.staging;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
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
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.stream.Collectors;
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

    return catalog.getStreams().stream().map(toWriteConfig(namingResolver, config)).collect(Collectors.toList());
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
      LOGGER.info("Preparing tmp tables in destination started for {} streams", writeConfigs.size());
      for (final WriteConfig writeConfig : writeConfigs) {
        final String schema = writeConfig.getOutputSchemaName();
        final String stream = writeConfig.getStreamName();
        final String tmpTable = writeConfig.getTmpTableName();
        final String stageName = stagingOperations.getStageName(schema, stream);
        final String stagingPath = stagingOperations.getStagingPath(RANDOM_CONNECTION_ID, schema, stream, writeConfig.getWriteDatetime());

        LOGGER.info("Preparing staging area in destination started for schema {} stream {}: tmp table: {}, stage: {}",
            schema, stream, tmpTable, stagingPath);

        stagingOperations.createSchemaIfNotExists(database, schema);
        stagingOperations.createTableIfNotExists(database, schema, tmpTable);
        stagingOperations.createStageIfNotExists(database, stageName);

        LOGGER.info("Preparing staging area in destination completed for schema {} stream {}", schema, stream);
      }

      LOGGER.info("Preparing tmp tables in destination completed.");
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
  private CheckedBiConsumer<AirbyteStreamNameNamespacePair, SerializableBuffer, Exception> flushBufferFunction(
                                                                                                               final JdbcDatabase database,
                                                                                                               final StagingOperations stagingOperations,
                                                                                                               final List<WriteConfig> writeConfigs,
                                                                                                               final ConfiguredAirbyteCatalog catalog) {
    final Map<AirbyteStreamNameNamespacePair, WriteConfig> pairToWriteConfig =
        writeConfigs.stream()
            .collect(Collectors.toUnmodifiableMap(
                StagingConsumerFactory::toNameNamespacePair, Function.identity()));

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
        writeConfig.addStagedFile(stagingOperations.uploadRecordsToStage(database, writer, schemaName, stageName, stagingPath));
      } catch (final Exception e) {
        LOGGER.error("Failed to flush and upload buffer to stage:", e);
        throw new RuntimeException("Failed to upload buffer to stage", e);
      }
    };
  }

  /**
   * Upon processing all {@link AirbyteMessage} wrap up lingering logic. This logic includes:
   * <li>Migrating data stored in staging area to temporary tables</li>
   * <li>Creates a final table (if one does not already exist)</li>
   * <li>Inserts all data from the temporary table into the final table</li>
   *
   * @param database database used for syncing
   * @param stagingOperations SQL queries used to write and delete data from the staging folder
   * @param writeConfigs list of all write configs for each stream in a {@link ConfiguredAirbyteCatalog}
   * @param purgeStagingData purges staging data if true otherwise data retained
   * @return
   */
  private OnCloseFunction onCloseFunction(final JdbcDatabase database,
                                          final StagingOperations stagingOperations,
                                          final List<WriteConfig> writeConfigs,
                                          final boolean purgeStagingData) {
    return (hasFailed) -> {
      if (!hasFailed) {
        final List<String> queryList = new ArrayList<>();
        LOGGER.info("Copying into tables in destination started for {} streams", writeConfigs.size());

        for (final WriteConfig writeConfig : writeConfigs) {
          final String schemaName = writeConfig.getOutputSchemaName();
          final String streamName = writeConfig.getStreamName();
          final String srcTableName = writeConfig.getTmpTableName();
          final String dstTableName = writeConfig.getOutputTableName();
          final String stageName = stagingOperations.getStageName(schemaName, streamName);
          final String stagingPath = stagingOperations.getStagingPath(RANDOM_CONNECTION_ID, schemaName, streamName, writeConfig.getWriteDatetime());
          LOGGER.info("Copying stream {} of schema {} into tmp table {} to final table {} from stage path {} with {} file(s) [{}]",
              streamName, schemaName, srcTableName, dstTableName, stagingPath, writeConfig.getStagedFiles().size(),
              String.join(",", writeConfig.getStagedFiles()));

          // Copies all the data stored in the staging files into a temporary table and creates final table if nonexistent
          try {
            stagingOperations.copyIntoTmpTableFromStage(database, stageName, stagingPath, writeConfig.getStagedFiles(), srcTableName, schemaName);
          } catch (final Exception e) {
            stagingOperations.cleanUpStage(database, stageName, writeConfig.getStagedFiles());
            LOGGER.info("Cleaning stage path {}", stagingPath);
            throw new RuntimeException("Failed to upload data from stage " + stagingPath, e);
          }
          writeConfig.clearStagedFiles();
          stagingOperations.createTableIfNotExists(database, schemaName, dstTableName);
          switch (writeConfig.getSyncMode()) {
            case OVERWRITE -> queryList.add(stagingOperations.truncateTableQuery(database, schemaName, dstTableName));
            case APPEND, APPEND_DEDUP -> {}
            default -> throw new IllegalStateException("Unrecognized sync mode: " + writeConfig.getSyncMode());
          }
          queryList.add(stagingOperations.insertTableQuery(database, schemaName, srcTableName, dstTableName));
        }
        stagingOperations.onDestinationCloseOperations(database, writeConfigs);
        LOGGER.info("Executing finalization of tables.");
        // copies data from temporary table into final table (airbyte_raw)
        stagingOperations.executeTransaction(database, queryList);
        LOGGER.info("Finalizing tables in destination completed.");
      }
      // After moving data from staging area to the finalized table (airybte_raw) clean up temporary tables and the staging area (if user configured)
      LOGGER.info("Cleaning up destination started for {} streams", writeConfigs.size());
      for (final WriteConfig writeConfig : writeConfigs) {
        final String schemaName = writeConfig.getOutputSchemaName();
        final String tmpTableName = writeConfig.getTmpTableName();
        LOGGER.info("Cleaning tmp table in destination started for stream {}. schema {}, tmp table name: {}", writeConfig.getStreamName(), schemaName,
            tmpTableName);

        stagingOperations.dropTableIfExists(database, schemaName, tmpTableName);
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
