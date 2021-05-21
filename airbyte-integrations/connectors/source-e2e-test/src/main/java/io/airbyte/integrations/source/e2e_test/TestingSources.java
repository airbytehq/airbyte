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

package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This source is designed to be a switch statement for our suite of highly-specific test sourcess.
 */
public class TestingSources extends BaseConnector implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(TestingSources.class);

  private final Map<TestDestinationType, Source> sourceMap;

  public enum TestDestinationType {
    INFINITE_FEED,
    EXCEPTION_AFTER_N
  }

  public TestingSources() {
    this(ImmutableMap.<TestDestinationType, Source>builder()
        .put(TestDestinationType.INFINITE_FEED, new InfiniteFeedSource())
        .put(TestDestinationType.EXCEPTION_AFTER_N, new ExceptionAfterNSource())
        .build());
  }

  public TestingSources(Map<TestDestinationType, Source> sourceMap) {
    this.sourceMap = sourceMap;
  }

  private Source selectSource(JsonNode config) {
    return sourceMap.get(TestDestinationType.valueOf(config.get("type").asText()));
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) throws Exception {
    return selectSource(config).check(config);
  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) throws Exception {
    return selectSource(config).discover(config);
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode config,
                                                    final ConfiguredAirbyteCatalog catalog,
                                                    final JsonNode state)
      throws Exception {
    return selectSource(config).read(config, catalog, state);
  }

  public static void main(String[] args) throws Exception {
    final Source source = new TestingSources();
    LOGGER.info("starting source: {}", TestingSources.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", TestingSources.class);
  }

}
