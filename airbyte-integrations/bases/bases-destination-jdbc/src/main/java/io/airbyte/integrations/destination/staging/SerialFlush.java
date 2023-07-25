/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.staging;

import static java.util.stream.Collectors.joining;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.destination.typing_deduping.TypeAndDedupeOperationValve;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;
import io.airbyte.integrations.destination.jdbc.WriteConfig;
import io.airbyte.integrations.destination.record_buffer.FlushBufferFunction;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;

/**
 * Serial flushing logic. Though simpler, this causes unnecessary backpressure and slows down the
 * entire pipeline.
 * <p>
 * Note: This class should be re-written so that is implements the {@link FlushBufferFunction}
 * interface, instead of return an anonymous function implementing this interface for clarity. As of
 * this writing, we avoid doing so to simplify the migration to async flushing.
 */
@Slf4j
public class SerialFlush {

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
  public static FlushBufferFunction function(
                                             final JdbcDatabase database,
                                             final StagingOperations stagingOperations,
                                             final List<WriteConfig> writeConfigs,
                                             final ConfiguredAirbyteCatalog catalog,
                                             TypeAndDedupeOperationValve typerDeduperValve,
                                             TyperDeduper typerDeduper) {
    // TODO: (ryankfu) move this block of code that executes before the lambda to #onStartFunction
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
          conflictingStreams.stream().map(config -> config.getNamespace() + "." + config.getStreamName()).collect(joining(", ")));
      throw new ConfigErrorException(message);
    }
    return (pair, writer) -> {
      log.info("Flushing buffer for stream {} ({}) to staging", pair.getName(), FileUtils.byteCountToDisplaySize(writer.getByteCount()));
      if (!pairToWriteConfig.containsKey(pair)) {
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s", Jsons.serialize(catalog)));
      }

      final WriteConfig writeConfig = pairToWriteConfig.get(pair);
      final String schemaName = writeConfig.getOutputSchemaName();
      final String stageName = stagingOperations.getStageName(schemaName, writeConfig.getStreamName());
      final String stagingPath =
          stagingOperations.getStagingPath(StagingConsumerFactory.RANDOM_CONNECTION_ID, schemaName, writeConfig.getStreamName(),
              writeConfig.getWriteDatetime());
      try (writer) {
        writer.flush();
        final String stagedFile = stagingOperations.uploadRecordsToStage(database, writer, schemaName, stageName, stagingPath);
        GeneralStagingFunctions.copyIntoTableFromStage(database, stageName, stagingPath, List.of(stagedFile), writeConfig.getOutputTableName(),
            schemaName,
            stagingOperations,
            writeConfig.getNamespace(),
            writeConfig.getStreamName(),
            typerDeduperValve,
            typerDeduper);
      } catch (final Exception e) {
        log.error("Failed to flush and commit buffer data into destination's raw table", e);
        throw new RuntimeException("Failed to upload buffer to stage and commit to destination", e);
      }
    };
  }

  private static AirbyteStreamNameNamespacePair toNameNamespacePair(final WriteConfig config) {
    return new AirbyteStreamNameNamespacePair(config.getStreamName(), config.getNamespace());
  }

}
