/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Functions;
import com.google.common.base.Preconditions;
import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.functional.CheckedBiConsumer;
import io.airbyte.commons.functional.CheckedBiFunction;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
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
 * This class mimics the same functionality as {@link io.airbyte.integrations.destination.staging.StagingConsumerFactory}
 * which likely should be placed into a commons package to be utilized across all ConsumerFactories
 */
public class BigQueryStagingConsumerFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryStagingConsumerFactory.class);

  public AirbyteMessageConsumer create(final JsonNode config,
                                       final ConfiguredAirbyteCatalog catalog,
                                       final Consumer<AirbyteMessage> outputRecordCollector,
                                       final BigQueryStagingOperations bigQueryGcsOperations,
                                       final CheckedBiFunction<AirbyteStreamNameNamespacePair, ConfiguredAirbyteCatalog, SerializableBuffer, Exception> onCreateBuffer,
                                       final Function<JsonNode, BigQueryRecordFormatter> recordFormatterCreator,
                                       final Function<String, String> tmpTableNameTransformer,
                                       final Function<String, String> targetTableNameTransformer) {
    final Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs = createWriteConfigs(
        config,
        catalog,
        recordFormatterCreator,
        tmpTableNameTransformer,
        targetTableNameTransformer);

    return new BufferedStreamConsumer(
        outputRecordCollector,
        onStartFunction(bigQueryGcsOperations, writeConfigs),
        new SerializedBufferingStrategy(
            onCreateBuffer,
            catalog,
            flushBufferFunction(bigQueryGcsOperations, writeConfigs, catalog)),
        onCloseFunction(bigQueryGcsOperations, writeConfigs),
        catalog,
        json -> true);
  }

  private Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> createWriteConfigs(final JsonNode config,
                                                                                      final ConfiguredAirbyteCatalog catalog,
                                                                                      final Function<JsonNode, BigQueryRecordFormatter> recordFormatterCreator,
                                                                                      final Function<String, String> tmpTableNameTransformer,
                                                                                      final Function<String, String> targetTableNameTransformer) {
    return catalog.getStreams().stream()
        .map(configuredStream -> {
          Preconditions.checkNotNull(configuredStream.getDestinationSyncMode(), "Undefined destination sync mode");

          final AirbyteStream stream = configuredStream.getStream();
          final String streamName = stream.getName();
          final BigQueryRecordFormatter recordFormatter = recordFormatterCreator.apply(stream.getJsonSchema());

          final BigQueryWriteConfig writeConfig = new BigQueryWriteConfig(
              streamName,
              stream.getNamespace(),
              BigQueryUtils.getSchema(config, configuredStream),
              BigQueryUtils.getDatasetLocation(config),
              tmpTableNameTransformer.apply(streamName),
              targetTableNameTransformer.apply(streamName),
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
   * @return
   */
  private VoidCallable onStartFunction(final BigQueryStagingOperations bigQueryGcsOperations,
                                       final Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs) {
    return () -> {
      LOGGER.info("Preparing airbyte_raw tables in destination started for {} streams", writeConfigs.size());
      for (final BigQueryWriteConfig writeConfig : writeConfigs.values()) {
        LOGGER.info("Preparing staging are in destination for schema: {}, stream: {}, target table: {}, stage: {}",
            writeConfig.tableSchema(), writeConfig.streamName(), writeConfig.targetTableId(), writeConfig.streamName());
        final String datasetId = writeConfig.datasetId();
        bigQueryGcsOperations.createSchemaIfNotExists(datasetId, writeConfig.datasetLocation());
        // With checkpointing, we will be creating the target table earlier in the setup such that
        // the data can be immediately loaded from the staging area
        bigQueryGcsOperations.createTableIfNotExists(writeConfig.targetTableId(), writeConfig.tableSchema());
        bigQueryGcsOperations.createStageIfNotExists(datasetId, writeConfig.streamName());
        // When OVERWRITE mode, truncate the destination's raw table prior to syncing data
        if (writeConfig.syncMode() == DestinationSyncMode.OVERWRITE) {
          bigQueryGcsOperations.truncateTableIfExists(datasetId, writeConfig.targetTableId(), writeConfig.tableSchema());
        }
      }
      LOGGER.info("Preparing airbyte_raw tables in destination completed.");
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
  private CheckedBiConsumer<AirbyteStreamNameNamespacePair, SerializableBuffer, Exception> flushBufferFunction(final BigQueryStagingOperations bigQueryGcsOperations,
                                                                                                               final Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs,
                                                                                                               final ConfiguredAirbyteCatalog catalog) {
    return (pair, writer) -> {
      LOGGER.info("Flushing buffer for stream {} ({}) to staging", pair.getName(), FileUtils.byteCountToDisplaySize(writer.getByteCount()));
      if (!writeConfigs.containsKey(pair)) {
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s", Jsons.serialize(catalog)));
      }

      final BigQueryWriteConfig writeConfig = writeConfigs.get(pair);
      final String datasetId = writeConfig.datasetId();
      final String stream = writeConfig.streamName();
      try (writer) {
        writer.flush();
        final String stagedFile = bigQueryGcsOperations.uploadRecordsToStage(datasetId, stream, writer);
        /*
         * The primary reason for still adding staged files despite immediately uploading the staged
         * file to the destination's raw table is because the cleanup for the staged files will occur
         * at the end of the sync
         */
        writeConfig.addStagedFile(stagedFile);
        bigQueryGcsOperations.copyIntoTableFromStage(datasetId, stream, writeConfig.targetTableId(), writeConfig.tableSchema(),
            List.of(stagedFile));
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
   * @param writeConfigs configuration settings used to describe how to write data and where it exists
   * @return
   */
  private CheckedConsumer<Boolean, Exception> onCloseFunction(final BigQueryStagingOperations bigQueryGcsOperations,
                                                              final Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs) {
    return (hasFailed) -> {
      /*
       * Previously the hasFailed value was used to commit any remaining staged files into destination,
       * however, with the changes to checkpointing this will no longer be necessary since despite partial
       * successes, we'll be committing the target table (aka airbyte_raw) table throughout the sync
       */

      LOGGER.info("Cleaning up destination started for {} streams", writeConfigs.size());
      for (final BigQueryWriteConfig writeConfig : writeConfigs.values()) {
        bigQueryGcsOperations.dropStageIfExists(writeConfig.datasetId(), writeConfig.streamName());
      }
      LOGGER.info("Cleaning up destination completed.");
    };
  }

}
