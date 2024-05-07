/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.integrations.BaseConnector;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.util.List;
import java.util.Map;

public class TestingSources extends BaseConnector implements Source {
  private final Map<TestingSourceType, Source> sourceMap;

  public enum TestingSourceType {
    CONTINUOUS_FEED,
    EXCEPTION_AFTER_N,
    INFINITE_FEED,

    BENCHMARK
  }

  public TestingSources() {
    this(ImmutableMap.<TestingSourceType, Source>builder()
        .put(TestingSourceType.CONTINUOUS_FEED, new ContinuousFeedSource())
        .put(TestingSourceType.EXCEPTION_AFTER_N, new LegacyExceptionAfterNSource())
        .put(TestingSourceType.INFINITE_FEED, new LegacyInfiniteFeedSource())
        .put(TestingSourceType.BENCHMARK, new SpeedBenchmarkSource())
        .build());
  }

  public ConnectorSpecification spec() throws Exception {
    if (isCloudDeployment()) {
      ConnectorSpecification originalSpec = Jsons.clone(super.spec());
      final ArrayNode allOptions = ((ArrayNode) originalSpec.getConnectionSpecification().get("oneOf"));
      for (final JsonNode mode : allOptions) {
        if (mode.get("properties").get("type").get("const").asText().equals("CONTINUOUS_FEED")) {
          ((ObjectNode) originalSpec.getConnectionSpecification()).set("oneOf", Jsons.arrayNode().add(mode));
          return originalSpec;
        }
      }
      throw new RuntimeException ("in cloud mode, but couldn't find the CONTINUOUS_FEED option");
    } else {
      return super.spec();
    }
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
