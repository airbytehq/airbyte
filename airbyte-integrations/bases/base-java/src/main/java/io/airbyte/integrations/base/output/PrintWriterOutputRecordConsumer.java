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
import javax.annotation.concurrent.NotThreadSafe;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Implementation of the {@link OutputRecordConsumer} interface that uses a {@link PrintWriter} to
 * publish serialized {@link AirbyteMessage} objects. This implementation is not thread safe and it
 * is recommended to create a consumer per thread if used in a multithreaded way.
 */
@NotThreadSafe
public class PrintWriterOutputRecordConsumer implements OutputRecordConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(PrintWriterOutputRecordConsumer.class);

  private final PrintWriter writer;

  public PrintWriterOutputRecordConsumer() {
    LOGGER.info("Using PrintWriter for output record collection.");
    writer = new PrintWriter(
        new BufferedWriter(
            new OutputStreamWriter(
                new FileOutputStream(FileDescriptor.out),
                StandardCharsets.UTF_8)));
  }

  @Override
  public void close() throws Exception {
    LOGGER.info("Flushing and closing PrintWriter...");
    writer.flush();
    writer.close();
  }

  @Override
  public void accept(final AirbyteMessage airbyteMessage) {
    final String json = Jsons.serialize(airbyteMessage);
    LOGGER.info("Accepted message '{}' for output.", json);
    writer.println(json);
  }

}
