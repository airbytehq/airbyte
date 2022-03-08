/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc;

import io.airbyte.db.jdbc.JdbcDatabase;
import java.io.File;

public interface StagingOperations extends SqlOperations {

  /**
   * Create a staging folder where to upload temporary files before loading into the final destination
   */
  void createStageIfNotExists(JdbcDatabase database, String stage) throws Exception;

  /**
   * Upload the data file into the stage area.*
   */
  void uploadRecordsToStage(JdbcDatabase database, File dataFile, String schemaName, String path) throws Exception;

  /**
   * Load the data stored in the stage area into a temporary table in the destination
   */
  void copyIntoTmpTableFromStage(JdbcDatabase database, String path, String srcTableName, String schemaName) throws Exception;

  /**
   * Remove files that were just staged
   */
  void cleanUpStage(JdbcDatabase database, String path) throws Exception;

  /**
   * Delete the stage area and all staged files that was in it
   */
  void dropStageIfExists(JdbcDatabase database, String stageName) throws Exception;

}
