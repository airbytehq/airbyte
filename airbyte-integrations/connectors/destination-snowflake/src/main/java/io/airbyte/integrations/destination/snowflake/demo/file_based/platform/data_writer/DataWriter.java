package io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer;

import java.io.IOException;
import org.apache.commons.io.function.IOConsumer;

/**
 * Writes airbyte records to some underlying storage.\
 */
public interface DataWriter {

  /**
   * Naming needs work. Returns a string which uniquely identifies the current output location.
   */
  String getCurrentFilename();

  /**
   * Get a thing that writes rendered records to the underlying storage.
   * <p>
   * Close the previous output stream if it exists, flushing any in-memory buffer to the underlying
   * storage medium.
   */
  void roll() throws IOException;

  /**
   * @return The current output stream
   */
  IOConsumer<byte[]> getCurrentOutputStream();
}
