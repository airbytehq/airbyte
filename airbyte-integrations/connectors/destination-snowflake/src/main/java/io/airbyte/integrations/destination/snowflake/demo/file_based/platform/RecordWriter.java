package io.airbyte.integrations.destination.snowflake.demo.file_based.platform;

import io.airbyte.protocol.models.v0.AirbyteRecordMessage;

/**
 * Writes airbyte records to a local file (i.e. within the connector container).
 * <p>
 * I don't love this interface, it's mostly illustrative. The existing SerializedBuffer stuff is
 * approximately equivalent - I just didn't want to wire up all the dependencies.
 */
public interface RecordWriter {

  /**
   * Get the name of the file we're currently writing to.
   */
  String getCurrentFilename();
  /**
   * Append a record to the current file. This method must be threadsafe.
   */
  void write(AirbyteRecordMessage record);

  /**
   * Flushes the current file and creates a new file. The new file must have a unique filename,
   * for example using a UUID. This method must be threadsafe.
   */
  void rotateFile();
}
