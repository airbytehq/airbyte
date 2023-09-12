package io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer;

import java.io.IOException;
import org.apache.commons.io.function.IOConsumer;

/**
 * Writes airbyte records to some underlying storage.\
 */
public interface DataWriter<T extends StorageLocation> {

  T getCurrentLocation();

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
