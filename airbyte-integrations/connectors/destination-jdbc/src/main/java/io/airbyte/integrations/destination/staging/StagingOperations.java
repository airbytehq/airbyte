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

/**
 * Staging operations focuses on the SQL queries that are needed to success move data into a staging environment like GCS or S3. In general, the
 * reference of staging is the usage of an object storage for the purposes of efficiently uploading bulk data to destinations
 */
public interface StagingOperations extends SqlOperations {

  /**
   * Returns the staging environment's name
   *
   * @param namespace Name of schema
   * @param streamName Name of the stream
   * @return Fully qualified name of the staging environment
   */
  String getStageName(String namespace, String streamName);

  String getStagingPath(UUID connectionId, String namespace, String streamName, DateTime writeDatetime);

  /**
   * Create a staging folder where to upload temporary files before loading into the final destination
   */
  void createStageIfNotExists(JdbcDatabase database, String stageName) throws Exception;

  /**
   * Upload the data file into the stage area.
   *
   * @param database database used for syncing
   * @param recordsData records stored in in-memory buffer
   * @param schemaName name of schema
   * @param stageName name of the staging area folder
   * @param stagingPath path of staging folder to data files
   * @return the name of the file that was uploaded.
   */
  String uploadRecordsToStage(JdbcDatabase database, SerializableBuffer recordsData, String schemaName, String stageName, String stagingPath)
      throws Exception;

  /**
   * Load the data stored in the stage area into a temporary table in the destination
   *
   * @param database database interface
   * @param stageName name of staging area folder
   * @param stagingPath path to staging files
   * @param stagedFiles collection of staged files
   * @param tableName name of table to write staging files to
   * @param schemaName name of schema
   */
  void copyIntoTableFromStage(JdbcDatabase database,
                                 String stageName,
                                 String stagingPath,
                                 List<String> stagedFiles,
                                 String tableName,
                                 String schemaName)
      throws Exception;

  /**
   * Remove files that were just staged
   *
   * @param database database used for syncing
   * @param stageName name of staging area folder
   * @param stagedFiles collection of the staging files to remove
   */
  void cleanUpStage(JdbcDatabase database, String stageName, List<String> stagedFiles) throws Exception;

  /**
   * Delete the stage area and all staged files that was in it
   *
   * @param database database used for syncing
   * @param stageName Name of the staging area used to store files
   */
  void dropStageIfExists(JdbcDatabase database, String stageName) throws Exception;

}
