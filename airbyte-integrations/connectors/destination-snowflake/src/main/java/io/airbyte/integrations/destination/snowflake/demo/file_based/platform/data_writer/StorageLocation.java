package io.airbyte.integrations.destination.snowflake.demo.file_based.platform.data_writer;

public interface StorageLocation {

  /**
   * Delete the data from this location. For example, if the underlying storage is a file, delete the
   * file.
   */
  default void delete() throws Exception {

  }

}
