/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.JsonNodeType;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

public class MoreOAuthParametersTest {

  @Test
  void testFlattenConfig() {
    final JsonNode nestedConfig = Jsons.jsonNode(Map.of(
        "field", "value1",
        "top-level", Map.of(
            "nested_field", "value2")));
    final JsonNode expectedConfig = Jsons.jsonNode(Map.of(
        "field", "value1",
        "nested_field", "value2"));
    final JsonNode actualConfig = MoreOAuthParameters.flattenOAuthConfig(nestedConfig);
    assertEquals(expectedConfig, actualConfig);
  }

  @Test
  void testFailureFlattenConfig() {
    final JsonNode nestedConfig = Jsons.jsonNode(Map.of(
        "field", "value1",
        "top-level", Map.of(
            "nested_field", "value2",
            "field", "value3")));
    assertThrows(IllegalStateException.class, () -> MoreOAuthParameters.flattenOAuthConfig(nestedConfig));
  }

  private void maskAllValues(final ObjectNode node) {
    for (final String key : Jsons.keys(node)) {
      if (node.get(key).getNodeType() == JsonNodeType.OBJECT) {
        maskAllValues((ObjectNode) node.get(key));
      } else {
        node.set(key, MoreOAuthParameters.getSecretMask());
      }
    }
  }

  @Test
  void testInjectUnnestedNode_Masked() {
    final ObjectNode oauthParams = (ObjectNode) Jsons.jsonNode(generateOAuthParameters());
    final ObjectNode maskedOauthParams = Jsons.clone(oauthParams);
    maskAllValues(maskedOauthParams);
    final ObjectNode actual = generateJsonConfig();
    final ObjectNode expected = Jsons.clone(actual);
    expected.setAll(maskedOauthParams);

    MoreOAuthParameters.mergeJsons(actual, oauthParams, MoreOAuthParameters.getSecretMask());
    assertEquals(expected, actual);
  }

  @Test
  void testInjectUnnestedNode_Unmasked() {
    final ObjectNode oauthParams = (ObjectNode) Jsons.jsonNode(generateOAuthParameters());

    final ObjectNode actual = generateJsonConfig();
    final ObjectNode expected = Jsons.clone(actual);
    expected.setAll(oauthParams);

    MoreOAuthParameters.mergeJsons(actual, oauthParams);

    assertEquals(expected, actual);
  }

  @Test
  void testInjectNewNestedNode_Masked() {
    final ObjectNode oauthParams = (ObjectNode) Jsons.jsonNode(generateOAuthParameters());
    final ObjectNode maskedOauthParams = Jsons.clone(oauthParams);
    maskAllValues(maskedOauthParams);
    final ObjectNode nestedConfig = (ObjectNode) Jsons.jsonNode(ImmutableMap.builder()
        .put("oauth_credentials", oauthParams)
        .build());

    // nested node does not exist in actual object
    final ObjectNode actual = generateJsonConfig();
    final ObjectNode expected = Jsons.clone(actual);
    expected.putObject("oauth_credentials").setAll(maskedOauthParams);

    MoreOAuthParameters.mergeJsons(actual, nestedConfig, MoreOAuthParameters.getSecretMask());
    assertEquals(expected, actual);
  }

  @Test
  @DisplayName("A nested config should be inserted with the same nesting structure")
  void testInjectNewNestedNode_Unmasked() {
    final ObjectNode oauthParams = (ObjectNode) Jsons.jsonNode(generateOAuthParameters());
    final ObjectNode nestedConfig = (ObjectNode) Jsons.jsonNode(ImmutableMap.builder()
        .put("oauth_credentials", oauthParams)
        .build());

    // nested node does not exist in actual object
    final ObjectNode actual = generateJsonConfig();
    final ObjectNode expected = Jsons.clone(actual);
    expected.putObject("oauth_credentials").setAll(oauthParams);

    MoreOAuthParameters.mergeJsons(actual, nestedConfig);

    assertEquals(expected, actual);
  }

  @Test
  @DisplayName("A nested node which partially exists in the main config should be merged into the main config, not overwrite the whole nested object")
  void testInjectedPartiallyExistingNestedNode_Unmasked() {
    final ObjectNode oauthParams = (ObjectNode) Jsons.jsonNode(generateOAuthParameters());
    final ObjectNode nestedConfig = (ObjectNode) Jsons.jsonNode(ImmutableMap.builder()
        .put("oauth_credentials", oauthParams)
        .build());

    // nested node partially exists in actual object
    final ObjectNode actual = generateJsonConfig();
    actual.putObject("oauth_credentials").put("irrelevant_field", "_");
    final ObjectNode expected = Jsons.clone(actual);
    ((ObjectNode) expected.get("oauth_credentials")).setAll(oauthParams);

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
