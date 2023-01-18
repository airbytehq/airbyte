/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteMessage;
import java.io.BufferedWriter;
import java.io.IOException;

public class DefaultAirbyteMessageBufferedWriter implements AirbyteMessageBufferedWriter {

  protected final BufferedWriter writer;

  public DefaultAirbyteMessageBufferedWriter(final BufferedWriter writer) {
    this.writer = writer;
  }

  @Override
  public void write(final AirbyteMessage message) throws IOException {
    writer.write(Jsons.serialize(message));
    writer.newLine();
  }

  @Override
  public void flush() throws IOException {
    writer.flush();
  }

  @Override
  public void close() throws IOException {
    writer.close();
  }

}
