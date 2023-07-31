/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.staging;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.destination.typing_deduping.TypeAndDedupeOperationValve;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnCloseFunction;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnStartFunction;
import io.airbyte.integrations.destination.jdbc.WriteConfig;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.util.ArrayList;
import java.util.List;
import lombok.extern.slf4j.Slf4j;

/**
 * Functions and logic common to all flushing strategies.
 */
@Slf4j
public class GeneralStagingFunctions {

  public static OnStartFunction onStartFunction(final JdbcDatabase database,
                                                final StagingOperations stagingOperations,
                                                final List<WriteConfig> writeConfigs,
                                                final TyperDeduper typerDeduper) {
    return () -> {
      log.info("Preparing raw tables in destination started for {} streams", writeConfigs.size());
      final List<String> queryList = new ArrayList<>();
      for (final WriteConfig writeConfig : writeConfigs) {
        final String schema = writeConfig.getOutputSchemaName();
        final String stream = writeConfig.getStreamName();
        final String dstTableName = writeConfig.getOutputTableName();
        final String stageName = stagingOperations.getStageName(schema, stream);
        final String stagingPath =
            stagingOperations.getStagingPath(StagingConsumerFactory.RANDOM_CONNECTION_ID, schema, stream, writeConfig.getWriteDatetime());

        log.info("Preparing staging area in destination started for schema {} stream {}: target table: {}, stage: {}",
            schema, stream, dstTableName, stagingPath);

        stagingOperations.createSchemaIfNotExists(database, schema);
        stagingOperations.createTableIfNotExists(database, schema, dstTableName);
        stagingOperations.createStageIfNotExists(database, stageName);

        /*
         * When we're in OVERWRITE, clear out the table at the start of a sync, this is an expected side
         * effect of checkpoint and the removal of temporary tables
         */
        switch (writeConfig.getSyncMode()) {
          case OVERWRITE -> queryList.add(stagingOperations.truncateTableQuery(database, schema, dstTableName));
          case APPEND, APPEND_DEDUP -> {}
          default -> throw new IllegalStateException("Unrecognized sync mode: " + writeConfig.getSyncMode());
        }

        log.info("Preparing staging area in destination completed for schema {} stream {}", schema, stream);
      }
      log.info("Executing finalization of tables.");
      stagingOperations.executeTransaction(database, queryList);

      typerDeduper.prepareFinalTables();
    };
  }

  /**
   * Handles copying data from staging area to destination table and clean up of staged files if
   * upload was unsuccessful
   */
  public static void copyIntoTableFromStage(final JdbcDatabase database,
                                            final String stageName,
                                            final String stagingPath,
                                            final List<String> stagedFiles,
                                            final String tableName,
                                            final String schemaName,
                                            final StagingOperations stagingOperations,
                                            final String streamNamespace,
                                            final String streamName,
                                            final TypeAndDedupeOperationValve typerDeduperValve,
                                            final TyperDeduper typerDeduper)
      throws Exception {
    try {
      stagingOperations.copyIntoTableFromStage(database, stageName, stagingPath, stagedFiles,
          tableName, schemaName);

      AirbyteStreamNameNamespacePair streamId = new AirbyteStreamNameNamespacePair(streamNamespace, streamName);
      if (!typerDeduperValve.containsKey(streamId)) {
        typerDeduperValve.addStream(streamId);
      } else if (typerDeduperValve.readyToTypeAndDedupe(streamId)) {
        typerDeduper.typeAndDedupe(streamId.getNamespace(), streamId.getName());
        typerDeduperValve.updateTimeAndIncreaseInterval(streamId);
      }
    } catch (final Exception e) {
      stagingOperations.cleanUpStage(database, stageName, stagedFiles);
      log.info("Cleaning stage path {}", stagingPath);
      throw new RuntimeException("Failed to upload data from stage " + stagingPath, e);
    }
  }

  /**
   * Tear down process, will attempt to try to clean out any staging area
   *
   * @param database database used for syncing
   * @param stagingOperations collection of SQL queries necessary for writing data into a staging area
   * @param writeConfigs configuration settings for all destination connectors needed to write
   * @param purgeStagingData drop staging area if true, keep otherwise
   * @return
   */
  public static OnCloseFunction onCloseFunction(final JdbcDatabase database,
                                                final StagingOperations stagingOperations,
                                                final List<WriteConfig> writeConfigs,
                                                final boolean purgeStagingData,
                                                final TyperDeduper typerDeduper) {
    return (hasFailed) -> {
      // After moving data from staging area to the target table (airybte_raw) clean up the staging
      // area (if user configured)
      log.info("Cleaning up destination started for {} streams", writeConfigs.size());
      for (final WriteConfig writeConfig : writeConfigs) {
        final String schemaName = writeConfig.getOutputSchemaName();
        if (purgeStagingData) {
          final String stageName = stagingOperations.getStageName(schemaName, writeConfig.getStreamName());
          log.info("Cleaning stage in destination started for stream {}. schema {}, stage: {}", writeConfig.getStreamName(), schemaName,
              stageName);
          stagingOperations.dropStageIfExists(database, stageName);
        }

        typerDeduper.typeAndDedupe(writeConfig.getNamespace(), writeConfig.getStreamName());
      }

      typerDeduper.commitFinalTables();
      log.info("Cleaning up destination completed.");
    };
  }

}
