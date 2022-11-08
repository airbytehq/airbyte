/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.staging;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import java.util.List;
import java.util.UUID;
import org.joda.time.DateTime;

public interface StagingOperations extends SqlOperations {

  String getStageName(String namespace, String streamName);

  String getStagingPath(UUID connectionId, String namespace, String streamName, DateTime writeDatetime);

  /**
   * Create a staging folder where to upload temporary files before loading into the final destination
   */
  void createStageIfNotExists(JdbcDatabase database, String stageName) throws Exception;

  /**
   * Upload the data file into the stage area.
   *
   * @return the name of the file that was uploaded.
   */
  String uploadRecordsToStage(JdbcDatabase database, SerializableBuffer recordsData, String schemaName, String stageName, String stagingPath)
      throws Exception;

  /**
   * Load the data stored in the stage area into a temporary table in the destination
   */
  void copyIntoTmpTableFromStage(JdbcDatabase database,
                                 String stageName,
                                 String stagingPath,
                                 List<String> stagedFiles,
                                 String srcTableName,
                                 String schemaName)
      throws Exception;

  /**
   * Remove files that were just staged
   */
  void cleanUpStage(JdbcDatabase database, String stageName, List<String> stagedFiles) throws Exception;

  /**
   * Delete the stage area and all staged files that was in it
   */
  void dropStageIfExists(JdbcDatabase database, String stageName) throws Exception;

}
