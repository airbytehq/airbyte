/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.Map;

public class TestingSources extends BaseConnector implements Source {

  private final Map<TestingSourceType, Source> sourceMap;

  public enum TestingSourceType {
    CONTINUOUS_FEED,
    // the following are legacy types
    EXCEPTION_AFTER_N,
    INFINITE_FEED
  }

  public TestingSources() {
    this(ImmutableMap.<TestingSourceType, Source>builder()
        .put(TestingSourceType.CONTINUOUS_FEED, new ContinuousFeedSource())
        .put(TestingSourceType.EXCEPTION_AFTER_N, new LegacyExceptionAfterNSource())
        .put(TestingSourceType.INFINITE_FEED, new LegacyInfiniteFeedSource())
        .build());
  }

  public TestingSources(final Map<TestingSourceType, Source> sourceMap) {
    this.sourceMap = sourceMap;
  }

  private Source selectSource(final JsonNode config) {
    return sourceMap.get(TestingSourceType.valueOf(config.get("type").asText()));
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

  public static void main(final String[] args) throws Exception {
    final Source source = new TestingSources();
    new IntegrationRunner(source).run(args);
  }

}
