/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE;

import com.google.cloud.bigquery.TableId;
import com.google.common.base.Functions;
import com.google.common.base.Preconditions;
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.cdk.integrations.destination.async.AsyncStreamConsumer;
import io.airbyte.cdk.integrations.destination.async.buffers.BufferManager;
import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction;
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnCloseFunction;
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnStartFunction;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Consumer;
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
                                                      final ConfiguredAirbyteCatalog catalog,
                                                      final Consumer<AirbyteMessage> outputRecordCollector,
                                                      final BigQueryGcsOperations bigQueryGcsOperations,
                                                      final TyperDeduper typerDeduper,
                                                      final ParsedCatalog parsedCatalog,
                                                      final String defaultNamespace) {
    final Map<StreamDescriptor, StreamConfig> streamConfigMap = createWriteConfigs(
        catalog,
        parsedCatalog);

    final DestinationFlushFunction flusher = new BigQueryAsyncFlush(streamConfigMap, bigQueryGcsOperations, catalog);
    return new AsyncStreamConsumer(
        outputRecordCollector,
        onStartFunction(bigQueryGcsOperations, parsedCatalog.getStreams(), typerDeduper),
        onCloseFunction(bigQueryGcsOperations, parsedCatalog.getStreams(), typerDeduper),
        flusher,
        catalog,
        new BufferManager(getBigQueryBufferMemoryLimit()),
        Optional.ofNullable(defaultNamespace));
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

  private Map<StreamDescriptor, StreamConfig> createWriteConfigs(final ConfiguredAirbyteCatalog catalog,
                                                                 final ParsedCatalog parsedCatalog) {
    return catalog.getStreams().stream()
        .map(configuredStream -> {
          Preconditions.checkNotNull(configuredStream.getDestinationSyncMode(), "Undefined destination sync mode");

          final AirbyteStream stream = configuredStream.getStream();
          return parsedCatalog.getStream(stream.getNamespace(), stream.getName());
        })
        .collect(Collectors.toMap(
            c -> new StreamDescriptor().withName(c.getId().getOriginalName()).withNamespace(c.getId().getOriginalNamespace()),
            Functions.identity()));
  }

  /**
   * @param bigQueryGcsOperations collection of Google Cloud Storage Operations
   * @param streamConfigs configuration settings used to describe how to write data and where it
   *        exists
   */
  private OnStartFunction onStartFunction(final BigQueryGcsOperations bigQueryGcsOperations,
                                          final List<StreamConfig> streamConfigs,
                                          final TyperDeduper typerDeduper) {
    return () -> {
      LOGGER.info("Preparing airbyte_raw tables in destination started for {} streams", streamConfigs.size());
      typerDeduper.prepareSchemasAndRunMigrations();

      for (final StreamConfig streamConfig : streamConfigs) {
        final var tableId = TableId.of(streamConfig.getId().getRawNamespace(), streamConfig.getId().getRawName());
        LOGGER.info("Preparing staging are in destination for schema: {}, stream: {}, target table: {}, stage: {}",
            BigQueryRecordFormatter.SCHEMA_V2, streamConfig.getId().getOriginalName(),
            tableId, streamConfig.getId().getOriginalName());
        // In Destinations V2, we will always use the 'airbyte_internal' schema/originalNamespace for raw
        // tables
        final String rawDatasetId = DEFAULT_AIRBYTE_INTERNAL_NAMESPACE;
        // Regardless, ensure the schema the customer wants to write to exists
        bigQueryGcsOperations.createSchemaIfNotExists(streamConfig.getId().getRawNamespace());
        // Schema used for raw and airbyte internal tables
        bigQueryGcsOperations.createSchemaIfNotExists(rawDatasetId);
        // Customer's destination schema
        // With checkpointing, we will be creating the target table earlier in the setup such that
        // the data can be immediately loaded from the staging area
        bigQueryGcsOperations.createTableIfNotExists(tableId, BigQueryRecordFormatter.SCHEMA_V2);
        bigQueryGcsOperations.createStageIfNotExists(rawDatasetId, streamConfig.getId().getOriginalName());
        // When OVERWRITE mode, truncate the destination's raw table prior to syncing data
        if (streamConfig.getDestinationSyncMode() == DestinationSyncMode.OVERWRITE) {
          // TODO: this might need special handling during the migration
          bigQueryGcsOperations.truncateTableIfExists(rawDatasetId, tableId, BigQueryRecordFormatter.SCHEMA_V2);
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
   * @param streamConfigs configuration settings used to describe how to write data and where it
   *        exists
   */
  private OnCloseFunction onCloseFunction(final BigQueryGcsOperations bigQueryGcsOperations,
                                          final List<StreamConfig> streamConfigs,
                                          final TyperDeduper typerDeduper) {
    return (hasFailed, streamSyncSummaries) -> {
      /*
       * Previously the hasFailed value was used to commit any remaining staged files into destination,
       * however, with the changes to checkpointing this will no longer be necessary since despite partial
       * successes, we'll be committing the target table (aka airbyte_raw) table throughout the sync
       */
      typerDeduper.typeAndDedupe(streamSyncSummaries);
      LOGGER.info("Cleaning up destination started for {} streams", streamConfigs.size());
      for (final StreamConfig streamConfig : streamConfigs) {
        bigQueryGcsOperations.dropStageIfExists(streamConfig.getId().getRawNamespace(), streamConfig.getId().getOriginalName());
      }
      typerDeduper.commitFinalTables();
      typerDeduper.cleanup();
      LOGGER.info("Cleaning up destination completed.");
    };
  }

}
