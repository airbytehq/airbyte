/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import io.airbyte.protocol.models.AirbyteMessage;
import java.io.IOException;

public interface AirbyteMessageBufferedWriter {

  void write(AirbyteMessage message) throws IOException;

  void flush() throws IOException;

  void close() throws IOException;

}
