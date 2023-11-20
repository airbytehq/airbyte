/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import io.airbyte.cdk.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.cdk.integrations.destination.s3.csv.CsvSerializedBuffer;
import io.airbyte.cdk.integrations.destination.s3.csv.StagingDatabaseCsvSheetGenerator;
import io.airbyte.cdk.integrations.destination_async.DestinationFlushFunction;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.Map;
import java.util.stream.Stream;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;

/**
 * Async flushing logic. Flushing async prevents backpressure and is the superior flushing strategy.
 */
@Slf4j
class BigQueryAsyncFlush implements DestinationFlushFunction {

  private final Map<StreamDescriptor, BigQueryWriteConfig> streamDescToWriteConfig;
  private final BigQueryStagingOperations stagingOperations;
  private final ConfiguredAirbyteCatalog catalog;

  public BigQueryAsyncFlush(
                            final Map<StreamDescriptor, BigQueryWriteConfig> streamDescToWriteConfig,
                            final BigQueryStagingOperations stagingOperations,
                            final ConfiguredAirbyteCatalog catalog) {
    this.streamDescToWriteConfig = streamDescToWriteConfig;
    this.stagingOperations = stagingOperations;
    this.catalog = catalog;
  }

  @Override
  public void flush(final StreamDescriptor decs, final Stream<PartialAirbyteMessage> stream) throws Exception {
    final SerializableBuffer writer;
    try {
      writer = new CsvSerializedBuffer(
          new FileBuffer(CsvSerializedBuffer.CSV_GZ_SUFFIX),
          new StagingDatabaseCsvSheetGenerator(true),
          true);

      stream.forEach(record -> {
        try {
          writer.accept(record.getSerialized(), record.getRecord().getEmittedAt());
        } catch (final Exception e) {
          throw new RuntimeException(e);
        }
      });
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }

    writer.flush();
    log.info("Flushing CSV buffer for stream {} ({}) to staging", decs.getName(), FileUtils.byteCountToDisplaySize(writer.getByteCount()));
    if (!streamDescToWriteConfig.containsKey(decs)) {
      throw new IllegalArgumentException(
          String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s", Jsons.serialize(catalog)));
    }

    final BigQueryWriteConfig writeConfig = streamDescToWriteConfig.get(decs);
    try {
      final String stagedFileName = stagingOperations.uploadRecordsToStage(writeConfig.datasetId(), writeConfig.streamName(), writer);

      stagingOperations.copyIntoTableFromStage(
          writeConfig.datasetId(),
          writeConfig.streamName(),
          writeConfig.targetTableId(),
          writeConfig.tableSchema(),
          stagedFileName);
    } catch (final Exception e) {
      log.error("Failed to flush and commit buffer data into destination's raw table", e);
      throw new RuntimeException("Failed to upload buffer to stage and commit to destination", e);
    }

    writer.close();
  }

  @Override
  public long getOptimalBatchSizeBytes() {
    // Chosen arbitrarily (mostly to match legacy behavior). We have no reason to believe a larger
    // number would be worse.
    // This was previously set to 25MB, which ran into rate-limiting issues:
    // https://cloud.google.com/bigquery/quotas#standard_tables
    // > Your project can make up to 1,500 table modifications per table per day
    return 200 * 1024 * 1024;
  }

  @Override
  public long getQueueFlushThresholdBytes() {
    return 200 * 1024 * 1024;
  }

}
