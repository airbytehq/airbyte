/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.TableId;
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.cdk.integrations.destination.async.AsyncStreamConsumer;
import io.airbyte.cdk.integrations.destination.async.buffers.BufferManager;
import io.airbyte.cdk.integrations.destination.async.state.FlushFailure;
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnCloseFunction;
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnStartFunction;
import io.airbyte.integrations.base.destination.typing_deduping.DefaultTyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.NoOpTyperDeduperWithV1V2Migrations;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDestinationHandler;
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator;
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryV1V2Migrator;
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryV2TableMigrator;
import io.airbyte.integrations.destination.bigquery.uploader.BigQueryDirectUploader;
import io.airbyte.integrations.destination.bigquery.uploader.BigQueryUploaderFactory;
import io.airbyte.integrations.destination.bigquery.uploader.config.UploaderConfig;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.Executors;
import java.util.function.Consumer;
import java.util.function.Supplier;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Slf4j
@SuppressWarnings("try")
public class BigQueryRecordStandardConsumer extends AsyncStreamConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryRecordStandardConsumer.class);

  public BigQueryRecordStandardConsumer(Consumer<AirbyteMessage> outputRecordCollector,
                                        OnStartFunction onStart,
                                        OnCloseFunction onClose,
                                        ConfiguredAirbyteCatalog catalog,
                                        String defaultNamespace,
                                        Supplier<ConcurrentMap<AirbyteStreamNameNamespacePair, BigQueryDirectUploader>> uploaderMap) {
    super(outputRecordCollector,
        onStart,
        onClose,
        new BigQueryAsyncStandardFlush(uploaderMap),
        catalog,
        new BufferManager((long) (Runtime.getRuntime().maxMemory() * 0.5)),
        Optional.ofNullable(defaultNamespace),
        new FlushFailure(),
        Executors.newFixedThreadPool(2));
  }

  public static SerializedAirbyteMessageConsumer createStandardConsumer(final BigQuery bigquery,
                                                                        final JsonNode config,
                                                                        final ConfiguredAirbyteCatalog catalog,
                                                                        final ParsedCatalog parsedCatalog,
                                                                        final Consumer<AirbyteMessage> outputRecordCollector,
                                                                        final BigQuerySqlGenerator sqlGenerator,
                                                                        final BigQueryDestinationHandler destinationHandler,
                                                                        final boolean disableTypeDedupe)
      throws Exception {
    // Code related to initializing standard insert consumer isolated in this class file.
    final TyperDeduper typerDeduper =
        buildTyperDeduper(sqlGenerator, parsedCatalog, destinationHandler, bigquery, disableTypeDedupe);
    return getStandardRecordConsumer(bigquery, config, catalog, parsedCatalog, outputRecordCollector, typerDeduper);

  }

  private static SerializedAirbyteMessageConsumer getStandardRecordConsumer(final BigQuery bigquery,
                                                                            final JsonNode config,
                                                                            final ConfiguredAirbyteCatalog catalog,
                                                                            final ParsedCatalog parsedCatalog,
                                                                            final Consumer<AirbyteMessage> outputRecordCollector,
                                                                            final TyperDeduper typerDeduper)
      throws Exception {
    final Supplier<ConcurrentMap<AirbyteStreamNameNamespacePair, BigQueryDirectUploader>> writeConfigs = getUploaderMap(
        bigquery,
        config,
        catalog,
        parsedCatalog);

    final String bqNamespace = BigQueryUtils.getDatasetId(config);

    return new BigQueryRecordStandardConsumer(
        outputRecordCollector,
        () -> {
          typerDeduper.prepareSchemasAndRunMigrations();

          // Set up our raw tables
          writeConfigs.get().forEach((streamId, uploader) -> {
            final StreamConfig stream = parsedCatalog.getStream(streamId);
            if (stream.getDestinationSyncMode() == DestinationSyncMode.OVERWRITE) {
              // For streams in overwrite mode, truncate the raw table.
              // non-1s1t syncs actually overwrite the raw table at the end of the sync, so we only do this in
              // 1s1t mode.
              final TableId rawTableId = TableId.of(stream.getId().getRawNamespace(), stream.getId().getRawName());
              LOGGER.info("Deleting Raw table {}", rawTableId);
              if (!bigquery.delete(rawTableId)) {
                LOGGER.info("Raw table {} not found, continuing with creation", rawTableId);
              }
              LOGGER.info("Creating table {}", rawTableId);
              BigQueryUtils.createPartitionedTableIfNotExists(bigquery, rawTableId, BigQueryRecordFormatter.SCHEMA_V2);
            } else {
              uploader.createRawTable();
            }
          });

          typerDeduper.prepareFinalTables();
        },
        (hasFailed, streamSyncSummaries) -> {
          try {
            Thread.sleep(30 * 1000);
            typerDeduper.typeAndDedupe(streamSyncSummaries);
            typerDeduper.commitFinalTables();
            typerDeduper.cleanup();
          } catch (final Exception e) {
            throw new RuntimeException(e);
          }
        },
        catalog,
        bqNamespace,
        writeConfigs);
  }

  protected static Supplier<ConcurrentMap<AirbyteStreamNameNamespacePair, BigQueryDirectUploader>> getUploaderMap(
                                                                                                                  final BigQuery bigquery,
                                                                                                                  final JsonNode config,
                                                                                                                  final ConfiguredAirbyteCatalog catalog,
                                                                                                                  final ParsedCatalog parsedCatalog)
      throws IOException {
    return () -> {
      final ConcurrentMap<AirbyteStreamNameNamespacePair, BigQueryDirectUploader> uploaderMap = new ConcurrentHashMap<>();
      for (final ConfiguredAirbyteStream configStream : catalog.getStreams()) {
        final AirbyteStream stream = configStream.getStream();
        final StreamConfig parsedStream;

        final String targetTableName;

        parsedStream = parsedCatalog.getStream(stream.getNamespace(), stream.getName());
        targetTableName = parsedStream.getId().getRawName();

        final UploaderConfig uploaderConfig = UploaderConfig
            .builder()
            .bigQuery(bigquery)
            .parsedStream(parsedStream)
            .bigQueryClientChunkSize(BigQueryUtils.getBigQueryClientChunkSize(config))
            .datasetLocation(BigQueryUtils.getDatasetLocation(config))
            .formatter(new BigQueryRecordFormatter(new BigQuerySQLNameTransformer()))
            .targetTableName(targetTableName)
            .build();

        try {
          putStreamIntoUploaderMap(stream, uploaderConfig, uploaderMap);
        } catch (final IOException e) {
          throw new RuntimeException(e);
        }
      }
      return uploaderMap;
    };
  }

  protected static void putStreamIntoUploaderMap(final AirbyteStream stream,
                                                 final UploaderConfig uploaderConfig,
                                                 final Map<AirbyteStreamNameNamespacePair, BigQueryDirectUploader> uploaderMap)
      throws IOException {
    uploaderMap.put(
        AirbyteStreamNameNamespacePair.fromAirbyteStream(stream),
        BigQueryUploaderFactory.getUploader(uploaderConfig));
  }

  private static TyperDeduper buildTyperDeduper(final BigQuerySqlGenerator sqlGenerator,
                                                final ParsedCatalog parsedCatalog,
                                                final BigQueryDestinationHandler destinationHandler,
                                                final BigQuery bigquery,
                                                final boolean disableTypeDedupe) {
    final BigQueryV1V2Migrator migrator = new BigQueryV1V2Migrator(bigquery, new BigQuerySQLNameTransformer());
    final BigQueryV2TableMigrator v2RawTableMigrator = new BigQueryV2TableMigrator(bigquery);

    if (disableTypeDedupe) {
      return new NoOpTyperDeduperWithV1V2Migrations<>(
          sqlGenerator, destinationHandler, parsedCatalog, migrator, v2RawTableMigrator, List.of());
    }

    return new DefaultTyperDeduper<>(
        sqlGenerator,
        destinationHandler,
        parsedCatalog,
        migrator,
        v2RawTableMigrator,
        List.of());
  }

}
