/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.throughput_throttled;

import static java.lang.Thread.sleep;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ThroughputThrottledDestination extends BaseConnector implements Destination {

  private static final AtomicLong RECORD_COUNTER = new AtomicLong();
  private static final Logger LOGGER = LoggerFactory.getLogger(ThroughputThrottledDestination.class);

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config, final ConfiguredAirbyteCatalog catalog) throws Exception {
    return new ThrottledConsumer(config.get("millis_per_record").asLong());
  }

  public static class ThrottledConsumer implements AirbyteMessageConsumer {

    private final long millisPerRecord;

    public ThrottledConsumer(long millisPerRecord) {
      this.millisPerRecord = millisPerRecord;
    }

    @Override
    public void start() throws Exception {

    }

    @Override
    public void accept(final AirbyteMessage message) throws Exception {
      final long value = message.getRecord().getData().get("column1").asLong();
      if(RECORD_COUNTER.get() != 0 && value - 1 != RECORD_COUNTER.get()) {
        throw new IllegalStateException(String.format("Previous value was: %s, but next value was: %s", RECORD_COUNTER.get(), value));
      }
      RECORD_COUNTER.set(value);

      LOGGER.info("received record: {}", value);
      sleep(millisPerRecord);
      LOGGER.info("completed sleep");
    }

    @Override
    public void close() throws Exception {

    }
  }


  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new ThroughputThrottledDestination()).run(args);
  }
}
