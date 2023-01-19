/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import java.io.BufferedWriter;

public class DefaultAirbyteMessageBufferedWriterFactory implements AirbyteMessageBufferedWriterFactory {

  @Override
  public AirbyteMessageBufferedWriter createWriter(BufferedWriter writer) {
    return new DefaultAirbyteMessageBufferedWriter(writer);
  }

}
