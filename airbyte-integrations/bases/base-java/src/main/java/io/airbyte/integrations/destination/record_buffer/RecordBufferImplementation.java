/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.record_buffer;

import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;

public interface RecordBufferImplementation extends AutoCloseable {

  Long accept(AirbyteRecordMessage recordMessage) throws Exception;

  void flush() throws Exception;

  Long getCount();

  String getFilename() throws IOException;

  File getFile() throws IOException;

  InputStream getInputStream();

  Long getMaxTotalBufferSizeInBytes();

  Long getMaxPerStreamBufferSizeInBytes();

  int getMaxConcurrentStreamsInBuffer();

}
