/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.output;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.io.BufferedWriter;
import java.io.FileDescriptor;
import java.io.FileOutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;

/**
 * Implementation of the {@link OutputRecordConsumer} interface that uses a {@link PrintWriter} to
 * publish serialized {@link AirbyteMessage} objects. This implementation is not thread safe and it
 * is recommended to create a consumer per thread if used in a multithreaded way.
 */
public class PrintWriterOutputRecordConsumer implements OutputRecordConsumer {

  private final PrintWriter writer;

  public PrintWriterOutputRecordConsumer() {
    writer = new PrintWriter(
        new BufferedWriter(
            new OutputStreamWriter(
                new FileOutputStream(FileDescriptor.out),
                StandardCharsets.UTF_8)));
  }

  @Override
  public void close() throws Exception {
    writer.flush();
    writer.close();
  }

  @Override
  public void accept(final AirbyteMessage airbyteMessage) {
    writer.println(Jsons.serialize(airbyteMessage));
  }

}
