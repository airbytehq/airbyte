/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Functions;
import com.google.common.base.Preconditions;
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer;
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnCloseFunction;
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnStartFunction;
import io.airbyte.cdk.integrations.destination_async.AsyncStreamConsumer;
import io.airbyte.cdk.integrations.destination_async.buffers.BufferManager;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.Map;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class mimics the same functionality as
 * {@link io.airbyte.cdk.integrations.destination.staging.StagingConsumerFactory} which likely
 * should be placed into a commons package to be utilized across all ConsumerFactories
 */
public class BigQueryStagingConsumerFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryStagingConsumerFactory.class);

  public SerializedAirbyteMessageConsumer createAsync(
                                                      final JsonNode config,
                                                      final ConfiguredAirbyteCatalog catalog,
                                                      final Consumer<AirbyteMessage> outputRecordCollector,
                                                      final BigQueryStagingOperations bigQueryGcsOperations,
                                                      final Function<JsonNode, BigQueryRecordFormatter> recordFormatterCreator,
                                                      final Function<String, String> tmpTableNameTransformer,
                                                      final TyperDeduper typerDeduper,
                                                      final ParsedCatalog parsedCatalog,
                                                      final String defaultNamespace) {
    final Map<StreamDescriptor, BigQueryWriteConfig> writeConfigsByDescriptor = createWriteConfigs(
        config,
        catalog,
        parsedCatalog,
        recordFormatterCreator,
        tmpTableNameTransformer);

    final var flusher = new BigQueryAsyncFlush(writeConfigsByDescriptor, bigQueryGcsOperations, catalog);
    return new AsyncStreamConsumer(
        outputRecordCollector,
        onStartFunction(bigQueryGcsOperations, writeConfigsByDescriptor, typerDeduper),
        (hasFailed, recordCounts) -> {
          try {
            onCloseFunction(bigQueryGcsOperations, writeConfigsByDescriptor, typerDeduper).accept(hasFailed, recordCounts);
          } catch (final Exception e) {
            throw new RuntimeException(e);
          }
        },
        flusher,
        catalog,
        new BufferManager(getBigQueryBufferMemoryLimit()),
        defaultNamespace);
  }

  /**
   * Out BigQuery's uploader threads use a fair amount of memory. We believe this is largely due to
   * the sdk client we use.
   *
   * @return number of bytes to make available for message buffering.
   */
  private long getBigQueryBufferMemoryLimit() {
    return (long) (Runtime.getRuntime().maxMemory() * 0.4);
  }

  private Map<StreamDescriptor, BigQueryWriteConfig> createWriteConfigs(final JsonNode config,
                                                                        final ConfiguredAirbyteCatalog catalog,
                                                                        final ParsedCatalog parsedCatalog,
                                                                        final Function<JsonNode, BigQueryRecordFormatter> recordFormatterCreator,
                                                                        final Function<String, String> tmpTableNameTransformer) {
    return catalog.getStreams().stream()
        .map(configuredStream -> {
          Preconditions.checkNotNull(configuredStream.getDestinationSyncMode(), "Undefined destination sync mode");

          final AirbyteStream stream = configuredStream.getStream();
          final StreamConfig streamConfig = parsedCatalog.getStream(stream.getNamespace(), stream.getName());
          final String streamName = stream.getName();
          final BigQueryRecordFormatter recordFormatter = recordFormatterCreator.apply(stream.getJsonSchema());

          final var internalTableNamespace = streamConfig.id().rawNamespace();
          final var targetTableName = streamConfig.id().rawName();

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
            c -> new StreamDescriptor().withName(c.streamName()).withNamespace(c.namespace()),
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
                                          final Map<StreamDescriptor, BigQueryWriteConfig> writeConfigs,
                                          final TyperDeduper typerDeduper) {
    return () -> {
      LOGGER.info("Preparing airbyte_raw tables in destination started for {} streams", writeConfigs.size());
      typerDeduper.prepareSchemasAndRunMigrations();

      for (final BigQueryWriteConfig writeConfig : writeConfigs.values()) {
        LOGGER.info("Preparing staging are in destination for schema: {}, stream: {}, target table: {}, stage: {}",
            writeConfig.tableSchema(), writeConfig.streamName(), writeConfig.targetTableId(), writeConfig.streamName());
        // In Destinations V2, we will always use the 'airbyte' schema/namespace for raw tables
        final String rawDatasetId = DEFAULT_AIRBYTE_INTERNAL_NAMESPACE;
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
   * Tear down process, will attempt to clean out any staging area
   *
   * @param bigQueryGcsOperations collection of staging operations
   * @param writeConfigs configuration settings used to describe how to write data and where it exists
   */
  private OnCloseFunction onCloseFunction(final BigQueryStagingOperations bigQueryGcsOperations,
                                          final Map<StreamDescriptor, BigQueryWriteConfig> writeConfigs,
                                          final TyperDeduper typerDeduper) {
    return (hasFailed, streamSyncSummaries) -> {
      /*
       * Previously the hasFailed value was used to commit any remaining staged files into destination,
       * however, with the changes to checkpointing this will no longer be necessary since despite partial
       * successes, we'll be committing the target table (aka airbyte_raw) table throughout the sync
       */
      typerDeduper.typeAndDedupe(streamSyncSummaries);
      LOGGER.info("Cleaning up destination started for {} streams", writeConfigs.size());
      for (final Map.Entry<StreamDescriptor, BigQueryWriteConfig> entry : writeConfigs.entrySet()) {
        bigQueryGcsOperations.dropStageIfExists(entry.getValue().datasetId(), entry.getValue().streamName());
      }
      typerDeduper.commitFinalTables();
      typerDeduper.cleanup();
      LOGGER.info("Cleaning up destination completed.");
    };
  }

}
