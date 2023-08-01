/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static io.airbyte.integrations.base.JavaBaseConstants.AIRBYTE_NAMESPACE_SCHEMA;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Functions;
import com.google.common.base.Preconditions;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.TypingAndDedupingFlag;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.TypeAndDedupeOperationValve;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnCloseFunction;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnStartFunction;
import io.airbyte.integrations.destination.record_buffer.BufferCreateFunction;
import io.airbyte.integrations.destination.record_buffer.FlushBufferFunction;
import io.airbyte.integrations.destination.record_buffer.SerializedBufferingStrategy;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class mimics the same functionality as
 * {@link io.airbyte.integrations.destination.staging.StagingConsumerFactory} which likely should be
 * placed into a commons package to be utilized across all ConsumerFactories
 */
public class BigQueryStagingConsumerFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryStagingConsumerFactory.class);

  public AirbyteMessageConsumer create(final JsonNode config,
                                       final ConfiguredAirbyteCatalog catalog,
                                       final Consumer<AirbyteMessage> outputRecordCollector,
                                       final BigQueryStagingOperations bigQueryGcsOperations,
                                       final BufferCreateFunction onCreateBuffer,
                                       final Function<JsonNode, BigQueryRecordFormatter> recordFormatterCreator,
                                       final Function<String, String> tmpTableNameTransformer,
                                       final Function<String, String> targetTableNameTransformer,
                                       final TyperDeduper typerDeduper,
                                       final ParsedCatalog parsedCatalog,
                                       final String defaultNamespace)
      throws Exception {
    final Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs = createWriteConfigs(
        config,
        catalog,
        parsedCatalog,
        recordFormatterCreator,
        tmpTableNameTransformer,
        targetTableNameTransformer);

    CheckedConsumer<AirbyteStreamNameNamespacePair, Exception> typeAndDedupeStreamFunction =
        incrementalTypingAndDedupingStreamConsumer(typerDeduper);

    return new BufferedStreamConsumer(
        outputRecordCollector,
        onStartFunction(bigQueryGcsOperations, writeConfigs, typerDeduper),
        new SerializedBufferingStrategy(
            onCreateBuffer,
            catalog,
            flushBufferFunction(bigQueryGcsOperations, writeConfigs, catalog, typeAndDedupeStreamFunction)),
        onCloseFunction(bigQueryGcsOperations, writeConfigs, typerDeduper),
        catalog,
        json -> true,
        defaultNamespace);
  }

  private CheckedConsumer<AirbyteStreamNameNamespacePair, Exception> incrementalTypingAndDedupingStreamConsumer(final TyperDeduper typerDeduper) {
    final TypeAndDedupeOperationValve valve = new TypeAndDedupeOperationValve();
    return (streamId) -> {
      if (!valve.containsKey(streamId)) {
        valve.addStream(streamId);
      }
      if (valve.readyToTypeAndDedupe(streamId)) {
        typerDeduper.typeAndDedupe(streamId.getNamespace(), streamId.getName());
        valve.updateTimeAndIncreaseInterval(streamId);
      }
    };
  }

  private Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> createWriteConfigs(final JsonNode config,
                                                                                      final ConfiguredAirbyteCatalog catalog,
                                                                                      final ParsedCatalog parsedCatalog,
                                                                                      final Function<JsonNode, BigQueryRecordFormatter> recordFormatterCreator,
                                                                                      final Function<String, String> tmpTableNameTransformer,
                                                                                      final Function<String, String> targetTableNameTransformer) {
    return catalog.getStreams().stream()
        .map(configuredStream -> {
          Preconditions.checkNotNull(configuredStream.getDestinationSyncMode(), "Undefined destination sync mode");

          final AirbyteStream stream = configuredStream.getStream();
          StreamConfig streamConfig = parsedCatalog.getStream(stream.getNamespace(), stream.getName());
          final String streamName = stream.getName();
          final BigQueryRecordFormatter recordFormatter = recordFormatterCreator.apply(stream.getJsonSchema());

          final var internalTableNamespace = TypingAndDedupingFlag.isDestinationV2() ? streamConfig.id().rawNamespace() : BigQueryUtils.sanitizeDatasetId(stream.getNamespace());
          final var targetTableName =
              TypingAndDedupingFlag.isDestinationV2() ? streamConfig.id().rawName() : targetTableNameTransformer.apply(streamName);

          final BigQueryWriteConfig writeConfig = new BigQueryWriteConfig(
              streamName,
              stream.getNamespace(),
              internalTableNamespace,
              BigQueryUtils.getDatasetLocation(config),
              tmpTableNameTransformer.apply(streamName),
              targetTableName,
              recordFormatter.getBigQuerySchema(),
              configuredStream.getDestinationSyncMode());

          LOGGER.info("BigQuery write config: {}", writeConfig);

          return writeConfig;
        })
        .collect(Collectors.toMap(
            c -> new AirbyteStreamNameNamespacePair(c.streamName(), c.namespace()),
            Functions.identity()));
  }

  /**
   * Sets up {@link BufferedStreamConsumer} with creation of the destination's raw tables
   *
   * <p>
   * Note: targetTableId is synonymous with airbyte_raw table
   * </p>
   *
   * @param bigQueryGcsOperations collection of Google Cloud Storage Operations
   * @param writeConfigs configuration settings used to describe how to write data and where it exists
   */
  private OnStartFunction onStartFunction(final BigQueryStagingOperations bigQueryGcsOperations,
                                          final Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs,
                                          final TyperDeduper typerDeduper) {
    return () -> {
      LOGGER.info("Preparing airbyte_raw tables in destination started for {} streams", writeConfigs.size());
      for (final BigQueryWriteConfig writeConfig : writeConfigs.values()) {
        LOGGER.info("Preparing staging are in destination for schema: {}, stream: {}, target table: {}, stage: {}",
            writeConfig.tableSchema(), writeConfig.streamName(), writeConfig.targetTableId(), writeConfig.streamName());
        // In Destinations V2, we will always use the 'airbyte' schema/namespace for raw tables
        final String rawDatasetId = TypingAndDedupingFlag.isDestinationV2() ? AIRBYTE_NAMESPACE_SCHEMA : writeConfig.datasetId();
        // Regardless, ensure the schema the customer wants to write to exists
        bigQueryGcsOperations.createSchemaIfNotExists(writeConfig.datasetId(), writeConfig.datasetLocation());
        // Schema used for raw and airbyte internal tables
        bigQueryGcsOperations.createSchemaIfNotExists(rawDatasetId, writeConfig.datasetLocation());
        // Customer's destination schema
        // With checkpointing, we will be creating the target table earlier in the setup such that
        // the data can be immediately loaded from the staging area
        bigQueryGcsOperations.createTableIfNotExists(writeConfig.targetTableId(), writeConfig.tableSchema());
        bigQueryGcsOperations.createStageIfNotExists(rawDatasetId, writeConfig.streamName());
        // When OVERWRITE mode, truncate the destination's raw table prior to syncing data
        if (writeConfig.syncMode() == DestinationSyncMode.OVERWRITE) {
          // TODO: this might need special handling during the migration
          bigQueryGcsOperations.truncateTableIfExists(rawDatasetId, writeConfig.targetTableId(), writeConfig.tableSchema());
        }
      }
      typerDeduper.prepareFinalTables();
      LOGGER.info("Preparing tables in destination completed.");
    };
  }

  /**
   * Flushes buffer data, writes to staging environment then proceeds to upload those same records to
   * destination table
   *
   * @param bigQueryGcsOperations collection of utility SQL operations
   * @param writeConfigs book keeping configurations for writing and storing state to write records
   * @param catalog configured Airbyte catalog
   */
  private FlushBufferFunction flushBufferFunction(
                                                  final BigQueryStagingOperations bigQueryGcsOperations,
                                                  final Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs,
                                                  final ConfiguredAirbyteCatalog catalog,
                                                  final CheckedConsumer<AirbyteStreamNameNamespacePair, Exception> incrementalTypeAndDedupeConsumer) {
    return (pair, writer) -> {
      LOGGER.info("Flushing buffer for stream {} ({}) to staging", pair.getName(), FileUtils.byteCountToDisplaySize(writer.getByteCount()));
      if (!writeConfigs.containsKey(pair)) {
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream that was not in the catalog: %s.\nKeys: %s\ncatalog: %s", pair,
                writeConfigs.keySet(), Jsons.serialize(catalog)));
      }

      final BigQueryWriteConfig writeConfig = writeConfigs.get(pair);
      final String datasetId = writeConfig.datasetId();
      final String stream = writeConfig.streamName();
      try (writer) {
        writer.flush();
        final String stagedFile = bigQueryGcsOperations.uploadRecordsToStage(datasetId, stream, writer);
        /*
         * The primary reason for still adding staged files despite immediately uploading the staged file to
         * the destination's raw table is because the cleanup for the staged files will occur at the end of
         * the sync
         */
        writeConfig.addStagedFile(stagedFile);
        bigQueryGcsOperations.copyIntoTableFromStage(datasetId, stream, writeConfig.targetTableId(), writeConfig.tableSchema(),
            List.of(stagedFile));
        incrementalTypeAndDedupeConsumer.accept(new AirbyteStreamNameNamespacePair(writeConfig.streamName(), writeConfig.namespace()));
      } catch (final Exception e) {
        LOGGER.error("Failed to flush and commit buffer data into destination's raw table:", e);
        throw new RuntimeException("Failed to upload buffer to stage and commit to destination", e);
      }
    };
  }

  /**
   * Tear down process, will attempt to clean out any staging area
   *
   * @param bigQueryGcsOperations collection of staging operations
   * @param writeConfigs          configuration settings used to describe how to write data and where it exists
   */
  private OnCloseFunction onCloseFunction(final BigQueryStagingOperations bigQueryGcsOperations,
                                          final Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs,
                                          final TyperDeduper typerDeduper) {
    return (hasFailed) -> {
      /*
       * Previously the hasFailed value was used to commit any remaining staged files into destination,
       * however, with the changes to checkpointing this will no longer be necessary since despite partial
       * successes, we'll be committing the target table (aka airbyte_raw) table throughout the sync
       */

      LOGGER.info("Cleaning up destination started for {} streams", writeConfigs.size());
      for (final Map.Entry<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> entry : writeConfigs.entrySet()) {
        typerDeduper.typeAndDedupe(entry.getKey().getNamespace(), entry.getKey().getName());
        bigQueryGcsOperations.dropStageIfExists(entry.getValue().datasetId(), entry.getValue().streamName());
      }
      typerDeduper.commitFinalTables();
      LOGGER.info("Cleaning up destination completed.");
    };
  }

}
