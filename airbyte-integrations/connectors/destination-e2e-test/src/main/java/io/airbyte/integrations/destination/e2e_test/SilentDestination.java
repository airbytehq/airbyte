/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This destination silently receives records.
 */
public class SilentDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(LoggingDestination.class);
  private static final AtomicInteger counter = new AtomicInteger();

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    return new SilentDestination.RecordConsumer(outputRecordCollector);
  }

  public static class RecordConsumer implements AirbyteMessageConsumer {

    private final Consumer<AirbyteMessage> outputRecordCollector;

    public RecordConsumer(Consumer<AirbyteMessage> outputRecordCollector) {
      this.outputRecordCollector = outputRecordCollector;
    }

    @Override
    public void start() {}

    @Override
    public void accept(final AirbyteMessage message) {
      if (message.getType() == Type.STATE) {
        LOGGER.info("emitting state: {}", message);
        outputRecordCollector.accept(message);
      }

      var curr = counter.incrementAndGet();
      if (curr % 1000 == 0) {
        LOGGER.info("Record count: {}", curr);
      }
    }

    @Override
    public void close() {}

  }

}
