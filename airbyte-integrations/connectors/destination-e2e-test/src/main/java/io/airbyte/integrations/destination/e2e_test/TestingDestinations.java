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

package io.airbyte.integrations.destination.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.Map;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TestingDestinations extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(TestingDestinations.class);

  private final Map<TestDestinationType, Destination> destinationMap;

  public enum TestDestinationType {
    LOGGING,
    THROTTLED
  }

  public TestingDestinations() {
    this(ImmutableMap.<TestDestinationType, Destination>builder()
        .put(TestDestinationType.LOGGING, new LoggingDestination())
        .put(TestDestinationType.THROTTLED, new ThrottledDestination())
        .build());
  }

  public TestingDestinations(Map<TestDestinationType, Destination> destinationMap) {
    this.destinationMap = destinationMap;
  }

  private Destination selectDestination(JsonNode config) {
    return destinationMap.get(TestDestinationType.valueOf(config.get("type").asText()));
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception {
    return selectDestination(config).getConsumer(config, catalog, outputRecordCollector);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) throws Exception {
    return selectDestination(config).check(config);
  }

  public static void main(String[] args) throws Exception {
    final Destination destination = new TestingDestinations();
    LOGGER.info("starting destination: {}", TestingDestinations.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", TestingDestinations.class);
  }

}
