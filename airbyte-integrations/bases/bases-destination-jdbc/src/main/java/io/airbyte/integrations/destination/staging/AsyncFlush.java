/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.staging;

import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.jdbc.WriteConfig;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.s3.csv.CsvSerializedBuffer;
import io.airbyte.integrations.destination.s3.csv.StagingDatabaseCsvSheetGenerator;
import io.airbyte.integrations.destination_async.DestinationFlushFunction;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;

/**
 * Async flushing logic. Flushing async prevents backpressure and is the superior flushing strategy.
 */
@Slf4j
class AsyncFlush implements DestinationFlushFunction {

  private final Map<StreamDescriptor, WriteConfig> streamDescToWriteConfig;
  private final StagingOperations stagingOperations;
  private final JdbcDatabase database;
  private final ConfiguredAirbyteCatalog catalog;

  public AsyncFlush(final Map<StreamDescriptor, WriteConfig> streamDescToWriteConfig,
                    final StagingOperations stagingOperations,
                    final JdbcDatabase database,
                    final ConfiguredAirbyteCatalog catalog) {
    this.streamDescToWriteConfig = streamDescToWriteConfig;
    this.stagingOperations = stagingOperations;
    this.database = database;
    this.catalog = catalog;
  }

  @Override
  public void flush(final StreamDescriptor decs, final Stream<PartialAirbyteMessage> stream) throws Exception {
    final CsvSerializedBuffer writer;
    try {
      writer = new CsvSerializedBuffer(
          new FileBuffer(CsvSerializedBuffer.CSV_GZ_SUFFIX),
          new StagingDatabaseCsvSheetGenerator(),
          true);

      // reassign as lambdas require references to be final.
      stream.forEach(record -> {
        try {
          // todo (cgardens) - most writers just go ahead and re-serialize the contents of the record message.
          // we should either just pass the raw string or at least have a way to do that and create a default
          // impl that maintains backwards compatible behavior.
          writer.accept(Jsons.deserialize(record.getSerialized(), AirbyteMessage.class).getRecord());
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

    final WriteConfig writeConfig = streamDescToWriteConfig.get(decs);
    final String schemaName = writeConfig.getOutputSchemaName();
    final String stageName = stagingOperations.getStageName(schemaName, writeConfig.getStreamName());
    final String stagingPath =
        stagingOperations.getStagingPath(StagingConsumerFactory.RANDOM_CONNECTION_ID, schemaName, writeConfig.getStreamName(),
            writeConfig.getWriteDatetime());
    try {
      final String stagedFile = stagingOperations.uploadRecordsToStage(database, writer, schemaName, stageName, stagingPath);
      GeneralStagingFunctions.copyIntoTableFromStage(database, stageName, stagingPath, List.of(stagedFile), writeConfig.getOutputTableName(),
          schemaName,
          stagingOperations);
    } catch (final Exception e) {
      log.error("Failed to flush and commit buffer data into destination's raw table", e);
      throw new RuntimeException("Failed to upload buffer to stage and commit to destination", e);
    }

    writer.close();
  }

  @Override
  public long getOptimalBatchSizeBytes() {
    // todo(davin): this should be per-destination specific. currently this is for Snowflake.
    return 200 * 1024 * 1024;
  }

}
