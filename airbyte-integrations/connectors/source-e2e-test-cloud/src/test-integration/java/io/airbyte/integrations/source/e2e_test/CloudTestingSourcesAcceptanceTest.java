/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.source.e2e_test.ContinuousFeedConfig.MockCatalogType;
import io.airbyte.integrations.source.e2e_test.TestingSources.TestingSourceType;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

/**
 * This acceptance test is mostly the same as {@code ContinuousFeedSourceAcceptanceTest}. The only
 * difference is the image name. TODO: find a way to share classes from integrationTest.
 */
public class CloudTestingSourcesAcceptanceTest extends SourceAcceptanceTest {

  private static final int MAX_MESSAGES = ThreadLocalRandom.current().nextInt(10, 20);
  private static final JsonSchemaValidator JSON_VALIDATOR = new JsonSchemaValidator();
  private static final String STREAM_1 = "stream1";
  private static final JsonNode SCHEMA_1 = Jsons.deserialize("""
                                                             {
                                                               "type": "object",
                                                               "properties": {
                                                                 "field1": { "type": "integer" }
                                                               }
                                                             }
                                                             """);
  private static final String STREAM_2 = "stream2";
  private static final JsonNode SCHEMA_2 = Jsons.deserialize("""
                                                             {
                                                               "type": "object",
                                                               "properties": {
                                                                 "column1": { "type": "string" },
                                                                 "column2": {
                                                                   "type": "object",
                                                                   "properties": {
                                                                     "field1": { "type": "array", "items": { "type": "boolean" } },
                                                                     "field2": { "type": "integer" }
                                                                   }
                                                                 }
                                                               }
                                                             }
                                                             """);

  private JsonNode config;

  @Override
  protected String getImageName() {
    return "airbyte/source-e2e-test-cloud:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return this.config;
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) {

    final JsonNode mockCatalog = Jsons.jsonNode(ImmutableMap.builder()
        .put("type", MockCatalogType.MULTI_STREAM)
        .put("stream_schemas", String.format("{ \"%s\": %s, \"%s\": %s }",
            STREAM_1,
            Jsons.serialize(SCHEMA_1),
            STREAM_2,
            Jsons.serialize(SCHEMA_2)))
        .build());
    this.config = Jsons.jsonNode(ImmutableMap.builder()
        .put("type", TestingSourceType.CONTINUOUS_FEED)
        .put("seed", 1024)
        .put("message_interval_ms", 0)
        .put("max_messages", MAX_MESSAGES)
        .put("mock_catalog", mockCatalog)
        .build());
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    // do nothing
  }

  @Override
  protected ConnectorSpecification getSpec() throws IOException {
    return Jsons.deserialize(MoreResources.readResource("expected_spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() throws JsonValidationException {
    final ContinuousFeedConfig feedConfig = new ContinuousFeedConfig(this.config);
    return CatalogHelpers.toDefaultConfiguredCatalog(feedConfig.getMockCatalog());
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

  @Override
  protected void assertFullRefreshMessages(final List<AirbyteMessage> allMessages) {
    final List<AirbyteRecordMessage> recordMessages = filterRecords(allMessages);

    int index = 0;
    // the first N messages are from stream 1
    while (index < MAX_MESSAGES) {
      final AirbyteRecordMessage message = recordMessages.get(index);
      assertEquals(STREAM_1, message.getStream());
      assertTrue(JSON_VALIDATOR.validate(SCHEMA_1, message.getData()).isEmpty());
      ++index;
    }
    // the second N messages are from stream 2
    while (index < MAX_MESSAGES * 2) {
      final AirbyteRecordMessage message = recordMessages.get(index);
      assertEquals(STREAM_2, message.getStream());
      assertTrue(JSON_VALIDATOR.validate(SCHEMA_2, message.getData()).isEmpty());
      ++index;
    }
  }

}
