/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.record_buffer;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

public interface RecordBufferStorage {

  OutputStream getOutputStream() throws IOException;

  String getFilename() throws IOException;

  File getFile() throws IOException;

  InputStream convertToInputStream() throws IOException;

  void close() throws IOException;

  void deleteFile() throws IOException;

  Long getMaxTotalBufferSizeInBytes();

  Long getMaxPerStreamBufferSizeInBytes();

  int getMaxConcurrentStreamsInBuffer();

}
