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
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.Map;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

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

  private VoidCallable onStartFunction(final BigQueryStagingOperations bigQueryGcsOperations,
                                       final Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs) {
    return () -> {
      LOGGER.info("Preparing tmp tables in destination started for {} streams", writeConfigs.size());
      for (final BigQueryWriteConfig writeConfig : writeConfigs.values()) {
        final String datasetId = writeConfig.datasetId();
        bigQueryGcsOperations.createSchemaIfNotExists(datasetId, writeConfig.datasetLocation());
        // only the tmp table is explicitly created, because the target table will be automatically
        // created when the data is copied from the tmp table
        bigQueryGcsOperations.createTmpTableIfNotExists(writeConfig.tmpTableId(), writeConfig.tableSchema());
        bigQueryGcsOperations.createStageIfNotExists(datasetId, writeConfig.streamName());
      }
      LOGGER.info("Preparing tmp tables in destination completed.");
    };
  }

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
      try (writer) {
        writer.flush();
        final String stagedFile = bigQueryGcsOperations.uploadRecordsToStage(writeConfig.datasetId(), writeConfig.streamName(), writer);
        writeConfig.addStagedFile(stagedFile);
      } catch (final Exception e) {
        LOGGER.error("Failed to flush and upload buffer to stage:", e);
        throw new RuntimeException("Failed to upload buffer to stage", e);
      }
    };
  }

  private CheckedConsumer<Boolean, Exception> onCloseFunction(final BigQueryStagingOperations bigQueryGcsOperations,
                                                              final Map<AirbyteStreamNameNamespacePair, BigQueryWriteConfig> writeConfigs) {
    return (hasFailed) -> {
      if (!hasFailed) {
        LOGGER.info("Copying into tables in destination started for {} streams", writeConfigs.size());

        for (final BigQueryWriteConfig writeConfig : writeConfigs.values()) {
          final String datasetId = writeConfig.datasetId();
          final String stream = writeConfig.streamName();

          try {
            bigQueryGcsOperations.copyIntoTmpTableFromStage(datasetId, stream, writeConfig.tmpTableId(), writeConfig.tableSchema(),
                writeConfig.stagedFiles());
          } catch (final Exception e) {
            bigQueryGcsOperations.cleanUpStage(datasetId, stream, writeConfig.stagedFiles());
            final String stagingPath = bigQueryGcsOperations.getStagingFullPath(datasetId, stream);
            throw new RuntimeException("Failed to upload data from stage " + stagingPath, e);
          }
          writeConfig.clearStagedFiles();
          bigQueryGcsOperations.copyIntoTargetTable(
              datasetId, writeConfig.tmpTableId(), writeConfig.targetTableId(), writeConfig.tableSchema(), writeConfig.syncMode());
        }

        LOGGER.info("Finalizing tables in destination completed");
      }

      LOGGER.info("Cleaning up destination started for {} streams", writeConfigs.size());
      for (final BigQueryWriteConfig writeConfig : writeConfigs.values()) {
        bigQueryGcsOperations.dropTableIfExists(writeConfig.datasetId(), writeConfig.tmpTableId());
        bigQueryGcsOperations.dropStageIfExists(writeConfig.datasetId(), writeConfig.streamName());
      }
      LOGGER.info("Cleaning up destination completed.");
    };
  }

}
