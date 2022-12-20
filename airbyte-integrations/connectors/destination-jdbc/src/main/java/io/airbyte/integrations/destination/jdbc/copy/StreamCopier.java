/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy;

import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.util.UUID;

/**
 * StreamCopier is responsible for writing to a staging persistence and providing methods to remove
 * the staged data.
 */
public interface StreamCopier {

  /**
   * Writes a value to a staging file for the stream.
   */
  void write(UUID id, AirbyteRecordMessage recordMessage, String fileName) throws Exception;

  /**
   * Closes the writer for the stream to the current staging file. The staging file must be of a
   * certain size specified in GlobalDataSizeConstants + one more buffer. The writer for the stream
   * will close with a note that no errors were found.
   */
  void closeNonCurrentStagingFileWriters() throws Exception;

  /**
   * Closes the writer for the stream to the staging persistence. This method should block until all
   * buffered data has been written to the persistence.
   */
  void closeStagingUploader(boolean hasFailed) throws Exception;

  /**
   * Creates a temporary table in the target database.
   */
  void createTemporaryTable() throws Exception;

  /**
   * Copies the staging file to the temporary table. This method should block until the copy/upload
   * has completed.
   */
  void copyStagingFileToTemporaryTable() throws Exception;

  /**
   * Creates the destination schema if it does not already exist.
   */
  void createDestinationSchema() throws Exception;

  /**
   * Creates the destination table if it does not already exist.
   *
   * @return the name of the destination table
   */
  String createDestinationTable() throws Exception;

  /**
   * Generates a merge SQL statement from the temporary table to the final table.
   */
  String generateMergeStatement(String destTableName) throws Exception;

  /**
   * Cleans up the copier by removing the staging file and dropping the temporary table after
   * completion or failure.
   */
  void removeFileAndDropTmpTable() throws Exception;

  /**
   * Creates the staging file and all the necessary items to write data to this file.
   *
   * @return A string that unqiuely identifies the file. E.g. the filename, or a unique suffix that is
   *         appended to a shared filename prefix
   */
  String prepareStagingFile();

  /**
   * @return current staging file name
   */
  String getCurrentFile();

}
