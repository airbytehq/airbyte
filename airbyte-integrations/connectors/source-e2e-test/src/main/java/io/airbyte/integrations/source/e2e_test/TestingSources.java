/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
