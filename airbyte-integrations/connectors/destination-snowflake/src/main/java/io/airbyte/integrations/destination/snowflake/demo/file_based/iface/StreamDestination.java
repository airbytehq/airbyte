package io.airbyte.integrations.destination.snowflake.demo.file_based.iface;

import java.io.File;

public interface StreamDestination extends AutoCloseable {

  /**
   * Do any setup prior to writing data. For example, setting up destination tables, etc.
   */
  void setup() throws Exception;

  /**
   * Commit the data in this file to the destination. This method may consume additional
   * memory proportional to the size of the incoming file and all uncommitted files,
   * and/or the number of uncommitted files.
   * <p>
   * This method <b>MUST</b> be thread-safe.
   */
  void upload(String file, int numRecords, int numBytes) throws Exception;
}
