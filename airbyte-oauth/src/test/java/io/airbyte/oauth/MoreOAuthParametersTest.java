/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class MoreOAuthParametersTest {

  private static final String FIELD = "field";
  private static final String OAUTH_CREDS = "oauth_credentials";

  @Test
  void testFlattenConfig() {
    final JsonNode nestedConfig = Jsons.jsonNode(Map.of(
        FIELD, "value1",
        "top-level", Map.of(
            "nested_field", "value2")));
    final JsonNode expectedConfig = Jsons.jsonNode(Map.of(
        FIELD, "value1",
        "nested_field", "value2"));
    final JsonNode actualConfig = MoreOAuthParameters.flattenOAuthConfig(nestedConfig);
    assertEquals(expectedConfig, actualConfig);
  }

  @Test
  void testFailureFlattenConfig() {
    final JsonNode nestedConfig = Jsons.jsonNode(Map.of(
        FIELD, "value1",
        "top-level", Map.of(
            "nested_field", "value2",
            FIELD, "value3")));
    assertThrows(IllegalStateException.class, () -> MoreOAuthParameters.flattenOAuthConfig(nestedConfig));
  }

  @Test
  void testInjectUnnestedNode() {
    final ObjectNode oauthParams = (ObjectNode) Jsons.jsonNode(generateOAuthParameters());

    final ObjectNode actual = generateJsonConfig();
    final ObjectNode expected = Jsons.clone(actual);
    expected.setAll(oauthParams);

    MoreOAuthParameters.mergeJsons(actual, oauthParams);

    assertEquals(expected, actual);
  }

  @Test
  @DisplayName("A nested config should be inserted with the same nesting structure")
  void testInjectNewNestedNode() {
    final ObjectNode oauthParams = (ObjectNode) Jsons.jsonNode(generateOAuthParameters());
    final ObjectNode nestedConfig = (ObjectNode) Jsons.jsonNode(ImmutableMap.builder()
        .put(OAUTH_CREDS, oauthParams)
        .build());

    // nested node does not exist in actual object
    final ObjectNode actual = generateJsonConfig();
    final ObjectNode expected = Jsons.clone(actual);
    expected.putObject(OAUTH_CREDS).setAll(oauthParams);

    MoreOAuthParameters.mergeJsons(actual, nestedConfig);

    assertEquals(expected, actual);
  }

  @Test
  @DisplayName("A nested node which partially exists in the main config should be merged into the main config, not overwrite the whole nested object")
  void testInjectedPartiallyExistingNestedNode() {
    final ObjectNode oauthParams = (ObjectNode) Jsons.jsonNode(generateOAuthParameters());
    final ObjectNode nestedConfig = (ObjectNode) Jsons.jsonNode(ImmutableMap.builder()
        .put(OAUTH_CREDS, oauthParams)
        .build());

    // nested node partially exists in actual object
    final ObjectNode actual = generateJsonConfig();
    actual.putObject(OAUTH_CREDS).put("irrelevant_field", "_");
    final ObjectNode expected = Jsons.clone(actual);
    ((ObjectNode) expected.get(OAUTH_CREDS)).setAll(oauthParams);

    MoreOAuthParameters.mergeJsons(actual, nestedConfig);

    assertEquals(expected, actual);
  }

  private ObjectNode generateJsonConfig() {
    return (ObjectNode) Jsons.jsonNode(ImmutableMap.builder()
        .put("apiSecret", "123")
        .put("client", "testing")
        .build());
  }

  private Map<String, String> generateOAuthParameters() {
    return ImmutableMap.<String, String>builder()
        .put("api_secret", "mysecret")
        .put("api_client", UUID.randomUUID().toString())
        .build();
  }

}
