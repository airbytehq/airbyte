/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.record_buffer;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

/**
 * This interface abstract the actual object that is used to store incoming data being buffered. It
 * could be a file, in-memory or some other objects.
 *
 * However, in order to be used as part of the {@link SerializableBuffer}, this
 * {@link BufferStorage} should implement some methods used to determine how to write into and read
 * from the storage once we are done buffering
 *
 * Some easy methods for manipulating the storage viewed as a file or InputStream are therefore
 * required.
 *
 * Depending on the implementation of the storage medium, it would also determine what storage
 * limits are possible.
 */
public interface BufferStorage {

  /**
   * Builds a new outputStream on which to write the data for storage.
   */
  OutputStream getOutputStream() throws IOException;

  String getFilename() throws IOException;

  File getFile() throws IOException;

  /**
   * Once buffering has reached some limits, the storage stream should be turned into an InputStream.
   * This method should assume we are not going to write to buffer anymore, and it is safe to convert
   * to some other format to be read from now.
   */
  InputStream convertToInputStream() throws IOException;

  void close() throws IOException;

  /**
   * Cleans-up any file that was produced in the process of buffering (if any were produced)
   */
  void deleteFile() throws IOException;

  /*
   * Depending on the implementation of the storage, methods below defined reasonable thresholds
   * associated with using this kind of buffer storage.
   *
   * These could also be dynamically configured/tuned at runtime if needed (from user input for
   * example?)
   */

  /**
   * @return How much storage should be used overall by all buffers
   */
  long getMaxTotalBufferSizeInBytes();

  /**
   * @return How much storage should be used for a particular stream at a time before flushing it
   */
  long getMaxPerStreamBufferSizeInBytes();

  /**
   * @return How many concurrent buffers can be handled at once in parallel
   */
  int getMaxConcurrentStreamsInBuffer();

}
