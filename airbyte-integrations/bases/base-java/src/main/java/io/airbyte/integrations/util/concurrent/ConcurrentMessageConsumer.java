/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.util.concurrent;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.io.BufferedWriter;
import java.io.FileDescriptor;
import java.io.FileOutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Consumer;

/**
 * Custom {@link Consumer} used to serialize messages to standard out.
 * <p>
 * Using {@code System.out.println} in a multi-threaded environment comes with a large performance
 * penalty, as the {@code println} method is synchronized. Instead, use a {@link BufferedWriter} to
 * improve performance in a multi-threaded environment.
 * </p>
 */
public class ConcurrentMessageConsumer implements Consumer<AirbyteMessage>, AutoCloseable {

  private final AtomicLong flushCounter;

  private final PrintWriter out;

  public ConcurrentMessageConsumer() {
    flushCounter = new AtomicLong(0);
    out = new PrintWriter(
        new BufferedWriter(
            new OutputStreamWriter(
                new FileOutputStream(FileDescriptor.out), StandardCharsets.US_ASCII)));
  }

  @Override
  public void accept(final AirbyteMessage airbyteMessage) {
    out.write(Jsons.serialize(airbyteMessage));
    out.write(System.lineSeparator());

    if (flushCounter.incrementAndGet() % 1000 == 0) {
      out.flush();
    }
  }

  @Override
  public void close() throws Exception {
    out.flush();
    out.close();
  }

}
