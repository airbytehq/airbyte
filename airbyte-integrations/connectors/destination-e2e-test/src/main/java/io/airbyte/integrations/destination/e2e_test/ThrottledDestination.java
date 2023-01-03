/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.e2e_test;

import static java.lang.Thread.sleep;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This destination logs each record it receives. It sleeps for millis_per_record between accepting
 * each record. Useful for simulating backpressure / slow destination writes.
 */
public class ThrottledDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(ThrottledDestination.class);

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    return new ThrottledConsumer(config.get("millis_per_record").asLong(), outputRecordCollector);
  }

  public static class ThrottledConsumer implements AirbyteMessageConsumer {

    private final Consumer<AirbyteMessage> outputRecordCollector;
    private final long millisPerRecord;

    public ThrottledConsumer(final long millisPerRecord, final Consumer<AirbyteMessage> outputRecordCollector) {
      this.millisPerRecord = millisPerRecord;
      this.outputRecordCollector = outputRecordCollector;
      LOGGER.info("Will sleep {} millis before processing every record", millisPerRecord);
    }

    @Override
    public void start() {}

    @Override
    public void accept(final AirbyteMessage message) throws Exception {
      sleep(millisPerRecord);

      if (message.getType() == Type.STATE) {
        LOGGER.info("Emitting state: {}", message);
        outputRecordCollector.accept(message);
      }
    }

    @Override
    public void close() {}

  }

}
