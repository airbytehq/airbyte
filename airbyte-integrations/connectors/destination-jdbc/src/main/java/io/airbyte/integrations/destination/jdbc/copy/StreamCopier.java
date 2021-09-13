/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.jdbc.copy;

import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.util.UUID;

/**
 * StreamCopier is responsible for writing to a staging persistence and providing methods to remove
 * the staged data.
 */
public interface StreamCopier {

  /**
   * Writes a value to a staging file for the stream.
   */
  void write(UUID id, AirbyteRecordMessage recordMessage) throws Exception;

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

}
